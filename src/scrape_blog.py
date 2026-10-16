#!/usr/bin/env python3
"""Copy the latest Learning Center articles from the live site.

Reads the first pages of https://primetaxcpa.com/blog, saves each article's
text exactly as published (plus its date, categories, summary and photos) to
src/content/blog.json, and downloads the photos into assets/img/blog/.

Run:  python3 src/scrape_blog.py [pages]      (default: 2 listing pages)
Then: python3 src/build.py
"""
import html
import json
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = "https://primetaxcpa.com"
IMG_DIR = os.path.join(ROOT, "assets", "img", "blog")
OUT = os.path.join(ROOT, "src", "content", "blog.json")
UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="ignore")


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def download(url, name):
    """Save an image once; return its site-relative path."""
    ext = os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"
    rel = f"assets/img/blog/{name}{ext}"
    dest = os.path.join(ROOT, rel)
    if not os.path.exists(dest):
        with open(dest, "wb") as f:
            f.write(fetch(url, binary=True))
    return rel


# ---------------------------------------------------------------------------
# Listing pages: one card per article
# ---------------------------------------------------------------------------
CARD = re.compile(r'<div class="flex flex-col rounded-lg shadow-lg overflow-hidden">(.*?)</time>', re.S)


def read_listing(page):
    url = f"{LIVE}/blog" + (f"?page={page}" if page > 1 else "")
    cards = []
    for m in CARD.finditer(fetch(url)):
        c = m.group(1)
        link = re.search(r'href="https://primetaxcpa\.com/blog/([a-z0-9-]+)"', c)
        if not link:
            continue
        thumb = re.search(r'<img[^>]*src="([^"]+)"', c)
        cats = [text(b) for b in re.findall(r"<button[^>]*>(.*?)</button>", c, re.S)]
        title = re.search(r'<p class="text-xl[^"]*">(.*?)</p>', c, re.S)
        excerpt = re.search(r'<p class="mt-3[^"]*">(.*?)</p>', c, re.S)
        when = re.search(r'<time datetime="([^"]+)">\s*([^<]*)', c + "</time>")
        cards.append({
            "slug": link.group(1),
            "thumb_src": thumb.group(1) if thumb else None,
            "categories": cats,
            "title": text(title.group(1)) if title else "",
            "excerpt": text(excerpt.group(1)) if excerpt else "",
            "datetime_utc": when.group(1) if when else "",
            "date_short": when.group(2).strip() if when else "",
        })
    return cards


# ---------------------------------------------------------------------------
# Article pages: ordered blocks of rich text, "Let's Talk!" boxes and videos
# ---------------------------------------------------------------------------
KEEP = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "b", "em", "i", "a", "img", "br",
        "blockquote", "table", "thead", "tbody", "tr", "th", "td", "sup", "sub"}


class Clean(HTMLParser):
    """Keep the article's own markup, drop classes, styles and scripts."""

    def __init__(self, img_cb, link_cb):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.img_cb, self.link_cb = [], 0, img_cb, link_cb

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "iframe", "svg"):
            self.skip += 1
            return
        if self.skip or tag not in KEEP:
            return
        if tag == "img":
            src = a.get("src")
            if src:
                self.out.append(f'<img src="@/{self.img_cb(src)}" alt="{html.escape(a.get("alt") or "", quote=True)}" loading="lazy">')
            return
        if tag == "a":
            self.out.append(f'<a href="{html.escape(self.link_cb(a.get("href", "")), quote=True)}">')
            return
        if tag == "br":
            self.out.append("<br>")
            return
        self.out.append(f"<{'strong' if tag == 'b' else 'em' if tag == 'i' else tag}>")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "iframe", "svg"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag not in KEEP or tag in ("img", "br"):
            return
        self.out.append(f"</{'strong' if tag == 'b' else 'em' if tag == 'i' else tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))


PROSE = re.compile(r'<div class="my-6 ProseMirror prose[^"]*">\s*<p class="mt-8[^"]*">(.*?)</p>\s*</div>', re.S)
CTA = re.compile(r'<div class="text-2xl text-gray-700 font-bold">\s*(.*?)\s*</div>\s*<div class="text-gray-700">\s*(.*?)\s*</div>\s*<a href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', re.S)
VIDEO = re.compile(r'<iframe[^>]*?title="([^"]*)"[^>]*?src="([^"]+)"|<iframe[^>]*?src="([^"]+)"[^>]*?title="([^"]*)"', re.S)


def local_link(href):
    """Point links to the live site at the matching page of this site."""
    m = re.match(r"https?://(?:www\.)?primetaxcpa\.com(/[^?#]*)?", href or "")
    if not m:
        return href
    path = (m.group(1) or "/").strip("/")
    candidate = (path or "index") + ".html"
    return "@/" + candidate if os.path.exists(os.path.join(ROOT, candidate)) else href


def read_article(card):
    slug = card["slug"]
    raw = fetch(f"{LIVE}/blog/{slug}")
    head = raw[:raw.find("<body")]
    meta = re.search(r'<meta name="description" content="([^"]*)"', head)
    og = re.search(r'property="og:image" content="([^"]+)"', head)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
    when = re.search(r'<time datetime="([^"]+)">([^<]*)</time>', raw[:h1.start()] if h1 else raw)
    start = h1.end() if h1 else 0
    end = raw.find("Share this article", start)
    body = raw[start:end if end > 0 else None]

    counter = {"n": 0}

    def img_cb(src):
        counter["n"] += 1
        return download(src, f"{slug}-{counter['n']}")

    blocks = []
    found = []
    for m in PROSE.finditer(body):
        found.append((m.start(), "prose", m))
    for m in CTA.finditer(body):
        found.append((m.start(), "cta", m))
    for m in VIDEO.finditer(body):
        found.append((m.start(), "video", m))
    for _, kind, m in sorted(found, key=lambda x: x[0]):
        if kind == "prose":
            c = Clean(img_cb, local_link)
            c.feed(re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S))
            frag = re.sub(r"<p>\s*</p>", "", "".join(c.out)).strip()
            if frag:
                blocks.append({"type": "prose", "html": frag})
        elif kind == "cta":
            blocks.append({"type": "cta", "title": text(m.group(1)), "text": text(m.group(2)),
                           "href": html.unescape(m.group(3)), "label": text(m.group(4))})
        else:
            title = m.group(1) or m.group(4) or ""
            src = m.group(2) or m.group(3)
            blocks.append({"type": "video", "title": html.unescape(title), "src": src})

    hero = download(og.group(1), slug) if og else None
    thumb = download(card["thumb_src"], f"{slug}-thumb") if card.get("thumb_src") else hero
    return {
        **{k: v for k, v in card.items() if k != "thumb_src"},
        "title": text(h1.group(1)) if h1 else card["title"],
        "date_long": when.group(2).strip() if when else "",
        "description": html.unescape(meta.group(1)) if meta else card["excerpt"],
        "hero": hero,
        "hero_src": og.group(1) if og else None,
        "thumb": thumb,
        "blocks": blocks,
    }


def main():
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    os.makedirs(IMG_DIR, exist_ok=True)
    seen, cards = set(), []
    for page in range(1, pages + 1):
        for c in read_listing(page):
            if c["slug"] not in seen:
                seen.add(c["slug"])
                cards.append(c)
    articles = [read_article(c) for c in cards]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=1)
    print(f"Saved {len(articles)} articles to {os.path.relpath(OUT, ROOT)}")
    for a in articles:
        kinds = [b["type"] for b in a["blocks"]]
        print(f"  {a['datetime_utc'][:10]}  {a['slug']}  blocks={kinds}")


if __name__ == "__main__":
    main()
