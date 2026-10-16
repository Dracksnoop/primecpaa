#!/usr/bin/env python3
"""Static site generator for the Prime CPA redesign.

All copy is taken from the live site (primetaxcpa.com). Corrections applied
from the work checklist are marked with "# checklist:" comments.

Run:  python3 src/build.py      (writes the pages into the repository root)
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT

# ---------------------------------------------------------------------------
# Firm details. The firm name is pending client confirmation
# ("Prime CPA LLC" vs "Prime CPA & Advisors"); change it here only.
# ---------------------------------------------------------------------------
FIRM = "Prime CPA LLC"

# Home-page-only demo: when True, every link on the homepage that leaves the
# homepage is switched off (no href, so nothing opens and no address shows on
# hover). In-page links (#section) and Home Page links keep working.
# Set to False and rebuild to link all pages again.
DEMO_HOME_ONLY = False
LIVE = "https://primetaxcpa.com"
CDN = "https://cw3prd.s3.us-west-1.amazonaws.com/"
PHONE = "(678) 230-3179"
PHONE_HREF = "tel:+16782303179"
EMAIL = "taxhelp@primetaxcpa.com"
ADDRESS_1 = "2300 Lakeview Pkwy, Suite 700"
ADDRESS_2 = "Alpharetta, Georgia 30009"
CALENDLY = "https://calendly.com/kumar-at-prime"
BLOG = LIVE + "/blog"
MAP_EMBED = "https://www.google.com/maps?q=2300+Lakeview+Pkwy+Suite+700+Alpharetta+GA+30009&output=embed"
SOCIAL = {
    "x": "https://twitter.com/primetaxcpa",
    "facebook": "https://www.facebook.com/Prime-Accounting-Tax-Solutions-LLC-1112656572166450/",
    # checklist: should become the Google Business Profile link once provided
    "google": "https://www.google.com/search?q=prime+cpa",
    "taxbuzz": "https://www.taxbuzz.com/georgia/atlanta/prime-cpa-69c671bc80909",
    "countingworks": "https://www.countingworks.com/professionals/georgia/atlanta/prime-cpa",
}
FIRM_SUMMARY = (f"At {FIRM}, our focus is your success. We provide accounting help, tax consulting, "
                "and business advisory services in Alpharetta.")

# Local image -> original CDN file (used for absolute og:image URLs)
CDN_IMG = {
    "office-reception.webp": "9923396/conversions/Regus_Lakeview_2108_GA_Alpharetta_USA_Reception-webp.webp",
    "tax-form-estimated.webp": "9906527/conversions/Tax-form-estimated-payment-GettyImages-1365668953-2500-webp.webp",
    "office-exterior.webp": "9923411/conversions/Regus_Lakeview_2108_GA_Alpharetta_USA_Exterior-webp.webp",
    "firm-background.webp": "7880949/conversions/tax-planning-consultant-senior-home-GettyImages-1327589078-2500-webp.webp",
    "kumar.jpg": "3810382/responsive-images/kumar___media_library_original_350_350.jpeg",
    "page-why-best.jpg": "398750/responsive-images/Five_stars_blue_background_2500___media_library_original_1749_1166.jpg",
    "page-referrals.jpg": "137271/responsive-images/Quotes-GettyImages-1055880976-2500___media_library_original_1749_1311.jpg",
    "page-privacy.jpg": "396738/responsive-images/privacy-GettyImages-1169056417-2500___media_library_original_1749_1166.jpg",
    "svc-tax-strategy.webp": "7870648/conversions/tax-planning-blocks-GettyImages-1362521984-2500-webp.webp",
    "page-tax-prep.jpg": "3192125/responsive-images/Tax-form-1040-GettyImages-2043946640-2500___media_library_original_1749_1049.jpg",
    "page-accounting.webp": "3496/conversions/Accounting-GettyImages-1182777182-2500-webp.webp",
    "page-cfo.webp": "3461/conversions/aerial-view-desktop-green-GettyImages-871208414-2500-webp.webp",
    "page-payroll.jpg": "3177433/responsive-images/remote-deposit-payroll-check-GettyImages-1316932980-2500___media_library_original_1750_1167.jpg",
    "page-virtual-bookkeeping.webp": "3490/conversions/Graphs-on-computer-GettyImages-876975532-2500-webp.webp",
    "page-virtual-tax.webp": "8125/conversions/Smiling-woman-using-a-laptop-on-the-couch-GettyImages-1306509121-2400-webp.webp",
    "page-healthcare.webp": "10444/conversions/doctors-GettyImages-518063670-2000-webp.webp",
    "page-hnw.webp": "11149/conversions/Seniors-sailing-boat-GettyImages-984019868-2500-webp.webp",
    "page-law.webp": "10457/conversions/justice-law-GettyImages-638601140-2000-webp.webp",
    "page-realestate.webp": "11108/conversions/Real-Estate-GettyImages-1176556911-2500-webp.webp",
    "page-restaurants.jpg": "421022/responsive-images/Restaurant-staff-GettyImages-607047655-2500___media_library_original_1749_1166.jpg",
    "page-retail.jpg": "6105611/responsive-images/Grocery-Market-employees-GettyImages-1423350882-2500___media_library_original_1749_1168.jpg",
    "page-automotive.jpg": "418033/responsive-images/car-lot-GettyImages-480652712-2500___media_library_original_1749_1140.jpg",
    "page-misc.jpg": "7778446/responsive-images/leader-businesswoman-in-office-GettyImages-2219519829-2500___media_library_original_1749_1166.jpg",
}


def og_url(img):
    return CDN + CDN_IMG.get(img, CDN_IMG["office-exterior.webp"])


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
def svg(body, vb="0 0 24 24", fill="none", sw="1.6"):
    return (f'<svg viewBox="{vb}" fill="{fill}" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


I = {
    "arrow": svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "arrow-left": svg('<path d="M19 12H5M11 6l-6 6 6 6"/>'),
    "arrow-up": svg('<path d="M12 19V5M6 11l6-6 6 6"/>'),
    "chev": svg('<path d="M6 9l6 6 6-6"/>', sw="2"),
    "chev-r": svg('<path d="M9 6l6 6-6 6"/>'),
    "plus": svg('<path d="M12 5v14M5 12h14"/>'),
    "close": svg('<path d="M6 6l12 12M18 6L6 18"/>'),
    "phone": svg('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>'),
    "mail": svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'),
    "calendar": svg('<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M16 3v3M8 3v3M3 10h18"/>'),
    "dollar": svg('<circle cx="12" cy="12" r="9"/><path d="M15 9.2c-.6-.8-1.7-1.3-3-1.3-1.7 0-3 .9-3 2.1 0 2.9 6 1.4 6 4.2 0 1.2-1.3 2.1-3 2.1-1.3 0-2.5-.5-3.1-1.4M12 6.5v11"/>'),
    "pin": svg('<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    "star": svg('<path d="M12 2.8l2.8 5.8 6.3.9-4.6 4.4 1.1 6.3L12 17.2l-5.6 3 1.1-6.3L2.9 9.5l6.3-.9z"/>', fill="currentColor", sw="0"),
    "quote": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.2 5C5.6 6.6 3 10 3 14.2 3 17 4.7 19 7.1 19c2 0 3.5-1.5 3.5-3.4 0-1.9-1.4-3.3-3.2-3.3-.4 0-.8.1-1 .2.4-2.3 2.3-4.5 4.4-5.6L9.2 5zm10 0c-3.6 1.6-6.2 5-6.2 9.2 0 2.8 1.7 4.8 4.1 4.8 2 0 3.5-1.5 3.5-3.4 0-1.9-1.4-3.3-3.2-3.3-.4 0-.8.1-1 .2.4-2.3 2.3-4.5 4.4-5.6L19.2 5z"/></svg>',
    "x": svg('<path d="M4 4l16 16M20 4L4 20"/>', sw="1.8"),
    "facebook": svg('<path d="M14 8h2.5V4.5H14c-2.2 0-3.8 1.7-3.8 3.9V10H8v3.5h2.2V21h3.4v-7.5h2.6l.5-3.5h-3.1V8.6c0-.4.2-.6.4-.6z"/>', fill="currentColor", sw="0"),
    "google": svg('<path d="M20.6 12.2c0-.6-.1-1.2-.2-1.8H12v3.4h4.8a4.1 4.1 0 0 1-1.8 2.7v2.2h2.9c1.7-1.6 2.7-3.9 2.7-6.5z" fill="currentColor" stroke="none"/><path d="M12 21c2.4 0 4.5-.8 5.9-2.2L15 16.6c-.8.5-1.8.9-3 .9-2.3 0-4.3-1.6-5-3.7H4v2.3A9 9 0 0 0 12 21z" fill="currentColor" stroke="none" opacity=".8"/><path d="M7 13.8a5.4 5.4 0 0 1 0-3.5V8H4a9 9 0 0 0 0 8.1z" fill="currentColor" stroke="none" opacity=".6"/><path d="M12 6.6c1.3 0 2.5.5 3.4 1.3l2.6-2.6A9 9 0 0 0 4 8l3 2.3c.7-2.1 2.7-3.7 5-3.7z" fill="currentColor" stroke="none" opacity=".9"/>'),
    "taxbuzz": svg('<path d="M4 6h16M12 6v13"/><circle cx="18" cy="17" r="2.2"/>'),
    "cloud": svg('<path d="M7 18h10.5a4 4 0 0 0 .6-8A6 6 0 0 0 6.5 9 4.5 4.5 0 0 0 7 18z"/>'),
}



def e(text):
    return html.escape(text, quote=True)


def cur_attr(p, current):
    return ' aria-current="page"' if p == current else ""


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
ABOUT_LINKS = [
    ("Firm Background", "firm-background.html"),
    ("Meet the Team", "about-us/meet-the-team.html"),
    ("Why We're The Best", "about-us/why-were-the-best.html"),
    ("Referrals", "about-us/referrals.html"),
    ("FAQ", "about-us/faq.html"),
    ("Privacy Policy", "firm-background/privacy-policy.html"),
]
# checklist: "Tax Planning & Strategy" and "Tax Preparation" opened the same page;
# merged into one menu item until a separate page is approved.
SERVICE_LINKS = [
    ("Tax Preparation & Planning", "services/tax-preparation-planning.html"),
    ("Accounting & Bookkeeping", "services/accounting-bookkeeping.html"),
    ("Fractional CFO Services", "services/part-time-cfo.html"),
    ("Payroll", "services/payroll.html"),
    ("Virtual Bookkeeping", "services/virtual-bookkeeping.html"),
    ("Virtual Tax Preparation", "services/virtual-tax-preparation.html"),
]
INDUSTRY_LINKS = [
    ("Healthcare and Medical", "industries/healthcare-and-medical-accounting-services.html"),
    ("High Net Worth Individuals", "industries/high-net-worth-services.html"),
    ("Law Firms", "industries/law-firm-business-and-accounting-services.html"),
    ("Real Estate", "industries/accounting-and-tax-for-real-estate-agents.html"),
    ("Restaurants", "industries/restaurants.html"),
    ("Retail", "industries/retails.html"),
    ("Automotive Dealerships", "industries/automotive-dealerships.html"),
    ("Any Industry", "industries/miscellaneous-industries.html"),
]
NAV = [
    ("Home Page", "index.html", None),
    ("About Us", None, ABOUT_LINKS),
    ("Services", "services.html", SERVICE_LINKS),
    ("Industries", None, INDUSTRY_LINKS),
    ("Learning Center", BLOG, None),
]


def href(path):
    """Internal paths are written as @/path and resolved per page depth."""
    if path.startswith(("http", "mailto:", "tel:", "#")):
        return path
    return "@/" + path


def is_section_active(current, children):
    return any(current == p for _, p in children)


def render_nav(current):
    items = []
    for label, path, children in NAV:
        if children:
            active = " is-active" if is_section_active(current, children) else ""
            sub = "".join(
                f'<a href="{href(p)}"{cur_attr(p, current)}>{e(l)}{I["arrow"]}</a>'
                for l, p in children)
            link_href = href(path) if path else "#"
            tag = (f'<a class="nav__link" href="{link_href}" aria-haspopup="true">{e(label)}{I["chev"]}</a>'
                   if path else
                   f'<button class="nav__link" type="button" aria-haspopup="true">{e(label)}{I["chev"]}</button>')
            items.append(f'<li class="nav__item{active}">{tag}<div class="dropdown">{sub}</div></li>')
        else:
            cur = ' aria-current="page"' if path == current else ""
            ext = ' rel="noopener"' if path.startswith("http") else ""
            items.append(f'<li class="nav__item"><a class="nav__link" href="{href(path)}"{cur}{ext}>{e(label)}</a></li>')
    return '<ul class="nav">' + "".join(items) + "</ul>"


def render_mobile_menu():
    rows = []
    for label, path, children in NAV:
        if children:
            sub = "".join(f'<li><a href="{href(p)}">{e(l)}</a></li>' for l, p in children)
            rows.append(f'<li><details><summary>{e(label)}{I["plus"]}</summary><ul>{sub}</ul></details></li>')
        else:
            rows.append(f'<li><a class="mobile-menu__link" href="{href(path)}">{e(label)}</a></li>')
    rows.append(f'<li><a class="mobile-menu__link" href="{href("contact.html")}">Contact Us</a></li>')
    return f'''
<div class="mobile-menu" id="mobile-menu" aria-hidden="true" role="dialog" aria-label="Menu">
  <div class="mobile-menu__head">
    <a href="{href("index.html")}"><img src="@/assets/img/logo-light.png" alt="{e(FIRM)}" width="181" height="44"></a>
    <button class="mobile-menu__close" type="button" aria-label="Close menu">{I["close"]}</button>
  </div>
  <nav class="mobile-menu__body" aria-label="Mobile"><ul>{"".join(rows)}</ul></nav>
  <div class="mobile-menu__foot">
    <a href="{PHONE_HREF}">{I["phone"]}{PHONE}</a>
    <a href="mailto:{EMAIL}">{I["mail"]}{EMAIL}</a>
    <a href="{CALENDLY}" target="_blank" rel="noopener">{I["calendar"]}Appointments</a>
  </div>
</div>'''


def social_links(cls=""):
    return (f'<a href="{SOCIAL["x"]}" target="_blank" rel="noopener" aria-label="X (Twitter)">{I["x"]}</a>'
            f'<a href="{SOCIAL["facebook"]}" target="_blank" rel="noopener" aria-label="Facebook">{I["facebook"]}</a>'
            f'<a href="{SOCIAL["google"]}" target="_blank" rel="noopener" aria-label="Google">{I["google"]}</a>'
            f'<a href="{SOCIAL["taxbuzz"]}" target="_blank" rel="noopener" aria-label="TaxBuzz">{I["taxbuzz"]}</a>'
            f'<a href="{SOCIAL["countingworks"]}" target="_blank" rel="noopener" aria-label="CountingWorks">{I["cloud"]}</a>')


def header(current):
    return f'''
<a class="skip-link" href="#main">Skip to content</a>
<div class="progress-bar" aria-hidden="true"><span></span></div>
<div class="topbar">
  <div class="container">
    <div class="topbar__links">
      <a class="keep" href="mailto:{EMAIL}">{I["mail"]}<span>{EMAIL}</span></a>
      <a class="keep" href="{PHONE_HREF}">{I["phone"]}<span>{PHONE}</span></a>
      <a href="{CALENDLY}" target="_blank" rel="noopener">{I["calendar"]}Appointments</a>
      <a href="{href("tax-refund-tracker.html")}">{I["dollar"]}Track Your Refund</a>
    </div>
    <div class="topbar__social">{social_links()}</div>
  </div>
</div>
<header class="site-header">
  <div class="container">
    <a class="brand" href="{href("index.html")}" aria-label="{e(FIRM)} home">
      <img class="brand__color" src="@/assets/img/logo-color.png" alt="{e(FIRM)}" width="214" height="52">
      <img class="brand__light" src="@/assets/img/logo-light.png" alt="" width="214" height="52" aria-hidden="true">
    </a>
    <nav aria-label="Main">{render_nav(current)}</nav>
    <div class="header-cta">
      <a class="btn btn--sm" href="{href("contact.html")}">Contact Us {I["arrow"]}</a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span></button>
    </div>
  </div>
</header>
{render_mobile_menu()}'''


def footer():
    """Same contents as the live footer: Give us a call, Directory, Information, address, copyright."""
    col = lambda items: "".join(f'<li><a href="{href(p)}">{e(l)}</a></li>' for l, p in items)
    directory = [("Home Page", "index.html"), ("About Us", "firm-background.html"), ("Services", "services.html"),
                 ("Learning Center", BLOG), ("Contact", "contact.html")]
    # The live "Accessibility Statement" is a CountingWorks pop-up (its firm name is blank; the checklist asks
    # CountingWorks to fix it), so it is added back by CountingWorks on deployment.
    info = [("Terms Of Service", "terms-of-service.html"),
            ("Privacy Policy", "website-privacy-policy.html"),
            ("Powered by CountingWorks PRO", "https://www.countingworkspro.com")]
    return f'''
<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="@/assets/img/logo-light.png" alt="{e(FIRM)}" width="230" height="56" loading="lazy">
        <div class="footer-call"><small>Give us a call</small><a href="{PHONE_HREF}">{PHONE}</a></div>
        <a class="btn btn--light" href="{href("contact.html")}" style="margin-top:22px">Contact Us Now {I["arrow"]}</a>
      </div>
      <div class="footer-col"><h4>Directory</h4><ul>{col(directory)}</ul></div>
      <div class="footer-col"><h4>Information</h4><ul>{col(info)}</ul></div>
    </div>
    <div class="footer-bottom">
      <span>{ADDRESS_1}, {ADDRESS_2}</span>
      <span>&copy; 2026 {e(FIRM)} - All rights reserved.</span>
    </div>
  </div>
  <div class="footer-wordmark" aria-hidden="true">Prime CPA</div>
</footer>
<button class="to-top" type="button" aria-label="Back to top">
  <svg class="ring" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24"/></svg>
  {I["arrow-up"]}
</button>'''


# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------
KUMAR_LD = {
    "@type": "Person",
    "@id": LIVE + "/kumar-bhandari#person",
    "name": "Kumar Bhandari",
    "jobTitle": "Founder",
    "honorificSuffix": "CPA, PFS",
    "url": LIVE + "/kumar-bhandari",
    "image": og_url("kumar.jpg"),
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Georgia State University"},
    "memberOf": [
        {"@type": "Organization", "name": "Georgia Society of CPAs"},
        {"@type": "Organization", "name": "American Institute of Certified Public Accountants"},
    ],
    "worksFor": {"@id": LIVE + "/#firm"},
}
FIRM_LD = {
    "@type": "AccountingService",
    "@id": LIVE + "/#firm",
    "name": FIRM,
    "url": LIVE,
    "logo": CDN + "14492523/Untitled-design-%286%29.png",
    "image": og_url("office-exterior.webp"),
    "description": FIRM_SUMMARY,
    "telephone": PHONE,
    "email": EMAIL,
    "address": {"@type": "PostalAddress", "streetAddress": ADDRESS_1, "addressLocality": "Alpharetta",
                "addressRegion": "GA", "postalCode": "30009", "addressCountry": "US"},
    "areaServed": "US",
    "founder": {"@id": LIVE + "/kumar-bhandari#person"},
    "sameAs": [SOCIAL["x"], SOCIAL["facebook"], SOCIAL["taxbuzz"], SOCIAL["countingworks"]],
    "hasOfferCatalog": {
        "@type": "OfferCatalog", "name": "Services",
        "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": l}} for l, _ in SERVICE_LINKS],
    },
}


def ld_script(items):
    data = {"@context": "https://schema.org", "@graph": items}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def live_url(path):
    if path == "index.html":
        return LIVE + "/"
    return LIVE + "/" + path[:-5]


def demo_lock_links(doc):
    """Remove the href from every <a> that would leave the homepage."""
    def lock(m):
        tag = m.group(0)
        url = re.search(r'\shref="([^"]*)"', tag).group(1)
        if url.startswith("#") or url == "index.html" or url.startswith("index.html#"):
            return tag
        tag = re.sub(r'\s(href|target|rel)="[^"]*"', "", tag)
        return tag[:-1] + ' data-demo-locked aria-disabled="true">'

    return re.sub(r'<a\s[^>]*\shref="[^"]*"[^>]*>|<a\shref="[^"]*"[^>]*>', lock, doc)


def write_page(path, title, desc, body, og_img="office-exterior.webp", has_hero=False, ld=None):
    depth = path.count("/")
    prefix = "../" * depth
    graph = [FIRM_LD, KUMAR_LD] + (ld or [])
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{live_url(path)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(FIRM)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{live_url(path)}">
<meta property="og:image" content="{og_url(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_url(og_img)}">
<meta name="theme-color" content="#0a2230">
<link rel="icon" href="@/assets/img/favicon.png" type="image/png" sizes="32x32">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="@/assets/css/styles.css">
<script>document.documentElement.classList.add("js");</script>
{ld_script(graph)}
</head>
<body class="{"has-hero" if has_hero else ""}">
{header(path)}
<main id="main">
{body}
</main>
{footer()}
<script src="@/assets/js/main.js" defer></script>
</body>
</html>
'''
    doc = doc.replace('"@/', '"' + prefix).replace("(@/", "(" + prefix)
    if DEMO_HOME_ONLY and path == "index.html":
        doc = demo_lock_links(doc)
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------
def page_hero(title, eyebrow=None, lead=None, image=None, crumbs=None, title_html=None):
    crumbs = crumbs or []
    trail = [f'<a href="{href("index.html")}">Home</a>']
    for label, p in crumbs:
        trail.append(I["chev-r"])
        trail.append(f'<a href="{href(p)}">{e(label)}</a>' if p else f'<span aria-current="page">{e(label)}</span>')
    media = (f'<div class="page-hero__media" data-parallax="0.18"><img src="@/assets/img/{image}" alt="" '
             f'fetchpriority="high"></div>') if image else ""
    cls = "page-hero" if image else "page-hero page-hero--plain"
    eb = f'<p class="eyebrow eyebrow--light" data-reveal>{e(eyebrow)}</p>' if eyebrow else ""
    ld = f'<p class="lead" data-reveal style="--d:.25s">{lead}</p>' if lead else ""
    return f'''
<section class="{cls}">
  {media}
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb" data-reveal="fade">{"".join(trail)}</nav>
    {eb}
    <h1 data-split>{title_html or e(title)}</h1>
    {ld}
  </div>
</section>'''


CTA_TITLE = "Let’s Build a Stronger Financial Future"
CTA_TEXT = (f"If you’re ready for a tax and accounting partner that delivers clarity, strategy, and confidence, "
            f"{FIRM} is here to help. Schedule a consultation today to discover how our team can support your success.")


def cta_band(title=CTA_TITLE, text=CTA_TEXT, actions=False):
    buttons = (f'<div class="cta-band__actions"><a class="btn btn--light" href="{href("contact.html")}">Get in Touch {I["arrow"]}</a></div>'
               if actions else "")
    return f'''
<section class="section section--tight">
  <div class="container">
    <div class="cta-band" data-reveal="scale">
      <span class="cta-band__glow" aria-hidden="true"></span>
      <div>
        <h2 data-split>{e(title)}</h2>
        <p>{e(text)}</p>
      </div>
      {buttons}
    </div>
  </div>
</section>'''


LEGAL_SUBMIT = (f'I confirm this is a service inquiry and not an advertising message or solicitation. By clicking '
                f'“Submit”, I acknowledge and agree to the creation of an account and to the '
                f'<a href="{href("terms-of-service.html")}">Terms of Service</a> and '
                f'<a href="{href("website-privacy-policy.html")}">Privacy Policy</a>.')
SMS_CONSENT = (f'By checking this box, I agree to receive Text messages about informational messages from {FIRM} at '
               f'the phone number provided above. The SMS frequency may vary. Message and data rates may apply. '
               f'Text HELP to {PHONE} for assistance. Reply STOP to opt out of receiving SMS messages from {FIRM}. '
               f'You will receive no further SMS communication. For more information, please refer to our '
               f'<a href="{href("website-privacy-policy.html")}">Privacy Policy</a> and '
               f'<a href="{href("sms-terms-and-conditions.html")}">SMS Terms and Conditions</a> on our website.')


def field(name, label, kind="text", required=False, full=False, textarea=False, autocomplete=None):
    req = " required" if required else ""
    star = ' <span class="req">*</span>' if required else ""
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
    cls = "field full" if full else "field"
    if textarea:
        ctl = f'<textarea id="{name}" name="{name}" placeholder=" "{req}></textarea>'
    else:
        ctl = f'<input id="{name}" name="{name}" type="{kind}" placeholder=" "{req}{ac}>'
    return f'<div class="{cls}">{ctl}<label for="{name}">{e(label)}{star}</label></div>'


def contact_form(prefix="c"):
    return f'''
<form class="form-card" data-cw-form="contact" novalidate data-reveal="right">
  <div class="form-grid">
    {field(prefix + "-first", "First name", required=True, autocomplete="given-name")}
    {field(prefix + "-last", "Last name", required=True, autocomplete="family-name")}
    {field(prefix + "-email", "Email", "email", required=True, autocomplete="email")}
    {field(prefix + "-phone", "Phone Number", "tel", autocomplete="tel")}
    {field(prefix + "-message", "Message", full=True, textarea=True)}
    <p class="form-legal full">{LEGAL_SUBMIT}</p>
    <label class="check full"><input type="checkbox" name="sms_consent"><span>{SMS_CONSENT}</span></label>
    <div class="form-actions full"><button class="btn" type="submit">Submit {I["arrow"]}</button></div>
  </div>
</form>'''


def aside(links, current, heading):
    nav = "".join(
        f'<a href="{href(p)}"{cur_attr(p, current)}>{e(l)}{I["arrow"]}</a>' for l, p in links)
    return f'''
<aside class="aside" data-reveal="right">
  <div class="aside-card aside-card--dark">
    <h3>Give us a call</h3>
    <p>{ADDRESS_1}, {ADDRESS_2}</p>
    <a class="aside-phone" href="{PHONE_HREF}">{I["phone"]}{PHONE}</a>
    <a class="btn btn--light" href="{href("contact.html")}">Contact Us Now {I["arrow"]}</a>
  </div>
  <div class="aside-card aside-nav">{f"<h4>{e(heading)}</h4>" if heading else ""}{nav}</div>
</aside>'''


def paras(text):
    """Blank-line separated text -> <p> elements (text may contain inline HTML)."""
    return "".join(f"<p>{p.strip()}</p>" for p in text.strip().split("\n\n"))


# ---------------------------------------------------------------------------
# Homepage
# ---------------------------------------------------------------------------
HERO_SLIDES = [
    ("office-reception.webp", "Your trusted business advisors.", "Explore our services.", "services.html"),
    ("tax-law-book.webp", "We know the Tax law.", "Learn More", "firm-background.html"),
    ("office-conference.webp", "We measure our success.", "Learn More", "about-us/why-were-the-best.html"),
    ("tax-law-changes.webp", "One size does not fit all.", "We are ready to help you!", "services.html"),
    ("office-exterior.webp", "Minimize your tax liability.", "Learn More", "services/tax-preparation-planning.html"),
    # checklist: this slide now points to the full industries list (Firm Background) instead of Healthcare only
    ("plumber.webp", "Every industry is different.", "Learn More", "firm-background.html#who-we-serve"),
    # the live slide has no button
    ("tax-form-estimated.webp", "Small business accounting made easy.", None, None),
    # the live slider ends with two office photos that carry no headline
    ("office-lobby.jpg", None, None, None),
    ("office-boardroom.jpg", None, None, None),
]

# checklist: card order is Tax first, then Accounting; Tax Preparation and Fractional CFO cards included
HOME_SERVICES = [
    ("Tax Planning/Strategy", "tax-calculator.webp", "services/tax-preparation-planning.html", """
Sometimes, just filing your return isn’t enough. You might need a plan to pay the least you legally can. Our tax planning service starts with a proactive look at all your income and expenses. Our goal is to discover every legal deduction, credit, and strategy available, before we file your return.

All without “overly aggressive” strategies, that push “gray areas” which can raise red flags and put you at a higher risk for audits."""),
    ("Tax Preparation", "irs-block.webp", "services/tax-preparation-planning.html", """
The IRS likes nothing better than individuals preparing their own taxes. Today, tax laws are so complicated that filing a relatively simple return can be confusing. It’s too easy to overlook deductions and credits to which you are entitled. There’s no substitute for the assistance of an experienced tax professional.

When it comes to tax season, we have you covered. Using our extensive technology combined with years of experience, we offer reliable service and advice you can trust."""),
    ("Accounting and Bookkeeping", "accounting-teamwork.webp", "services/accounting-bookkeeping.html", f"""
We take the accounting stress off your mind and place it into the hands of tax professionals. We keep it simple. Our team doesn’t stop at your taxes. We provide a number of additional accounting services, mixed and matched according to your business needs.

We aim to relieve the stress of managing your month-to-month finances. {FIRM} creates customized monthly programs for your business such as bookkeeping, payroll, business advisory, and fractional CFO services."""),
    ("Fractional CFO Services", "svc-cfo.webp", "services/part-time-cfo.html", f"""
At {FIRM}, our Part-Time CFO Services provide growing businesses with high-level financial leadership—without the cost of a full-time executive. Designed for small to mid-sized companies that need strategic guidance, budgeting support, and forward-looking financial analysis, our services help you make confident decisions rooted in accurate data and clear projections."""),
    ("Virtual Services", "virtual-seaside.webp", "services/virtual-tax-preparation.html", """
The best part about our services is that you don’t even have to leave your home or office to work with us. We have designed tools and systems that enables us to provide you personalized services. By utilizing cloud technology we are able to make your tax forms and documents easily accessible and user friendly. This allows you to spend less time on tax work and more time growing your business.

We have clients all over the United States and internationally. We can fully serve you and your business wherever you may be."""),
]

# The four tiles on the live homepage, with their wording.
# checklist: the Restaurants tile mentions retail but linked only to Restaurants;
# it now links to both the Restaurants and the Retail page.
INDUSTRY_CARDS = [
    ("Healthcare and medical practices needing reliable Medical Office Accounting", "ind-healthcare-card.webp",
     [(None, INDUSTRY_LINKS[0][1])]),
    ("Law firms seeking specialized Law Office Tax Services", "ind-law-card.webp",
     [(None, INDUSTRY_LINKS[2][1])]),
    ("Real estate professionals requiring strategic tax planning and bookkeeping", "ind-realestate-card.webp",
     [(None, INDUSTRY_LINKS[3][1])]),
    ("Restaurants and retail businesses looking for accurate accounting and operational insight", "ind-restaurant-card.webp",
     [("Restaurants", INDUSTRY_LINKS[4][1]), ("Retail", INDUSTRY_LINKS[5][1])]),
]

# checklist: placeholder item ("Database Backups / Consequatur…") removed; items shown as plain text
WHY_ITEMS = [
    "Deep tax expertise backed by CPA, PFS &amp; Master of Taxation credentials",
    "A proactive approach through year-round planning—not just annual filings",
    "Personalized service with clarity, communication, and education at the forefront",
    "Specialized experience serving small to mid-sized businesses and high-net-worth individuals",
    "Comprehensive solutions including tax preparation, planning, bookkeeping, payroll, and part-time CFO services",
]

# Reviews currently on the live site (5-star filter). To be replaced by the CountingWorks review feed.
REVIEWS = [("So good at what they do.", "Lionel K."), ("Excellent.", "Lionel K.")]

# Latest Learning Center posts on the live homepage at the time of the snapshot (Oct 2026).
POSTS = [
    ("blog-1.jpg", "10/14/2026 08:55 AM", "Why Clean Financial Statements Matter When You Sell a Business",
     "Discover why clean, consistent financial statements and trusted accounting guidance build buyer confidence, streamline due diligence, and maximize value when selling a business.",
     BLOG + "/why-clean-financial-statements-matter-when-you-sell-a-business"),
    ("blog-2.jpg", "10/13/2026 01:36 PM", "Crowdfunding and Taxes: What Organizers and Contributors Need to Know",
     "A comprehensive guide explaining the tax implications of donation-based, rewards-based, and equity crowdfunding for both campaign organizers and backers.",
     BLOG + "/crowdfunding-and-taxes-what-organizers-and-contributors-need-to-know"),
    ("blog-3.jpg", "10/12/2026 12:36 PM", "Thinking About Selling Your Business? Start Preparing Your Financials Now",
     "Preparing to sell a business requires clean, credible financial records. Learn how early financial preparation, add-back documentation, and lender alignment impact deal value.",
     BLOG + "/thinking-about-selling-your-business-start-preparing-your-financials-now"),
    ("blog-4.jpg", "10/12/2026 09:58 AM", "Keeping Your Beneficiaries Up-to-Date",
     "A periodic review of your designated beneficiaries is vital. Learn why you should check your will, savings, and insurance policies to protect your estate planning goals.",
     BLOG + "/keeping-your-beneficiaries-up-to-date"),
]


def build_home():
    slides = []
    for i, (img, title, btn, link) in enumerate(HERO_SLIDES):
        loading = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'
        active = " is-active" if i == 0 else ""
        slides.append(f'''
  <div class="hero__slide{active}" aria-roledescription="slide" aria-label="{i + 1} of {len(HERO_SLIDES)}"{"" if i == 0 else ' aria-hidden="true"'}>
    <div class="hero__media"><img src="@/assets/img/{img}" alt="" {loading}></div>
    <div class="hero__content container">
      {f'<h2 class="hero__title">{e(title)}</h2>' if title else ""}
      {f'<div class="hero__actions"><a class="btn btn--light" href="{href(link)}">{e(btn)} {I["arrow"]}</a></div>' if btn else ""}
    </div>
  </div>''')
    dots = "".join(f'<button class="hero__dot" type="button" aria-label="Go to slide {i + 1}"><span></span></button>'
                   for i in range(len(HERO_SLIDES)))
    hero = f'''
<section class="hero" aria-roledescription="carousel" aria-label="Highlights" data-delay="7000" tabindex="-1">
  {"".join(slides)}
  <div class="hero__ui">
    <div class="container">
      <div class="hero__count"><b>01</b> / {len(HERO_SLIDES):02d}</div>
      <div class="hero__dots">{dots}</div>
      <div class="hero__arrows">
        <button class="hero__arrow hero__arrow--prev" type="button" aria-label="Previous slide">{I["arrow-left"]}</button>
        <button class="hero__arrow hero__arrow--next" type="button" aria-label="Next slide">{I["arrow"]}</button>
      </div>
    </div>
  </div>
</section>'''

    # Quick-contact bar overlapping the bottom of the hero (details from the live site)
    quick_items = [
        (PHONE_HREF, I["phone"], "Give us a call", PHONE, False),
        (f"mailto:{EMAIL}", I["mail"], "Email", EMAIL, False),
        (href("contact.html"), I["pin"], "Our Office", f"{ADDRESS_1}, Alpharetta", False),
        (href("tax-refund-tracker.html"), I["dollar"], "Tax Refund Tracker", "Track Your Refund", False),
    ]
    quick = f'''
<section class="quickbar" aria-label="Contact {e(FIRM)}">
  <div class="container">
    <div class="quickbar__card">
      {"".join(f'<a class="quickbar__item" href="{u}"><span class="quickbar__icon">{ic}</span><span class="quickbar__text"><small>{e(lbl)}</small><strong>{e(val)}</strong></span><span class="quickbar__go">{I["arrow"]}</span></a>' for u, ic, lbl, val, _ in quick_items)}
    </div>
  </div>
</section>'''

    welcome = f'''
<section class="section">
  <div class="container welcome">
    <div class="welcome__portrait" data-reveal="left">
      <span class="welcome__deco" aria-hidden="true"></span>
      <div class="portrait-frame" data-reveal="clip"><img src="@/assets/img/office-lobby.jpg" alt="Reception and waiting area at the {e(FIRM)} office, 2300 Lakeview Pkwy, Alpharetta" loading="lazy" data-parallax="0.06"></div>
      <a class="welcome__badge" href="{href("kumar-bhandari.html")}" data-reveal style="--d:.5s">
        <img class="welcome__avatar" src="@/assets/img/kumar.jpg" alt="Kumar Bhandari" width="132" height="132" loading="lazy">
        <span class="welcome__badge-text"><strong>Kumar Bhandari</strong></span>
      </a>
    </div>
    <div>
      <h1 data-split>Welcome to {e(FIRM)} — <em>Strategic Tax &amp; Accounting</em></h1>
      <div class="prose" data-reveal style="--d:.2s">
        <p>Led by Kumar Bhandari, a CPA, Personal Financial Specialist (PFS), and with a Master of Taxation, our firm provides an education-driven, relationship-focused approach that empowers clients to understand their numbers and plan for the future—not just react to tax season. At {e(FIRM)}, we help business owners, professionals, and high-net-worth individuals make confident financial decisions through expert tax planning, proactive accounting, and year-round advisory services.</p>
        <p>Whether you run a medical office, law firm, retail shop, restaurant, real estate operation, or car dealership, you deserve a financial partner who understands your industry and the challenges that come with growth. Our team delivers specialized support, from tax strategy and bookkeeping to payroll, part-time CFO services, and advanced planning designed to help you keep more of what you earn.</p>
      </div>
      <a class="btn" href="{href("contact.html")}" data-reveal style="--d:.3s">Get in Touch {I["arrow"]}</a>
    </div>
  </div>
</section>'''

    n_svc = len(HOME_SERVICES)
    tabs, slides = [], []
    for i, (title, img, link, text) in enumerate(HOME_SERVICES):
        tabs.append(f'''
        <button class="svx-tab{" is-active" if i == 0 else ""}" type="button" role="tab" id="svx-tab-{i}" aria-controls="svx-panel-{i}" aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else ' tabindex="-1"'}>
          <span class="svx-tab__num">{i + 1:02d}</span>
          <span class="svx-tab__title">{e(title)}</span>
          <span class="svx-tab__go">{I["arrow"]}</span>
        </button>''')
        slides.append(f'''
        <article class="svx-slide{" is-active" if i == 0 else ""}" role="tabpanel" id="svx-panel-{i}" aria-labelledby="svx-tab-{i}">
          <div class="svx-slide__media"><img src="@/assets/img/{img}" alt="" loading="lazy"></div>
          <span class="svx-slide__chip">{i + 1:02d} <i>/</i> {n_svc:02d}</span>
          <span class="svx-slide__num" aria-hidden="true">{i + 1:02d}</span>
          <div class="svx-slide__body">
            <h3><a class="svx-slide__link" href="{href(link)}">{e(title)} {I["arrow"]}</a></h3>
            <div class="svx-slide__text">{paras(e(text))}</div>
          </div>
        </article>''')
    services = f'''
<section class="section svx" id="services">
  <div class="svx__bg" aria-hidden="true"></div>
  <div class="container">
    <div class="svx__head">
      <div><p class="eyebrow eyebrow--light" data-reveal>Our services:</p><h2 data-split>Our focus is on <em>your success.</em></h2></div>
    </div>
    <div class="svx__grid" data-svx>
      <div class="svx__list" role="tablist" aria-label="Our services" data-reveal="left">
        <span class="svx__indicator" aria-hidden="true"><span class="svx__bar"></span></span>{"".join(tabs)}
      </div>
      <div class="svx__stage" data-reveal="scale">{"".join(slides)}
      </div>
    </div>
  </div>
</section>'''

    def industry_card(i, t, img, links):
        num = f'<span class="industry-card__num">{i + 1:02d}</span>'
        pic = f'<img src="@/assets/img/{img}" alt="" loading="lazy">'
        if len(links) == 1:
            return (f'<a class="industry-card" href="{href(links[0][1])}" data-reveal>{pic}{num}'
                    f'<div class="industry-card__body"><h3>{e(t)}</h3><span class="industry-card__arrow">{I["arrow"]}</span></div></a>')
        pills = "".join(f'<a class="industry-card__pill" href="{href(p)}">{e(l)} {I["arrow"]}</a>' for l, p in links)
        return (f'<div class="industry-card industry-card--multi" data-reveal>{pic}{num}'
                f'<div class="industry-card__body"><h3>{e(t)}</h3><div class="industry-card__pills">{pills}</div></div></div>')

    cards = "".join(industry_card(i, t, img, links) for i, (t, img, links) in enumerate(INDUSTRY_CARDS))
    industries = f'''
<section class="section" id="industries">
  <div class="container">
    <div class="section-head section-head--split">
      <div><h2 data-split>Who We Serve</h2></div>
      <p class="lead" data-reveal style="--d:.2s">We proudly support a diverse range of industries, including:</p>
    </div>
    <div class="industry-grid" data-stagger="0.07">{cards}</div>
  </div>
</section>'''

    firm = f'''
<section class="section section--ivory">
  <div class="container split">
    <div class="split__media" data-reveal="left">
      <div class="frame" data-reveal="clip"><img src="@/assets/img/office-exterior.webp" alt="Exterior of the Lakeview office building in Alpharetta, Georgia" loading="lazy" data-parallax="0.08"></div>
      <div class="split__float" data-reveal="scale" style="--d:.4s"><img src="@/assets/img/office-boardroom.jpg" alt="Conference room at the {e(FIRM)} office" loading="lazy"></div>
    </div>
    <div class="split__body">
      <h2 data-split>A Firm Built on Expertise, Clarity &amp; <em>Proactive Strategy</em></h2>
      <div class="prose" data-reveal style="--d:.2s;margin-top:30px">
        <p>What sets {e(FIRM)} apart is our commitment to forward-thinking tax planning. Through our signature annual tax-strategy engagement—with monthly or quarterly meetings and unlimited tax support—you receive continuous guidance tailored to your goals. Clients trust our firm for Advanced Tax Strategies, Business Tax Advisor guidance, and customized solutions for professionals and business owners.</p>
        <p>We combine deep technical expertise with practical, day-to-day support. Whether you need Accounting &amp; Bookkeeping, Virtual Tax Preparation, or Payroll Services, our team brings consistency, precision, and insight to every financial decision. High-net-worth individuals benefit from dedicated advisory services that address wealth preservation, multigenerational planning, and complex tax considerations.</p>
      </div>
      <a class="btn" href="{href("contact.html")}" data-reveal style="--d:.3s">Get in Touch {I["arrow"]}</a>
    </div>
  </div>
</section>'''

    why = f'''
<section class="section section--navy">
  <div class="container why">
    <div class="why__intro">
      <h2 data-split>Why Clients Choose <em>{e(FIRM)}</em></h2>
    </div>
    <ol class="why__list">{"".join(f'<li class="why__item"><p>{t}</p></li>' for t in WHY_ITEMS)}</ol>
  </div>
</section>'''

    def review_words(q):
        return " ".join(f'<span class="tq-w"><span style="--i:{i}">{e(w)}</span></span>' for i, w in enumerate(q.split()))

    def initials(n):
        return "".join(w[0] for w in n.replace(".", "").split())

    review_cards = "".join(f'''
        <article class="tq-card{" is-active" if i == 0 else ""}" aria-roledescription="slide" aria-label="Review {i + 1} of {len(REVIEWS)}">
          <div class="tq-card__top">
            <span class="tq-card__mark" aria-hidden="true">{I["quote"]}</span>
            <div class="tq-stars" role="img" aria-label="5 out of 5 stars">{"".join(f'<span style="--s:{k}">{I["star"]}</span>' for k in range(5))}</div>
          </div>
          <blockquote class="tq-card__quote">{review_words(q)}</blockquote>
          <footer class="tq-card__person">
            <span class="tq-card__avatar" aria-hidden="true"><span>{initials(n)}</span></span>
            <strong>{e(n)}</strong>
          </footer>
        </article>''' for i, (q, n) in enumerate(REVIEWS))
    testimonials = f'''
<section class="section testimonials" id="reviews" aria-roledescription="carousel" aria-label="Client reviews">
  <span class="tq-bg-mark" aria-hidden="true">{I["quote"]}</span>
  <div class="container tq">
    <div class="tq__intro">
      <h2 data-split>See why our clients <em>love us!</em></h2>
      <div class="tq__nav" data-reveal style="--d:.25s">
        <div class="tq__count"><b>01</b><span>/ {len(REVIEWS):02d}</span></div>
        <div class="tq__progress" aria-hidden="true"><span></span></div>
        <div class="tq__buttons">
          <button class="tq-btn" type="button" data-prev aria-label="Previous review">{I["arrow-left"]}</button>
          <button class="tq-btn" type="button" data-next aria-label="Next review">{I["arrow"]}</button>
        </div>
      </div>
    </div>
    <div class="tq__stage" data-testimonials data-reveal="scale" aria-live="polite">{review_cards}
    </div>
  </div>
</section>'''

    office = f'''
<section class="section">
  <div class="container">
    <div class="section-head">
      <h2 data-split>Our Office</h2>
    </div>
    <div class="gallery" data-stagger="0.1">
      <figure data-reveal="clip"><img src="@/assets/img/office-lobby.jpg" alt="Reception desk and waiting area" loading="lazy"></figure>
      <figure data-reveal="clip"><img src="@/assets/img/office-boardroom.jpg" alt="Conference room with city views" loading="lazy"></figure>
      <figure data-reveal="clip"><img src="@/assets/img/office-exterior.webp" alt="Office building exterior" loading="lazy"></figure>
      <figure data-reveal="clip"><img src="@/assets/img/office-reception.webp" alt="Office reception" loading="lazy"></figure>
      <figure data-reveal="clip"><img src="@/assets/img/office-conference.webp" alt="Large conference room" loading="lazy"></figure>
    </div>
    <div class="office-meta" data-reveal>
      <address>{ADDRESS_1}<br>{ADDRESS_2}</address>
    </div>
  </div>
</section>'''

    posts = "".join(f'''
      <article class="post-card" data-reveal>
        <a class="post-card__media" href="{url}"><img src="@/assets/img/{img}" alt="" loading="lazy"></a>
        <p class="post-card__meta">{date}</p>
        <h3><a href="{url}">{e(t)}</a></h3>
        <p>{e(ex)}</p>
        <a class="link-arrow post-card__more" href="{url}">Read full story {I["arrow"]}</a>
      </article>''' for img, date, t, ex, url in POSTS)
    blog = f'''
<section class="section section--ivory">
  <div class="container">
    <div class="section-head section-head--split">
      <div><h2 data-split>Latest Posts</h2></div>
      <div class="newsletter newsletter--inline" data-reveal style="--d:.2s">
        <p class="lead">Get weekly articles in your inbox on how to grow your business.</p>
        <form data-cw-form="newsletter" novalidate>
          <label class="sr-only" for="nl-email">Email address</label>
          <input id="nl-email" type="email" name="email" placeholder="Email address" autocomplete="email" required>
          <button class="btn btn--sm" type="submit">Notify me</button>
        </form>
      </div>
    </div>
    <div class="post-grid post-grid--4" data-stagger="0.1">{posts}</div>
    <div class="post-all" data-reveal><a class="btn btn--ghost" href="{BLOG}">View all articles {I["arrow"]}</a></div>
  </div>
</section>'''

    contact = f'''
<section class="section" id="contact">
  <div class="container contact-grid">
    <div>
      <h2 data-split>Get in Touch with <em>{e(FIRM)}</em></h2>
      <p class="lead" data-reveal style="--d:.2s;margin-top:24px">At {e(FIRM)}, we're committed to delivering timely and reliable solutions for your tax and accounting needs. Fill out the form below to reach out to us.</p>
    </div>
    {contact_form("home")}
  </div>
</section>'''

    body = hero + quick + welcome + services + industries + firm + why + testimonials + office + blog + cta_band(actions=False) + contact
    write_page("index.html", f"{FIRM} - Accounting & Taxes in Alpharetta, Georgia",
               FIRM_SUMMARY, body, og_img="office-exterior.webp", has_hero=True)


# ---------------------------------------------------------------------------
# About pages
# ---------------------------------------------------------------------------
def build_firm_background():
    serve = [
        ("Medical practices &amp; physician groups", INDUSTRY_LINKS[0][1]),
        ("Law offices", INDUSTRY_LINKS[2][1]),
        ("Retail businesses", INDUSTRY_LINKS[5][1]),
        ("Car dealerships", INDUSTRY_LINKS[6][1]),
        ("Restaurants &amp; hospitality groups", INDUSTRY_LINKS[4][1]),
        ("Real estate professionals and investors", INDUSTRY_LINKS[3][1]),
        ("High-net-worth individuals", INDUSTRY_LINKS[1][1]),
    ]
    # checklist: these links pointed at CountingWorks preview pages; now point at the real pages
    serve_html = "".join(f'<a href="{href(p)}">{t}{I["arrow"]}</a>' for t, p in serve)
    engagement = [
        "Quarterly—or even monthly—tax strategy meetings",
        "Unlimited appointments related to tax questions and decisions",
        "Implementation of advanced tax-saving strategies",
        "Preparation of their prior-year tax return (e.g., engagement in 2026 includes the 2025 return)",
    ]
    eng_cards = "".join(f'<div class="pillar" data-reveal><span class="pillar__num">{i + 1:02d}</span><p style="margin-top:18px;font-family:var(--font-display);font-size:1.3rem;line-height:1.35;color:var(--navy-900)">{t}</p></div>'
                        for i, t in enumerate(engagement))
    choose = [
        "Peace of mind and complete compliance",
        "A more insightful, strategic view of their business and personal finances",
        "Identifying tax-saving opportunities, both short- and long-term",
        "Support in operating more efficiently within their existing financial structure",
        "Genuine education and guidance—not just transactions",
    ]
    body = page_hero("Get to Know Prime CPA LLC", "About",
                     f"{FIRM} is located in Alpharetta, Georgia and is an expert in all areas of accounting, taxes, and business services.",
                     "firm-background.webp", [("About Us", None), ("Firm Background", None)],
                     title_html=f"Get to Know {e(FIRM)}")
    body += f'''
<section class="section">
  <div class="container split">
    <div class="split__body">
      <p class="eyebrow" data-reveal>Working With Us</p>
      <h2 data-split>Strategic Guidance for Alpharetta’s Most <em>Driven Professionals</em></h2>
      <div class="prose" data-reveal style="--d:.2s;margin-top:30px">
        <p class="lead">In <strong>Alpharetta, Georgia</strong>, {e(FIRM)} supports the entrepreneurs, professionals, and high-net-worth individuals who want more than a standard accountant—they want a long-term partner who proactively strengthens their financial life. Through <strong>tax planning, tax preparation, bookkeeping, accounting, payroll,</strong> and <strong>full-service support for small to mid-sized businesses</strong>, the firm provides clarity, efficiency, and strategy for clients who expect precision at every level.</p>
      </div>
    </div>
    <div class="split__media" data-reveal="right">
      <div class="frame frame--wide" data-reveal="clip"><img src="@/assets/img/office-boardroom.jpg" alt="Conference room at the {e(FIRM)} office in Alpharetta" loading="lazy" data-parallax="0.06"></div>
    </div>
  </div>
</section>

<section class="section section--ivory" id="who-we-serve">
  <div class="container split">
    <div>
      <h2 data-split>Who We Serve</h2>
      <p class="lead" data-reveal style="--d:.2s;margin-top:24px">Our practice is built for clients who value insight as much as accuracy, including:</p>
    </div>
    <div data-reveal="right">
      <nav class="aside-card aside-nav" aria-label="Who We Serve" style="background:#fff">{serve_html}</nav>
      <p class="lead" style="margin-top:28px">These are people who manage complex financial decisions daily—and want to understand the why behind the numbers.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container split split--reverse">
    <div class="split__media" data-reveal="right">
      <figure class="founder-photo" data-reveal="scale">
        <div class="founder-photo__frame"><img src="@/assets/img/kumar.jpg" alt="Kumar Bhandari, CPA, PFS" width="350" height="350" loading="lazy"></div>
      </figure>
    </div>
    <div class="split__body">
      <h2 data-split>Education as a Core Value</h2>
      <div class="prose" data-reveal style="--d:.2s;margin-top:30px">
        <p>Founder Kumar Bhandari’s background shapes everything we do. As a <strong>CPA, Personal Financial Specialist (PFS)</strong>, and holder of a <strong>Master’s in Taxation</strong>, Kumar brings rigorous technical expertise to every engagement. But he also brings something rarer: the heart of a teacher. He has spent years lecturing at the university level during the tax off-season, and that passion for education is woven into our client experience.</p>
        <p>Clients who come with questions feel encouraged—not rushed. Curious minds who want to understand tax implications, financial habits, or business performance find a partner who welcomes thoughtful discussion.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--sand">
  <div class="container">
    <div class="section-head section-head--split">
      <div><h2 data-split>A Modern, Upgraded Engagement Model</h2></div>
      <p class="lead" data-reveal style="--d:.2s">For those who want proactive strategy, the firm offers an <strong>annual tax-planning engagement</strong> designed for true partnership. Clients pay a fixed monthly fee for 12 months and receive:</p>
    </div>
    <div class="pillars" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))" data-stagger="0.1">{eng_cards}</div>
    <div class="prose" data-reveal style="margin-top:48px;max-width:820px">
      <p>This model gives business owners and high-income individuals year-round access to a tax specialist—not just seasonal help.</p>
      <p>For clients who simply need accurate, timely filings, the firm continues to offer traditional <strong>tax preparation</strong> as well.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container split" style="align-items:start">
    <div>
      <p class="eyebrow" data-reveal>Linking Tax Strategy to Wealth Strategy</p>
      <div class="prose" data-reveal style="--d:.1s">
        <p class="lead">With the <strong>PFS designation</strong>, Kumar is uniquely positioned at the intersection of tax and personal finance. While the firm does not sell investments, Kumar and his team help clients connect with vetted professionals who can deliver investment support aligned with tax-efficient goals. Every recommendation comes from a place of fiduciary responsibility, clarity, and long-term benefit.</p>
      </div>
    </div>
    <div>
      <p class="eyebrow" data-reveal>Why People Choose Kumar and His Team</p>
      <div class="prose" data-reveal style="--d:.1s">
        <p>Clients come to the firm for:</p>
        <ul>{"".join(f"<li>{t}</li>" for t in choose)}</ul>
        <p>Kumar also maintains deep local involvement as Treasurer of NASEA and an active contributor to the Alpharetta professional community.</p>
        <p>For clients who want the confidence that every financial decision is backed by expertise, strategy, and clarity, this firm is built with you in mind. Call <a href="{PHONE_HREF}">{PHONE}</a> to start working with all of the experts at {e(FIRM)} today.</p>
      </div>
    </div>
  </div>
</section>'''
    write_page("firm-background.html", f"Get to Know {FIRM} - Tax and Accounting Experts",
               f"In Alpharetta, Georgia, {FIRM} supports the entrepreneurs, professionals, and high-net-worth individuals who want more than standard accounting.",
               body, og_img="firm-background.webp")


TEAM = [
    ("Kumar Bhandari", "CPA", "kumar.jpg", "kumar-bhandari.html"),
    # checklist: headshot and title for Deborah Thomas still to be supplied
    ("Deborah Thomas", "", None, "deborah-thomas.html"),
    ("Manoj Silwal MBA", "Accounting Consultant", None, "manoj-silwal.html"),
]


def monogram(name):
    parts = [w for w in name.replace("MBA", "").split() if w]
    return parts[0][0] + parts[-1][0]


def build_team():
    cards = []
    for name, role, img, link in TEAM:
        media = (f'<img src="@/assets/img/{img}" alt="{e(name)}" loading="lazy">' if img
                 else f'<span class="team-card__mono" aria-hidden="true">{monogram(name)}</span>')
        inner = f'<div class="team-card__media">{media}</div><div class="team-card__body"><h3>{e(name)}</h3><p>{e(role)}</p></div>'
        cards.append(f'<a class="team-card" href="{href(link)}" data-reveal>{inner}</a>' if link
                     else f'<div class="team-card" data-reveal>{inner}</div>')
    body = page_hero("Meet the Team", None, f"Meet the members behind {e(FIRM)}. We are here to help you succeed!",
                     None, [("About Us", "firm-background.html"), ("Meet the Team", None)])
    body += f'''
<section class="section">
  <div class="container"><div class="team-grid" data-stagger="0.12">{"".join(cards)}</div></div>
</section>'''
    write_page("about-us/meet-the-team.html", f"Meet the Team - {FIRM}",
               f"Meet the team at {FIRM}. Founder Kumar Bhandari and his staff look forward to assisting with all of your tax, accounting, and advisory needs.",
               body, og_img="kumar.jpg")


def bio_page(path, name, role, photo, facts, text, title, desc, og_img="kumar.jpg"):
    photo_html = (f'<div class="bio__photo" data-reveal="clip"><img src="@/assets/img/{photo}" alt="{e(name)}"></div>' if photo
                  else f'<div class="bio__photo bio__photo--mono" data-reveal="scale"><span class="team-card__mono" aria-hidden="true">{monogram(name)}</span></div>')
    body = page_hero(name, role or None, None, None, [("About Us", "firm-background.html"), ("Meet the Team", "about-us/meet-the-team.html"), (name, None)])
    body += f'''
<section class="section">
  <div class="container bio">
    <div class="bio__card">
      {photo_html}
    </div>
    <div class="prose" data-reveal style="--d:.15s">{text}</div>
  </div>
</section>'''
    write_page(path, title, desc, body, og_img=og_img)


def build_bios():
    # checklist: experience shown as 18+ years (was 15); "Grant Thornton" spelling fixed;
    # reference to the Suwanee firm and its location removed.
    kumar_text = paras("""
Kumar brings 18+ years of tax, accounting, auditing and consulting experience to the firm. He started his career as an auditor with Grant Thornton. After transitioning into tax, Kumar worked with large local and national accounting firms, including Williams, Benator &amp; Libby and Aprio in different roles.

His industry experience includes professional services, construction, retail, hospitality, software, manufacturing and real estate. Functional experience includes accounting, auditing, tax compliance, tax planning, business consulting and payroll/sales tax. Kumar specializes in business/owner tax structuring including retirement plans and complex multi-state tax returns. Kumar particularly enjoys working with individuals, and those small and medium-sized businesses that are seeking for a more personal touch.

Kumar holds a CPA license in the state of Georgia. He earned his Master of Taxation degree and a Bachelor of Business Administration degree from Georgia State University, Atlanta, Georgia. Kumar is a member of the Georgia Society of CPA's and the American Institute of Certified Public Accountants.

Kumar lives in Johns Creek, GA with his wife and two daughters. He serves on several community volunteer organizations.""")
    kumar_text = kumar_text.replace("<p>Kumar brings", '<p class="article__lede" style="margin-bottom:0">Kumar brings', 1)
    bio_page("kumar-bhandari.html", "Kumar Bhandari", "CPA", "kumar.jpg", [
        ("Credentials", "CPA · Personal Financial Specialist (PFS) · Master of Taxation"),
        ("Education", "Master of Taxation and Bachelor of Business Administration, Georgia State University, Atlanta, Georgia"),
        ("Memberships", "Georgia Society of CPA's · American Institute of Certified Public Accountants"),
        ("Phone", f'<a href="{PHONE_HREF}">{PHONE}</a>'),
    ], kumar_text, f"Kumar Bhandari - {FIRM}",
        f"Meet Kumar Bhandari, CPA, founder of {FIRM}. Kumar has 18+ years of tax, accounting, auditing, and consulting experience. Get to know him.")

    manoj_text = paras("""
Manoj serves in the firm as Accounting Consultant since 2015. In that role, he oversees the delivery of all aspects of the firm’s tax and accounting services. Manoj has extensive experience in bookkeeping, processing payroll, and preparing tax returns. He received his Master of Business Administration degree from Jacksonville State University, Alabama.""")
    manoj_text = manoj_text.replace("<p>", '<p class="article__lede" style="margin-bottom:0">', 1)
    bio_page("manoj-silwal.html", "Manoj Silwal MBA", "Accounting Consultant", None, [
        ("Role", "Accounting Consultant"),
        ("With the firm since", "2015"),
        ("Education", "Master of Business Administration, Jacksonville State University, Alabama"),
    ], manoj_text, f"Manoj Silwal - {FIRM}",
        f"Meet Manoj Silwal, MBA, an accounting consultant at {FIRM}. Manoj has been with the firm since 2015. He looks forward to working with you.")

    # The live page has only her name (and the placeholder "Title"); checklist: title and headshot to come
    bio_page("deborah-thomas.html", "Deborah Thomas", "", None, [], "", f"Deborah Thomas - {FIRM}",
             f"Meet Deborah Thomas at {FIRM}.")


def build_why_best():
    pillars = [
        ("Our Mission", f"{FIRM} strives to give you proactive advice and safe tax strategies to help you and your business grow and keep more of what you earn."),
        ("Our Philosophy", "We help businesses fulfill their responsibilities and build better tomorrows by providing tax and accounting services that assist in reducing risk and increasing assets. Our culture is based on an unwavering belief in integrity and fair dealings, treating our clients and each other with dignity and respect as we strive for excellence!"),
        ("Our Promise", f"At {FIRM}, we will treat your business with the care and diligence it deserves with the goal of doing our part to help you achieve your business goals. Our clients are part of our family."),
    ]
    cards = "".join(f'<article class="pillar" data-reveal><span class="pillar__num">{i + 1:02d}</span><h3>{e(t)}:</h3><p>{e(p)}</p></article>'
                    for i, (t, p) in enumerate(pillars))
    body = page_hero("Why We're The Best", None, None, "page-why-best.jpg",
                     [("About Us", "firm-background.html"), ("Why We're The Best", None)])
    body += f'''
<section class="section section--ivory">
  <div class="container"><div class="pillars" data-stagger="0.12">{cards}</div></div>
</section>'''
    write_page("about-us/why-were-the-best.html", f"{FIRM} - Why Choose Us",
               f"Wondering why you should choose {FIRM}? Discover our mission, our philosophy, and why our clients think we're the best.",
               body, og_img="page-why-best.jpg")


def build_referrals():
    great = [
        "Business owners who want consistent bookkeeping, accurate financials, and better tax outcomes",
        "Medical offices, law firms, retail businesses, restaurants, and real estate professionals seeking industry-specific guidance",
        "High-net-worth individuals looking for advanced tax strategies and year-round support",
        "Professionals and entrepreneurs who need a proactive advisor—not just a tax preparer",
    ]
    expect = [
        "Proactive tax planning designed to reduce liability and increase savings",
        "Accurate, timely accounting and bookkeeping",
        "Payroll and compliance support that keeps operations running smoothly",
        "Advisory and part-time CFO services for clients focused on scaling their business",
        "A strategic, year-round relationship through our signature tax-strategy engagement",
    ]
    ul = lambda items: "<ul>" + "".join(f"<li>{e(t)}</li>" for t in items) + "</ul>"
    body = page_hero("We Love Referrals", None, None, "page-referrals.jpg", [("About Us", "firm-background.html"), ("Referrals", None)])
    body += f'''
<section class="section">
  <div class="container article">
    <div class="prose" data-reveal>
      <p class="article__lede">At {e(FIRM)}, we believe strong relationships are the foundation of exceptional service. Many of our best clients come from trusted referrals—professionals and community partners who value proactive tax planning, accurate accounting, and transparent financial guidance. If you know someone who could benefit from strategic tax support or reliable business accounting, we would be honored to help.</p>
      <p>Our firm, led by Kumar Bhandari, CPA, PFS, and Master of Taxation, serves small to mid-sized businesses, professionals, and high-net-worth individuals seeking clarity, compliance, and long-term financial strategy. From tax preparation and payroll to bookkeeping and part-time CFO services, we provide a comprehensive suite of solutions tailored to each client’s goals and industry.</p>
      <h3>Who Makes a Great Referral?</h3>
      <p>We welcome introductions to:</p>
      {ul(great)}
      <p>If your contact values communication, education, and long-term planning, they’ll fit in perfectly with our firm’s approach.</p>
      <h3>What Your Referral Can Expect</h3>
      <p>Your referrals receive the same level of care, transparency, and expertise you’ve come to know. Our team provides:</p>
      {ul(expect)}
      <p>Every client receives a personalized onboarding experience and clear, ongoing communication. Our goal is to create long-term partnerships built on trust, clarity, and measurable financial improvement.</p>
      <h3>How to Send a Referral</h3>
      <p>Referring someone is simple. Share their contact information with us, or send them directly to our website to schedule a consultation. You may also introduce us via email—whatever is easiest for you and your referral.</p>
      <h3>Thank You for Your Trust</h3>
      <p>We truly appreciate every referral and the confidence you place in us. If you have someone in mind, we look forward to helping them achieve greater clarity, better financial outcomes, and long-term peace of mind.</p>
    </div>
    {aside(ABOUT_LINKS, "about-us/referrals.html", "About Us")}
  </div>
</section>
<section class="section section--ivory" id="referral-form">
  <div class="container contact-grid">
    <div>
      <h2 data-split>Help Your Friends, Family, and Colleagues Discover <em>Exceptional Financial Services</em></h2>
      <div class="prose" data-reveal style="--d:.2s;margin-top:28px">
        <p>Thank you for considering referring a friend or colleague to {e(FIRM)} tax and accounting services. Your recommendation means a great deal to us, as we take client satisfaction seriously.</p>
        <p>Please fill out the form with your contact's information, and we'll reach out to them promptly. Rest assured, we value privacy and confidentiality. All personal information will be handled with the utmost care.</p>
      </div>
    </div>
    <form class="form-card" data-cw-form="referral" novalidate data-reveal="right">
      <h3 style="margin-bottom:24px">Please fill out the form details.</h3>
      <div class="form-grid">
        {field("r-first", "Your First Name", required=True, autocomplete="given-name")}
        {field("r-last", "Your Last Name", required=True, autocomplete="family-name")}
        {field("r-email", "Your Email", "email", required=True, autocomplete="email")}
        {field("r-phone", "Your Phone Number", "tel", autocomplete="tel")}
        {field("r-ref-first", "Referral's First Name", required=True)}
        {field("r-ref-last", "Referral's Last Name", required=True)}
        {field("r-ref-email", "Referral's Email Address", "email", required=True)}
        {field("r-ref-phone", "Referral's Phone Number", "tel")}
        {field("r-notes", "Additional Notes or Comments", full=True, textarea=True)}
        <p class="form-legal full">{LEGAL_SUBMIT}</p>
        <label class="check full"><input type="checkbox" name="sms_consent"><span>I consent to receive SMS messages and agree with the <a href="{href("terms-of-service.html")}">Terms of Service</a>.</span></label>
        <div class="form-actions full"><button class="btn" type="submit">Submit {I["arrow"]}</button></div>
      </div>
    </form>
  </div>
</section>'''
    write_page("about-us/referrals.html", f"{FIRM} - Referral Policy",
               f"At {FIRM}, we believe strong relationships are the foundation of exceptional service. Discover our referral policy and form here.",
               body, og_img="page-referrals.jpg")


FAQS = [
    (f"What tax and accounting services does {FIRM} provide?",
     f"{FIRM} offers a full suite of services for individuals and businesses, including tax preparation, proactive tax planning, bookkeeping, accounting, payroll, virtual bookkeeping, virtual tax preparation, and part-time CFO services. We serve small to mid-sized businesses, high-net-worth individuals, and professionals across industries such as medical, legal, real estate, retail, restaurants, and automotive. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm brings advanced expertise and strategic guidance to support long-term growth."),
    (f"Why choose {FIRM} for tax preparation and planning in Alpharetta?",
     "Clients choose our firm because we provide proactive, education-first tax strategy—not just once-a-year filing. Our signature annual tax-strategy engagement includes monthly or quarterly meetings and unlimited support, ensuring you stay ahead of changes throughout the year. With deep experience serving professionals, real estate investors, and high-net-worth individuals, we help you reduce liability, avoid surprises, and make informed decisions."),
    ("How does your tax planning benefit small businesses in Georgia?",
     "Small businesses in Georgia often face complex tax considerations—entity structure, payroll tax, estimated payments, and industry-specific deductions. We provide year-round planning that aligns with your revenue cycles, financial goals, and industry. Whether you operate a medical practice, law firm, retail store, or restaurant, we help you optimize deductions, improve forecasting, and strengthen long-term tax efficiency."),
    ("Do you offer virtual services for clients outside Alpharetta?",
     f"Yes. {FIRM} provides Virtual Bookkeeping and Virtual Tax Preparation, allowing clients across Georgia and beyond to receive the same level of expert support. Our secure systems enable document uploads, e-signatures, and real-time communication, making it easy to complete your tax or accounting engagement from anywhere."),
    ("What tax deductions are available for professionals in Georgia?",
     "Many Georgia professionals—physicians, attorneys, consultants, real estate agents, and entrepreneurs—qualify for deductions related to home offices, continuing education, supplies, software, mileage, retirement contributions, and more. During your planning sessions, we evaluate eligible deductions based on your work structure and create a proactive strategy tailored to your needs."),
    ("How can bookkeeping and accounting help my Alpharetta business grow?",
     "Accurate bookkeeping gives business owners clarity. Our accounting services provide organized financials, monthly reports, cash flow reviews, and industry-specific guidance. This helps you make informed decisions, maintain compliance, and understand trends affecting profitability. We also integrate your bookkeeping with tax planning to ensure every financial move supports long-term goals."),
    (f"What industries does {FIRM} specialize in?", None),
    ("What happens if I get audited?",
     "If the IRS contacts you, we can guide you through the entire process—from document requests to resolution. Our team reviews your records, prepares responses, and represents your interests professionally. With our proactive planning and clean documentation, most clients experience smooth, efficient outcomes."),
    ("Do I need a part-time CFO for my business?",
     "If you’re growing, managing cash flow challenges, preparing for expansion, or need deeper financial insight, a part-time CFO can provide strategic direction without the cost of a full-time executive. Our CFO services include budgeting, forecasting, financial analysis, and operational guidance designed to support business scalability."),
]
FAQ_INDUSTRIES = ["Healthcare &amp; Medical (Medical Office Accounting Alpharetta)", "Law Firms (Law Office Tax Services Alpharetta)",
                  "Real Estate Professionals", "Restaurants &amp; Hospitality", "Retail Businesses", "High-Net-Worth Individuals", "Car Dealerships"]
FAQ_INDUSTRIES_TEXT = "Each industry benefits from tailored accounting systems, customized reporting, and advanced tax strategies."


def build_faq():
    items, ld_items = [], []
    for q, a in FAQS:
        if a is None:
            answer_html = ("<p>We serve a diverse range of industries, including:</p><ul>" +
                           "".join(f"<li>{t}</li>" for t in FAQ_INDUSTRIES) + f"</ul><p>{FAQ_INDUSTRIES_TEXT}</p>")
            plain = "We serve a diverse range of industries, including: " + "; ".join(html.unescape(t) for t in FAQ_INDUSTRIES) + ". " + FAQ_INDUSTRIES_TEXT
        else:
            answer_html, plain = f"<p>{e(a)}</p>", a
        items.append(f'<details class="faq-item" data-reveal><summary>{e(q)}<span class="faq-item__icon">{I["plus"]}</span></summary>'
                     f'<div class="faq-item__body"><div class="prose">{answer_html}</div></div></details>')
        ld_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain}})
    body = page_hero("Frequently Asked Questions", None, None, None, [("About Us", "firm-background.html"), ("FAQ", None)])
    body += f'''
<section class="section">
  <div class="container container--narrow"><div class="faq-list" data-stagger="0.05">{"".join(items)}</div></div>
</section>''' + cta_band("Still Have Questions?",
                         f"We’re here to help. Whether you need proactive tax planning, reliable bookkeeping, or expert advisory services, {FIRM} is your trusted partner in Alpharetta, GA. Contact us today to schedule a consultation and get the clarity and strategy you deserve.")
    write_page("about-us/faq.html", f"{FIRM} - FAQ",
               f"{FIRM} answers frequently asked questions. Contact us at {PHONE} if you need more information.",
               body, ld=[{"@type": "FAQPage", "mainEntity": ld_items}])


def build_privacy():
    body = page_hero("Privacy Policy", None,
                     f"{e(FIRM)} focuses on implementing fair information practices that are designed to protect your privacy.",
                     "page-privacy.jpg", [("About Us", "firm-background.html"), ("Privacy Policy", None)])
    body += f'''
<section class="section">
  <div class="container article">
    <div class="prose" data-reveal>
      <p class="article__lede">You may have some concerns about the confidentiality of the information you provide to this office. It is our policy to keep your personal and business matters confidential to the extent permitted by law.</p>
      <h3>Client Information, Privacy Policies and Notice Regarding Advisor-Client Privileged Communications</h3>
      <p>The Federal Trade Commission has issued regulations that require tax preparation firms to provide an annual statement of firm privacy policies. Here is our policy:</p>
      <p>We handle all information you provide us with the utmost confidentiality. Your personal information will only be shared with members of our firm who need to know this information in order to complete the work you have hired our firm to do. We will not disclose your personal information to anyone outside our firm without your express written permission to do so, or unless we are legally required to do so. For example, if a mortgage lender contacts our office for a copy of your return or information about it, we will ask that you provide written permission prior to our responding to that request.</p>
      <p>You should also be aware that anything you tell us during the interview for the preparation of your tax return is confidential, but not protected from the IRS. Privileged communications (those that are protected from IRS authority to compel our testimony) are limited to non-criminal tax advice on matters before the IRS or non-criminal tax proceedings in federal courts. Although we consider any information you provide us as confidential, return preparation engagements are not covered by advisor-client privilege.</p>
      <p>If you feel the nature of any subject matter to be discussed requires protected communications, please raise that issue so that we can discuss your possible need to consult with an attorney for legal advice.</p>
    </div>
    {aside(LEGAL_LINKS, "firm-background/privacy-policy.html", "")}
  </div>
</section>'''
    write_page("firm-background/privacy-policy.html", f"Privacy Policy - {FIRM}",
               f"It is {FIRM}'s policy to keep your personal and business matters confidential to the extent permitted by law in Georgia.",
               body, og_img="page-privacy.jpg")


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
SERVICES_INDEX = [
    ("Tax Services", "Tax Preparation &amp; Planning", "svc-tax-strategy.webp", SERVICE_LINKS[0][1]),
    ("For Business", "Accounting &amp; Bookkeeping", "svc-accounting.webp", SERVICE_LINKS[1][1]),
    ("For Business", "Fractional CFO", "svc-cfo.webp", SERVICE_LINKS[2][1]),
    ("For Business", "Payroll", "svc-payroll.webp", SERVICE_LINKS[3][1]),
    ("For Business", "Virtual Bookkeeping", "svc-virtual-bookkeeping.webp", SERVICE_LINKS[4][1]),
    ("Tax Services", "Virtual Tax Preparation", "svc-virtual-tax.webp", SERVICE_LINKS[5][1]),
]


def build_services_index():
    cards = "".join(f'''
    <a class="svc-card" href="{href(p)}" data-reveal>
      <div class="svc-card__media"><img src="@/assets/img/{img}" alt="" loading="lazy"></div>
      <div class="svc-card__body"><span class="svc-card__tag">{tag}</span><h3>{t}</h3><span class="svc-card__go" aria-hidden="true">{I["arrow"]}</span></div>
    </a>''' for tag, t, img, p in SERVICES_INDEX)
    body = page_hero("What We Offer", "Services",
                     f"{e(FIRM)} gives business owners a full range of accounting and tax services. We care about your financial success!",
                     None, [("Services", None)])
    body += f'''
<section class="section section--ivory">
  <div class="container"><div class="card-grid" data-stagger="0.1">{cards}</div></div>
</section>'''
    write_page("services.html", f"{FIRM} - What We Offer",
               f"Based in Alpharetta, Georgia, {FIRM} gives individuals and business owners a full range of tax and accounting services. Learn more.",
               body, og_img="svc-tax-strategy.webp")


def detail_page(path, section, section_links, title, tagline, image, text, meta_title, meta_desc, section_crumb):
    blocks = [b.strip() for b in text.strip().split("\n\n")]
    lede = f'<p class="article__lede">{blocks[0]}</p>'
    rest = "".join(f"<p>{b}</p>" for b in blocks[1:])
    body = page_hero(html.unescape(title), None, e(tagline) if tagline else None, image,
                     [section_crumb, (html.unescape(title), None)], title_html=title)
    body += f'''
<section class="section">
  <div class="container article">
    <article class="prose" data-reveal>{lede}{rest}</article>
    {aside(section_links, path, section)}
  </div>
</section>'''
    ld = [{"@type": "Service", "name": html.unescape(title), "provider": {"@id": LIVE + "/#firm"},
           "areaServed": "US", "url": live_url(path), "description": html.unescape(meta_desc)}]
    write_page(path, meta_title, meta_desc, body, og_img=image, ld=ld)


SERVICE_PAGES = [
    ("services/tax-preparation-planning.html", "Tax Preparation &amp; Planning",
     "Preparing and planning for taxes is often a stressful and complicated endeavor for most people", "page-tax-prep.jpg",
     f"""At {FIRM}, we offer strategic, education-driven tax preparation and planning services designed to help you reduce liability, stay compliant, and build long-term financial confidence. Led by Kumar Bhandari—a CPA, Personal Financial Specialist (PFS), and Master of Taxation—our firm brings advanced expertise and industry-focused insight to individuals and businesses seeking more than a once-a-year tax filing.

We take a proactive approach to tax strategy. Instead of reacting to past transactions, we help you plan ahead—reviewing income, deductions, entity structure, investments, and future goals to uncover savings opportunities before deadlines arrive. Through our signature annual tax-strategy engagement, clients receive ongoing guidance with monthly or quarterly meetings and unlimited tax support. This ensures you always understand your tax position and can make informed decisions throughout the year.

Our team works closely with small to mid-sized businesses, real estate professionals, medical practices, law firms, retail shops, restaurants, and car dealerships. Each industry faces unique tax challenges, and we tailor our planning to match your operational needs, cash-flow realities, and long-term growth plans. For professionals and entrepreneurs, we provide tax planning that supports accurate forecasting, smoother financial operations, and fewer surprises at year-end.

High-net-worth individuals rely on {FIRM} for advanced planning that addresses multistate filings, investment income, trust considerations, wealth preservation, and generational tax strategy. With a deep background in complex taxation, our firm helps you protect more of what you’ve earned while aligning your tax plan with your broader financial goals.

Our tax preparation process is thorough, accurate, and built on communication. We use a detailed review system to ensure every return is prepared correctly the first time. With a focus on technology, organization, and compliance, we make filing seamless—whether you prefer in-office or virtual support.

When you choose {FIRM}, you get more than a tax preparer— you gain a partner dedicated to strategy, clarity, and long-term financial success. If you’re ready to move from reactive filing to proactive planning, schedule a consultation today and experience the difference an expert tax strategy can make.""",
     f"Tax Preparation & Planning - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, we offer strategic, education-driven tax preparation and planning services designed to help you reduce liability, stay compliant, and more."),
    ("services/accounting-bookkeeping.html", "Accounting &amp; Bookkeeping", "Small business accounting made easy", "page-accounting.webp",
     f"""At {FIRM}, our Accounting &amp; Bookkeeping services are built to give business owners accurate financials, better insights, and complete confidence in their day-to-day operations. Whether you run a medical practice, law firm, retail store, restaurant, real estate business, or automotive dealership, you deserve organized books and reliable financial reporting that support smarter, faster decision-making.

Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our team combines technical expertise with a practical, business-owner mindset. We manage your financial data with precision, ensuring your books stay current, compliant, and aligned with your tax and operational needs. From daily transaction management to monthly financial statements, we bring the clarity and structure that growing businesses rely on.

Our bookkeeping services include account reconciliation, expense categorization, payroll record tracking, vendor and receivable management, and preparation of clean financial reports. We also support clients using QuickBooks and other accounting platforms, helping streamline workflows and maintain consistency across systems. For businesses seeking additional advisory support, our team provides deeper analysis, budgeting guidance, and insight into trends affecting cash flow and profitability.

Because we work closely with small to mid-sized businesses, we understand the pressures of managing finances while running operations. Whether you’re scaling, stabilizing, or preparing for long-term growth, our accounting solutions adapt to your goals. We also integrate tax planning into your monthly bookkeeping, helping prevent surprises and ensuring your records fully support your tax strategy.

Industry-specific experience sets our firm apart. We understand the complexities of Medical Office Accounting, Law Office financials, Restaurant bookkeeping, Real Estate reporting, and Retail and Car Dealership accounting requirements. This allows us to provide not just numbers, but meaningful context that helps you make informed business decisions.

With {FIRM}, you receive accurate financials, responsive communication, and a team dedicated to supporting your success year-round. If you’re ready to eliminate bookkeeping stress and gain financial clarity, contact us today to learn how our Accounting &amp; Bookkeeping services can help your business operate with confidence and control.""",
     f"Accounting & Bookkeeping - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, our accounting & bookkeeping services are built to give business owners accurate financials, better insights, and complete confidence."),
    ("services/part-time-cfo.html", "Fractional CFO Services",
     "We make sure that our role as part-time chief financial officer translates into full-time confidence", "page-cfo.webp",
     f"""At {FIRM}, our Part-Time CFO Services provide growing businesses with high-level financial leadership—without the cost of a full-time executive. Designed for small to mid-sized companies that need strategic guidance, budgeting support, and forward-looking financial analysis, our services help you make confident decisions rooted in accurate data and clear projections. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, we deliver expert insight backed by years of specialized tax and accounting knowledge.

Many businesses reach a stage where bookkeeping and basic accounting are no longer enough. You may need help understanding cash flow trends, evaluating profitability, or preparing for expansion. Our Part-Time CFO solution fills that gap by offering strategic planning, financial oversight, and structured analysis at a fraction of the cost of hiring internally.

Our services include cash flow management, budget development, forecasting, financial statement interpretation, and performance metrics that highlight your business’s financial health. We help you identify opportunities for growth, reduce inefficiencies, and understand how operational decisions impact long-term profitability. For businesses preparing for lending, investment, or future scaling, we also support financial modeling and preparation of lender-ready packages.

Industry-specific insight strengthens our guidance. Whether you lead a medical office, law firm, restaurant, real estate company, or retail business, you benefit from a deep understanding of the financial pressures and tax challenges inside your sector. Our advisory approach blends technical strategy with real-world business practicality, helping you navigate decisions with confidence.

What makes our CFO service unique is its integration with tax planning. Because we already manage your accounting and understand your tax structure, our recommendations are fully aligned with both your day-to-day operations and long-term goals. This ensures more accurate planning, better forecasting, and fewer financial surprises.

With {FIRM}, you gain a strategic partner—not just a financial technician. We provide clarity, proactive guidance, and consistent communication that help you stay ahead of challenges and capitalize on opportunities. If your business is ready for expert financial direction without the commitment of a full-time hire, contact us today to learn how our Part-Time CFO Services can support your growth and success.""",
     f"Part-Time CFO - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, our part-time CFO services provide growing businesses with high-level financial leadership, without the cost of a full-time executive."),
    ("services/payroll.html", "Payroll", "We can simplify the payroll process for you", "page-payroll.jpg",
     f"""At {FIRM}, our Payroll Services are designed to make paying your employees simple, accurate, and fully compliant. For many small to mid-sized businesses, payroll is one of the most time-consuming and high-risk administrative tasks. With changing tax rules, filing deadlines, and employee requirements, it only takes one mistake to create costly penalties or employee frustration. Our team ensures your payroll processes run smoothly so you can focus on running your business—not managing calculations and compliance.

Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, {FIRM} provides a secure, streamlined payroll solution that integrates seamlessly with your accounting system. We manage payroll processing, tax withholdings, direct deposits, quarterly and annual payroll filings, W-2 and 1099 preparation, and compliance with federal and state regulations. Whether you have two employees or an entire team, our service ensures every payment is accurate and on time.

We understand the challenges faced by medical offices, law firms, retail shops, restaurants, real estate professionals, and service-based businesses. Each industry has specific payroll needs—from wage structures and tipped employee reporting to contractor payments and multistate requirements. Our experience in these sectors allows us to customize payroll support that aligns with your operational structure and tax obligations.

Beyond basic processing, we offer payroll reporting that helps you understand labor costs, staffing trends, and cash flow impact. This insight supports better decision-making and provides a stronger foundation for financial planning. Because our payroll services are integrated with your bookkeeping and tax strategy, we ensure accuracy across your entire financial system—from employee records to year-end filings.

Our clients choose {FIRM} because they want reliability, expertise, and clear communication. We prioritize accuracy, compliance, and responsiveness, making payroll worry-free and efficient. With secure systems, meticulous processes, and experienced oversight, we deliver the peace of mind business owners need.

If you’re ready to eliminate payroll stress, reduce risk, and ensure compliance at every level, {FIRM} is here to help. Contact us today to learn how our Payroll Services can support your business with confidence and consistency.""",
     f"Payroll - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, our payroll services are designed to make paying your employees simple, accurate, and fully compliant. Learn how we can help."),
    ("services/virtual-bookkeeping.html", "Virtual Bookkeeping", "We take care of the bookkeeping so that you don’t have to.", "page-virtual-bookkeeping.webp",
     f"""At {FIRM}, our Virtual Bookkeeping services give businesses a modern, efficient, and secure way to manage their financial records from anywhere. With a focus on accuracy, communication, and year-round support, we help business owners stay organized, compliant, and confident in their financial decision-making. Whether you operate a medical practice, law firm, retail store, restaurant, real estate business, or service-based company, our virtual system ensures your books stay current—without the need for on-site staff or outdated paperwork.

Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our team blends traditional accounting expertise with today’s best cloud-based tools. We manage daily transactions, reconciliations, expense tracking, vendor and receivable management, and monthly financial statements—all through a streamlined virtual platform. This approach gives you real-time access to accurate financial data while freeing your team from administrative burdens.

Because every business has different workflow preferences, we set up systems that work seamlessly with your existing processes and software. We support QuickBooks Online and other leading accounting platforms, making it easy to stay organized whether you’re in the office or on the go. Our secure digital tools protect your information and maintain clear communication through every step of the process.

What sets our virtual bookkeeping apart is its integration with tax planning and advisory services. Instead of simply recording transactions, we provide context and insight—helping you understand trends in cash flow, profitability, and expenses. This allows you to make informed decisions and stay prepared for tax season long before deadlines approach.

Industry-specific experience also plays a role in our accuracy and efficiency. We understand the reporting requirements and operational challenges of medical offices, legal practices, restaurants, real estate professionals, retailers, and car dealerships. This allows us to categorize financial activity correctly and provide reporting that fits your needs.

With {FIRM}, virtual bookkeeping is more than data entry—it’s a reliable, strategic partnership that helps your business stay organized and grow with clarity. If you’re ready for a streamlined, modern bookkeeping solution, contact us today to learn how our Virtual Bookkeeping services can support your success year-round.""",
     f"Virtual Bookkeeping - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, our virtual bookkeeping services give businesses a modern, efficient, and secure way to manage finances in Alpharetta or anywhere."),
    ("services/virtual-tax-preparation.html", "Virtual Tax Preparation", "Say goodbye to your paperwork", "page-virtual-tax.webp",
     f"""At {FIRM}, our Virtual Tax Preparation services offer a secure, convenient, and highly efficient way to manage your taxes from anywhere. Designed for busy professionals, business owners, and high-net-worth individuals, our virtual process combines advanced technology with the expertise of Kumar Bhandari, CPA, PFS, and Master of Taxation, ensuring accurate filings and proactive tax strategy without the need for in-person appointments.

Our virtual system makes tax preparation simple. From secure document upload portals to electronic signatures and real-time communication, we streamline every step while maintaining the highest level of privacy and compliance. Whether you're at home, traveling, or managing multiple business locations, you can complete your entire tax engagement with ease and confidence.

What sets our virtual tax services apart is our emphasis on strategy—not just filing. Before preparing your return, we analyze your financial picture, identify deductions and credits, and look for opportunities to reduce liability. Business owners benefit from tax planning tailored to their industry, entity structure, and long-term goals, while individuals receive guidance that aligns with income sources, investments, and future financial plans.

We work closely with small to mid-sized businesses, real estate professionals, medical practices, law firms, restaurants, and retail operations. Because we understand industry-specific tax rules and reporting requirements, our virtual process maintains the same level of accuracy and insight as an in-office engagement—just with more flexibility.

High-net-worth individuals rely on our virtual services for multistate filings, investment income reporting, trust considerations, and advanced planning that supports wealth preservation. With unlimited support through our annual tax-strategy engagement, we remain accessible throughout the year to answer questions and help you plan ahead.

Our clients choose {FIRM} because they want a modern, reliable, and expert-led tax experience. Whether you prefer remote convenience or simply need a more efficient solution, our virtual process ensures accurate results, clear communication, and a proactive approach to your tax health.

If you’re ready for a secure, streamlined alternative to traditional tax preparation, contact {FIRM} today to learn how our Virtual Tax Preparation services can help you file with confidence and strategy.""",
     f"Virtual Tax Preparation - Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, our virtual tax preparation services give businesses a modern, efficient, and secure way to manage finances in Alpharetta or anywhere."),
]


INDUSTRY_PAGES = [
    ("industries/healthcare-and-medical-accounting-services.html", "Healthcare and Medical",
     "Our professionals are focused on helping your healthcare organization succeed.", "page-healthcare.webp",
     f"""At {FIRM}, we provide specialized accounting and tax services tailored to the unique needs of healthcare and medical professionals. From solo practitioners to multi-provider clinics, medical office administrators trust our expertise to keep their financial systems accurate, compliant, and strategically aligned with their long-term goals. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm understands the complexities and regulatory demands that come with running a healthcare practice.

Medical practices face daily operational pressures—patient care, staffing, billing, compliance management, and more. With so many responsibilities, financial oversight often becomes reactive instead of strategic. Our Healthcare &amp; Medical Accounting services are designed to change that. We provide proactive financial structure, tax planning, and consistent reporting so you can make informed decisions and stay focused on patient care.

Our team manages bookkeeping, payroll for medical staff, practice financial statements, chart of accounts optimization, budgeting, and cash flow monitoring. We help practice owners understand overhead, profitability, and reimbursement trends while creating processes that support smoother daily operations. For growing practices, we assist with financial modeling, expansion planning, and evaluating the impact of adding new providers or services.

Tax planning is a critical part of our support. Medical professionals often face complex tax scenarios, including specialized deductions, equipment purchases, multi-entity structures, and retirement strategies. Through our annual tax-strategy engagement—with monthly or quarterly meetings and unlimited tax support—we ensure every decision is aligned with a long-term tax plan. This approach helps reduce liability, prevent surprises, and maximize financial efficiency year-round.

We serve a wide range of healthcare clients, including physicians, dentists, nurse practitioners, therapists, chiropractors, and specialty clinics. Our industry-specific experience allows us to categorize expenses properly, understand reimbursement cycles, and provide clear financial insights that general accounting firms often miss.

With {FIRM}, you gain a strategic financial partner who brings clarity, structure, and proactive planning to your medical practice. If you’re ready to strengthen your financial systems, improve tax outcomes, and gain deeper visibility into your practice’s performance, contact us today to learn how our Healthcare &amp; Medical Accounting services can help you achieve long-term success.""",
     f"Healthcare and Medical Accounting in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting and tax services tailored to the unique needs of healthcare and medical professionals. Learn more."),
    ("industries/high-net-worth-services.html", "High Net Worth Services",
     "Comprehensive tax and financial solutions for busy high net worth individuals and families", "page-hnw.webp",
     # checklist: "financial advisors" replaced with "financial professionals" (restricted term)
     f"""At {FIRM}, we provide sophisticated tax planning and advisory services tailored to the needs of high-net-worth individuals and families. With complex financial structures, multi-source income, and long-term wealth strategies, affluent clients require more than basic tax preparation—they need a partner who understands how to optimize tax outcomes while protecting and preserving wealth. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm offers the advanced expertise necessary to navigate high-level tax challenges with clarity and precision.

As your wealth grows, so does the complexity of your tax picture. Investments, real estate holdings, business ownership, trusts, philanthropic giving, retirement structures, and multistate filing requirements all contribute to a need for strategic, year-round planning. Our annual tax-strategy engagement includes monthly or quarterly meetings and unlimited tax support, ensuring your plan evolves with your goals and circumstances.

We take a proactive approach, analyzing income flow, entity structures, capital gains exposure, estate considerations, and tax-efficiency opportunities across all areas of your financial life. Our team identifies strategies that minimize liability, support wealth preservation, and align with long-term legacy planning. Whether you are preparing for a liquidity event, expanding your real estate portfolio, or managing multiple business ventures, we provide guidance rooted in deep technical expertise.

High-net-worth individuals benefit from our ability to coordinate with financial professionals, attorneys, wealth managers, and estate planning professionals. This collaborative approach ensures your tax strategy remains fully integrated with your broader financial plan. We also provide advisory support for trust taxation, gifting strategies, and generational wealth transfer.

Our clients include executives, physicians, attorneys, real estate investors, entrepreneurs, and family business owners. Each client receives personalized attention, ongoing communication, and a detailed strategic plan designed to reduce taxes while supporting long-term financial success.

When you work with {FIRM}, you gain a trusted advisor focused on protecting your wealth with forward-thinking tax planning and meticulous preparation. If you’re ready to strengthen your financial strategy and reduce tax exposure with expert guidance, contact us today to learn how our High-Net-Worth Individual Tax Services can help you achieve clarity, stability, and lasting financial confidence.""",
     f"High Net Worth Services in Alpharetta, Georgia | {FIRM}",
     f"At {FIRM}, we provide sophisticated tax planning and advisory services tailored to the needs of high-net-worth individuals and families."),
    ("industries/law-firm-business-and-accounting-services.html", "Law Firms",
     "The right business and accounting firm can boost your law firm’s bottom line.", "page-law.webp",
     f"""At {FIRM}, we provide specialized accounting and tax services designed to meet the unique needs of law firms and legal professionals. Attorneys operate in a fast-paced environment where accuracy, compliance, and financial clarity are essential—not only for firm stability but also for client trust. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm delivers the advanced expertise and industry-specific insight law practices need to operate efficiently and profitably.

Law firms face distinct financial challenges, including trust accounting requirements, irregular cash flow cycles, partner compensation structures, case-related expenses, and multistate tax considerations. We understand these complexities and provide the structure, guidance, and proactive planning necessary to keep your financial systems compliant and optimized.

Our services include bookkeeping and financial reporting tailored to legal workflows, trust account reconciliation, payroll for attorneys and staff, expense and retainer tracking, budgeting, and partner profit distribution analysis. We help firms maintain clean, accurate books that support better decisions, reduce risk, and streamline daily operations—allowing attorneys to focus on serving clients rather than managing finances.

Tax planning plays a central role in our support for law firms. From entity selection and restructuring to deductions for professional expenses, retirement planning, and income allocation strategies, our team identifies opportunities that minimize liability while aligning with your long-term goals. Through our annual tax-strategy engagement, you benefit from monthly or quarterly planning sessions and unlimited access to expert support, ensuring that your tax strategy stays ahead of changing circumstances.

We work with law firms of all sizes, including solo practitioners, boutique practices, and multi-attorney firms across specialties such as litigation, family law, real estate law, corporate law, immigration, and estate planning. Our understanding of legal-industry requirements allows us to provide meaningful insights into profitability, overhead management, and long-term financial health.

With {FIRM}, you gain a strategic accounting partner who understands the pressures and priorities of legal practice. If you’re ready to improve compliance, strengthen your financial systems, and build a proactive tax strategy, contact us today to learn how our specialized Accounting &amp; Tax Services for Law Firms can support your firm’s success.""",
     f"Law Firm Accounting in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting and tax services designed to meet the unique needs of law firms and legal professionals. Learn more."),
    ("industries/accounting-and-tax-for-real-estate-agents.html", "Real Estate",
     "A comprehensive tax strategy that maximizes profits while minimizing tax liabilities", "page-realestate.webp",
     f"""At {FIRM}, we provide specialized accounting, bookkeeping, and tax planning services tailored to the unique needs of real estate investors, agents, brokers, developers, and property managers. Real estate is an industry with complex financial structures, ongoing transactions, and high-value tax considerations—making accurate records and strategic planning essential. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm offers the advanced expertise needed to help real estate professionals maximize profitability and reduce tax exposure.

The real estate industry is filled with moving parts: rental income, commissions, capital improvements, depreciation schedules, 1031 exchanges, passive activity rules, entity structuring, and multistate reporting. Managing these components requires more than basic accounting. We help clients stay organized, compliant, and tax-efficient throughout every stage of their investment or business cycle.

Our services include industry-specific bookkeeping, cash flow tracking, property-level financials, expense categorization, payroll, and monthly reporting. We also assist clients with evaluating investment performance, understanding tax implications of acquisitions and sales, and optimizing cost recovery through depreciation strategies. Whether you manage multiple properties or operate as an independent agent, we ensure your financial foundation is strong and accurate.

Tax planning is central to our real estate support. We analyze your portfolio, entity structure, timing of sales, passive income rules, and investment strategy to identify opportunities for tax savings. From 1031 exchange planning to capital gains strategies and short-term vs. long-term rental taxation rules, our guidance is designed to increase after-tax returns. Through our annual tax-strategy engagement, clients benefit from monthly or quarterly planning meetings and unlimited tax support, ensuring constant alignment with financial goals.

We work with residential and commercial investors, real estate agents and brokers, developers, flippers, syndicators, landlords, and property managers. Our insights are rooted in real-world experience and a deep understanding of the financial patterns unique to the real estate sector.

With {FIRM}, you gain more than an accountant—you gain a strategic partner who helps you build, manage, and grow your real estate wealth with clarity and confidence. If you're ready to strengthen your financial strategy and improve profitability, contact us today to learn how our Real Estate Accounting &amp; Tax Services can support your success.""",
     f"Real Estate Accounting in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting, bookkeeping, and tax planning services tailored to the unique needs of real estate investors and agents."),
    ("industries/restaurants.html", "Restaurants", "Food Service Industry", "page-restaurants.jpg",
     f"""At {FIRM}, we provide specialized accounting, bookkeeping, and tax services designed to support the fast-paced and detail-driven restaurant industry. From family-owned eateries to multi-location establishments, restaurant owners face unique financial challenges—tight margins, fluctuating labor costs, inventory management, sales tax compliance, and complex reporting needs. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm delivers the expertise and structure that restaurant operators need to run a profitable, compliant, and efficient business.

Restaurants often operate on thin margins, making accurate accounting and proactive planning essential. Our team provides industry-specific bookkeeping, chart of accounts setup, daily transaction recording, payroll management, tip reporting, vendor tracking, and detailed financial statements that highlight labor, food cost, and overhead trends. This helps owners make informed decisions that improve cost control and profitability.

We understand the operational pressures of the restaurant industry—busy service hours, staff turnover, and unpredictable cash flow cycles. That’s why we streamline financial systems to keep books organized, reconciled, and up to date with minimal disruption to your daily workflow. Whether you’re managing a dine-in restaurant, café, bar, or fast-casual concept, our accounting structure adapts to your business model.

Tax planning is another central component of our restaurant support. With frequent purchases, equipment needs, wage considerations, and sales tax obligations, restaurants require a tax strategy that goes beyond basic filing. We help clients maximize deductions, plan for quarterly tax liabilities, and understand how operational decisions impact year-end results. Through our annual tax-strategy engagement—with monthly or quarterly meetings and unlimited tax support—you gain a proactive tax plan designed to minimize liability and keep you ahead of deadlines.

Our firm also assists with budgeting, cash flow forecasting, break-even analysis, and financial performance reviews. These tools help restaurant owners understand profitability, plan for growth, and identify opportunities for improvement.

With {FIRM}, restaurant owners gain a trusted partner who understands the financial realities of the hospitality industry. If you’re ready to improve profitability, strengthen compliance, and gain clarity in your financial operations, contact us today to learn how our Restaurant Accounting &amp; Tax Services can support your long-term success.""",
     f"Accounting for Restaurants in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting, bookkeeping, and tax services designed to support the fast-paced and detail-driven restaurant industry."),
    ("industries/retails.html", "Retail", "Need a retail accounting expert?", "page-retail.jpg",
     f"""At {FIRM}, we provide specialized accounting, bookkeeping, and tax services for retail businesses that need accuracy, organization, and strategic financial support. Whether you operate a boutique storefront, e-commerce shop, multi-location retail operation, or specialty goods store, our team ensures your financial systems stay aligned with your daily operations and long-term goals. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm brings deep technical expertise and industry-focused insight to every retail client we serve.

Retailers face a unique combination of financial challenges: inventory management, seasonal cash flow shifts, sales tax compliance, fluctuating labor costs, vendor relationships, and tight margins. Without the right financial structure, these challenges can quickly affect profitability. Our Retail Accounting &amp; Tax Services are designed to bring clarity, efficiency, and strategic guidance to every part of your financial operations.

We provide complete bookkeeping support—including transaction categorization, reconciliation, sales tracking, vendor payments, payroll management, and financial reporting that gives you insight into gross margin, overhead, and cash flow trends. Our systems integrate seamlessly with your point-of-sale and e-commerce platforms, ensuring clean, accurate data that supports better decision-making.

Tax strategy plays a critical role for retail clients. From sales tax requirements and inventory write-offs to cost-of-goods-sold calculations and year-end planning, retail businesses benefit from proactive guidance. Through our annual tax-strategy engagement, which includes monthly or quarterly planning sessions and unlimited support, we help retail owners minimize liability, forecast upcoming obligations, and stay ahead of tax deadlines.

We work with both brick-and-mortar and online retailers, understanding the financial differences between each model. Whether you manage inventory across multiple locations, operate a hybrid online store, or are preparing to expand, our team helps you maintain accurate financials and build a tax strategy that supports profitable growth.

With {FIRM}, retail owners gain a forward-thinking financial partner who understands the pace and pressure of the retail environment. If you’re ready to improve accuracy, strengthen tax outcomes, and gain deeper insight into your store’s financial performance, contact us today to learn how our Retail Accounting &amp; Tax Services can support long-term success.""",
     f"Accounting for Retail Stores in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting, bookkeeping, and tax services for retail businesses that need accuracy, organization, and more."),
    ("industries/automotive-dealerships.html", "Automotive Dealership", None, "page-automotive.jpg",
     # checklist: inventory tracking / inventory cost reconciliation claims removed.
     # The full repositioning (tax-advisor side) still needs approved copy.
     f"""At {FIRM}, we provide specialized accounting and tax services designed to meet the complex financial needs of automotive dealerships. From independent used-car lots to multi-location dealerships, auto businesses face unique challenges—high transaction volume, inventory financing, sales tax compliance, and cash flow management. Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm brings advanced expertise and industry-specific insight to help dealerships operate efficiently and profitably.

Automotive dealerships require accurate, real-time financial data to make informed decisions. Our team delivers structured bookkeeping, floor plan tracking, payroll management, and detailed financial reporting that supports operational clarity. We help ensure your financial systems align with your sales activity, lender requirements, and regulatory obligations, giving you confidence in both day-to-day operations and long-term planning.

Tax strategy is a critical component of dealership success. With large inventory purchases, variable revenue, financing considerations, and complex sales tax rules, proactive planning is essential. Through our annual tax-strategy engagement, we work with dealership owners to evaluate entity structure, timing of income, deductions, and long-term tax planning opportunities. Monthly or quarterly planning meetings and unlimited tax support ensure your strategy evolves alongside your business.

Our experience with automotive clients allows us to address industry-specific challenges such as managing commissions and incentive compensation, tracking floor plan interest, and preparing clean financials for lenders or potential buyers. We also assist with forecasting, budgeting, and advisory services for dealerships planning expansion, succession, or exit strategies.

When you partner with {FIRM}, you gain more than an accountant—you gain a strategic advisor who understands the financial realities of the automotive industry. If you’re looking to strengthen your accounting systems, improve tax efficiency, and gain clearer insight into your dealership’s financial performance, contact us today to learn how our Automotive Dealership Accounting &amp; Tax Services can support your long-term success.""",
     f"Automotive Dealership Accounting in Alpharetta | {FIRM}",
     f"At {FIRM}, we provide specialized accounting and tax services designed to meet the complex financial needs of automotive dealerships. Learn more."),
    ("industries/miscellaneous-industries.html", "Miscellaneous Industries", None, "page-misc.jpg",
     f"""At {FIRM}, we recognize that many successful businesses don’t fit neatly into a predefined industry category. While we serve several core industries, our expertise is not limited to those specifically listed on our website. We work with a wide range of businesses and professionals, providing customized accounting, tax, and advisory services built around each client’s unique operations and goals.

Led by Kumar Bhandari, CPA, PFS, and Master of Taxation, our firm takes a flexible, strategy-first approach. We begin by understanding how your business generates revenue, manages expenses, and plans for growth. From there, we design financial systems and tax strategies that support efficiency, compliance, and long-term success—regardless of industry.

Our services include bookkeeping, accounting, tax preparation and planning, payroll, virtual services, and part-time CFO support. Whether you’re a consultant, contractor, professional service provider, franchise owner, or growing enterprise, you receive accurate financial reporting, proactive tax planning, and clear guidance year-round.

What sets {FIRM} apart is our education-driven service model and commitment to proactive planning. Through our annual tax-strategy engagement, clients benefit from ongoing support, regular strategy check-ins, and planning that evolves alongside their business.

If your industry isn’t specifically mentioned on our site, we’re still ready to help. Contact {FIRM} today to learn how our flexible, expert-led approach can support your business with clarity and confidence.""",
     f"Accounting & Tax for Miscellaneous Industries in Alpharetta | {FIRM}",
     f"At {FIRM}, we recognize that many successful businesses don't fit neatly into a predefined industry category. No matter what you do, we're here to help."),
]


def build_details():
    for path, title, tagline, img, text, mt, md in SERVICE_PAGES:
        detail_page(path, "Services", SERVICE_LINKS, title, tagline, img, text, mt, md, ("Services", "services.html"))
    for path, title, tagline, img, text, mt, md in INDUSTRY_PAGES:
        detail_page(path, "Industries", INDUSTRY_LINKS, title, tagline, img, text, mt, md, ("Industries", "index.html#industries"))


# ---------------------------------------------------------------------------
# Contact + refund tracker
# ---------------------------------------------------------------------------
def build_contact():
    body = page_hero("Get in Touch", None,
                     "You can count on us for professional, timely and reliable tax and accounting services. If you’re ready to get started, just fill out this form and we’ll be in touch.",
                     None, [("Contact", None)], title_html=f"Get in Touch with <em>{e(FIRM)}</em>")
    body += f'''
<section class="section">
  <div class="container contact-grid">
    <div>
      <h2 data-split>Our Office</h2>
      <div class="contact-list" data-reveal style="--d:.2s">
        <div><span class="ico">{I["pin"]}</span><span>{ADDRESS_1}<br>{ADDRESS_2}</span></div>
        <a href="{PHONE_HREF}"><span class="ico">{I["phone"]}</span><span>{PHONE}</span></a>
        <a href="mailto:{EMAIL}"><span class="ico">{I["mail"]}</span><span>{EMAIL}</span></a>
      </div>
      <div class="map-frame" data-reveal style="margin-top:36px">
        <iframe src="{MAP_EMBED}" title="Map of {e(FIRM)} office" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
    {contact_form("contact")}
  </div>
</section>
<section class="section section--ivory section--tight">
  <div class="container container--narrow">
    <div class="prose" data-reveal>
      <h3>SMS Opt-In</h3>
      <p>If you would like to receive informational text message communications from {e(FIRM)}, from {PHONE}, you can sign up by texting START or YES to {PHONE}.</p>
      <p>Message frequency varies and may include responses to messages you send us, as well as information relevant to your relationship with us. Message and data rates may apply. You can opt-out of messaging at any time by replying STOP. For assistance, reply HELP.</p>
      <p>Our <a href="{href("website-privacy-policy.html")}">privacy policy</a> and <a href="{href("sms-terms-and-conditions.html")}">messaging terms and conditions</a> are available for more information.</p>
    </div>
  </div>
</section>'''
    write_page("contact.html", f"Contact {FIRM}",
               f"{FIRM} contact information: Alpharetta, Georgia - {PHONE} - {EMAIL}.", body, og_img="office-reception.webp")


STATES = [
    ("Alabama", "https://myalabamataxes.alabama.gov/_/#1"), ("Arizona", "https://www.aztaxes.gov/default.aspx"),
    ("Arkansas", "https://atap.arkansas.gov/_/#2"), ("California", "http://www.ftb.ca.gov/online/refund/index.asp"),
    ("Colorado", "https://www.colorado.gov/revenueonline/_/#2"), ("Connecticut", "https://portal.ct.gov/DRS/myconneCT/myconneCT"),
    ("Delaware", "https://dorweb.revenue.delaware.gov/refinq/"), ("Georgia", "https://gtc.dor.ga.gov/_/#2"),
    ("Hawaii", "https://tax.ehawaii.gov/hoihoi/refund.html"), ("Idaho", "https://www.accessidaho.org/secure/istc/refund/status.html"),
    ("Illinois", "https://www.revenue.state.il.us/app/refund/servlet/RefundStatus"), ("Indiana", "https://intime.dor.in.gov/eServices/_/"),
    ("Iowa", "https://www.idr.iowa.gov/wheresmyrefund/"), ("Kansas", "https://www.kdor.ks.gov/Apps/kcsc/increfundstatus.aspx"),
    ("Kentucky", "https://refund.ky.gov/"), ("Louisiana", "https://latap.revenue.louisiana.gov/_/"),
    ("Maine", "https://www.maine.gov/revenue"), ("Maryland", "https://interactive.marylandtaxes.gov/indiv/refundstatus/home.aspx"),
    ("Massachusetts", "https://mtc.dor.state.ma.us/mtc/_/#1"), ("Michigan", "https://www.michigan.gov/taxes/0,4676,7-238-43513_75466---,00.html"),
    ("Minnesota", "https://www.revenue.state.mn.us/individuals"), ("Mississippi", "https://tap.dor.ms.gov/?link=refundstatus"),
    ("Missouri", "https://dor.mo.gov/returnstatus/"), ("Montana", "https://tap.dor.mt.gov/_/#1"),
    ("Nebraska", "https://ndr-refundstatus.ne.gov/refundstatus/public/search.faces"), ("New Jersey", "https://www.nj.gov/treasury/taxation/checkrefundstatus.shtml"),
    ("New Mexico", "https://tap.state.nm.us/tap/_/#1"), ("New York", "https://www8.tax.ny.gov/PRIS/prisStart"),
    ("North Carolina", "https://www.ncdor.gov/refund"), ("North Dakota", "https://secure.apps.state.nd.us/tax/refundstatus/refundstatus.htm"),
    ("Ohio", "https://tax.ohio.gov/individual/refund-status/check-my-refund-status"), ("Oklahoma", "https://oktap.tax.ok.gov/oktap/Web/_/#1"),
    ("Oregon", "http://egov.oregon.gov/DOR/PERTAX/refund.shtml"), ("Pennsylvania", "https://mypath.pa.gov/_/"),
    ("Rhode Island", "https://www.ri.gov/cgi-bin/taxation/refund/status.cgi"), ("South Carolina", "https://dor.sc.gov/refund"),
    ("Utah", "https://incometax.utah.gov/refunds"), ("Vermont", "http://tax.vermont.gov/individuals/file-and-pay/check-refund-status"),
    ("Virginia", "https://www.individual.tax.virginia.gov/VTOL/IndRefundStatus.seam"), ("West Virginia", "https://mytaxes.wvtax.gov/_/#1"),
    ("Wisconsin", "https://ww2.revenue.wi.gov/RefundInquiry/request.html"),
]
NO_TAX_STATES = ["Alaska", "Florida", "Nevada", "New Hampshire", "South Dakota", "Tennessee", "Texas", "Washington", "Wyoming"]


def build_tracker():
    options = "".join(f'<option value="{e(u)}">{e(s)}</option>' for s, u in STATES)
    body = page_hero("Get The Status of Your Tax Refunds", "Tax Refund Tracker",
                     "Use the tool below to quickly access the refund tracking tool on the websites of IRS and your state's tax department.",
                     None, [("Tax Refund Tracker", None)])
    body += f'''
<section class="section section--ivory">
  <div class="container">
    <div class="tracker" data-stagger="0.12">
      <div class="tracker-card" data-reveal>
        <h3>Track Your Tax Refund</h3>
        <div class="stack">
          <a class="btn" href="https://sa.www4.irs.gov/irfof/lang/en/irfofgetstatus.jsp" target="_blank" rel="noopener">Track Federal Refund {I["arrow"]}</a>
          <a class="btn btn--ghost" href="https://www.irs.gov/filing/wheres-my-amended-return" target="_blank" rel="noopener">Check Federal Amended Return Fund {I["arrow"]}</a>
        </div>
      </div>
      <div class="tracker-card" data-reveal>
        <h3>Check your State Refund</h3>
        <div class="stack">
          <div class="field select-wrap">
            <label class="sr-only" for="state-select">Select State</label>
            <select id="state-select"><option value="">Select State</option>{options}</select>
            {I["chev"]}
          </div>
        </div>
        <p class="form-legal" style="margin-top:22px">Note: The following states do not have income tax, and therefore are not listed:</p>
        <ul class="state-pills">{"".join(f"<li>{s}</li>" for s in NO_TAX_STATES)}</ul>
      </div>
    </div>
  </div>
</section>'''
    write_page("tax-refund-tracker.html", f"Track your federal and state tax refunds - {FIRM}",
               "Convenient tool to help you track your federal and state tax refund status.", body, og_img="tax-form-estimated.webp")


# ---------------------------------------------------------------------------
# Legal pages: text copied verbatim from the live site into src/content/
# ---------------------------------------------------------------------------
LEGAL_LINKS = [
    ("Privacy Policy", "firm-background/privacy-policy.html"),
    ("Website Privacy Policy", "website-privacy-policy.html"),
    ("Terms of Service", "terms-of-service.html"),
    ("SMS Terms and Conditions", "sms-terms-and-conditions.html"),
]
LEGAL_PAGES = [
    ("terms-of-service.html", "Terms of Service", f"Terms of Service - {FIRM}",
     "Thanks for using our services! These terms of service cover your use and access to our services, client software and websites."),
    ("website-privacy-policy.html", "Website Privacy Policy", f"Website Privacy Policy | {FIRM}",
     "Here we describe how we collect, use, and handle your personal information when you use our websites, software, and services (“Services”)."),
    ("sms-terms-and-conditions.html", "SMS Terms and Conditions", f"{FIRM} SMS Terms and Conditions",
     f"{FIRM} respects your privacy. By opting into our SMS messaging service, you agree to our terms regarding how we handle your data."),
]


def build_legal():
    for path, title, meta_title, meta_desc in LEGAL_PAGES:
        with open(os.path.join(ROOT, "src", "content", path), encoding="utf-8") as f:
            text = f.read()
        body = page_hero(title, None, None, None, [(title, None)])
        body += f'''
<section class="section">
  <div class="container article">
    <article class="prose legal" data-reveal>{text}</article>
    {aside(LEGAL_LINKS, path, "")}
  </div>
</section>'''
        write_page(path, meta_title, meta_desc, body, og_img="page-privacy.jpg")


def main():
    build_home()
    build_firm_background()
    build_team()
    build_bios()
    build_why_best()
    build_referrals()
    build_faq()
    build_privacy()
    build_services_index()
    build_details()
    build_contact()
    build_tracker()
    build_legal()
    skip = {os.path.join(OUT, d) for d in ("src", "_old-draft", ".git", ".vscode")}
    count = sum(len([f for f in fs if f.endswith(".html")])
                for d, _, fs in os.walk(OUT) if not any(d == x or d.startswith(x + os.sep) for x in skip))
    print(f"Built {count} pages into {OUT}")


if __name__ == "__main__":
    main()
