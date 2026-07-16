#!/usr/bin/env python3
"""Generate the Dixon Pool Service static preview from verified Stage 1 data."""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent
DATA_PATH = Path('/home/chris/pitch-pipeline/01_scraped/dixon-pool-service.json')
PIPELINE_ROOT = Path('/home/chris/pitch-pipeline')
PUBLIC = ROOT / 'public'
BASE_URL = 'https://dixon-pool-service-preview.pages.dev'
PRESENTATION_TIER = 'casual'  # local consumer pool-service vertical

DATA = json.loads(DATA_PATH.read_text())
assert DATA['status'] == 'ok'

BUSINESS = DATA['business_name']
ORIGINAL_SITE_URL = DATA['source_url']
PHONE = DATA['phone']
PHONE_HREF = '+13016071011'
ADDRESS = DATA['address']
RATING = DATA['rating']
REVIEWS = DATA['review_count']
SERVICES = DATA['services']
TESTIMONIALS = DATA['testimonials']
FACEBOOK = DATA['social_links']['facebook']
TIKTOK = DATA['social_links']['tiktok']

PAGES = {
    'index.html': {
        'label': 'Home',
        'title': 'Dixon Pool Service | Pool Care in Frederick, Maryland',
        'description': 'Dixon Pool Service provides pool openings, closings, weekly maintenance, equipment repair, automation, heater repair, and safety covers in the Frederick area.',
    },
    'about.html': {
        'label': 'About',
        'title': 'About Dixon Pool Service | Frederick, Maryland',
        'description': 'Learn about Dixon Pool Service, a family pool service business established in 2005 in the Frederick area.',
    },
    'services.html': {
        'label': 'Services',
        'title': 'Pool Services | Dixon Pool Service',
        'description': 'Explore verified Dixon Pool Service offerings, including openings, closings, weekly maintenance, equipment work, automation, heaters, cleaning, and safety covers.',
    },
    'contact.html': {
        'label': 'Contact',
        'title': 'Contact Dixon Pool Service | Frederick, Maryland',
        'description': 'Call Dixon Pool Service at (301) 607-1011 or visit 9506 Hansonville Rd in Frederick, Maryland. Hours are Monday through Friday, 8 AM to 4 PM.',
    },
}

CSS = r'''
:root{--primary:#00afe7;--secondary:#2ea3f2;--navy:#105682;--ink:#22313b;--muted:#5b6972;--pale:#bfebf9;--white:#fff;--line:#cce8f2;--shadow:0 14px 35px rgba(16,86,130,.13);--radius:18px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.6;background:#fff}img{max-width:100%;display:block}a{color:inherit}.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;background:#fff;padding:.7rem 1rem;z-index:20}
.concept-banner{position:relative;z-index:10;padding:.65rem 1rem;background:#fff3bf;color:#2b250d;text-align:center;font-size:.9rem;font-weight:700;border-bottom:1px solid #eadb8a}.concept-banner a{color:#105682;font-weight:900}
.container{width:min(1120px,calc(100% - 2rem));margin:auto}.topbar{background:var(--primary);color:#052d3d;font-size:.9rem}.topbar .container{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0}.topbar a{font-weight:800;text-decoration:none}.site-header{background:#fff;border-bottom:1px solid var(--line);position:relative;z-index:5}.header-row{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:.65rem 0}.brand{display:flex;align-items:center;gap:1rem;text-decoration:none}.brand img{width:220px;height:118px;object-fit:contain}.brand-copy{display:none}.nav{display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}.nav a{padding:.65rem .9rem;text-decoration:none;font-weight:800;color:var(--navy);border-radius:999px}.nav a:hover,.nav a:focus,.nav a[aria-current=page]{background:var(--pale);color:#006b91}.nav .call{background:var(--primary);color:#072f40}
.hero{position:relative;overflow:hidden;background:var(--primary);color:#fff;padding:7rem 0;min-height:590px;display:flex;align-items:center}.hero-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0}.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,175,231,.91) 0%,rgba(0,175,231,.78) 46%,rgba(0,175,231,.35) 100%);z-index:1}.hero-grid{position:relative;z-index:2}.hero-copy{max-width:700px}.eyebrow{margin:0 0 .8rem;color:#fff;text-transform:uppercase;letter-spacing:.13em;font-weight:900;font-size:.8rem}.hero h1{font-size:clamp(2.4rem,5vw,4.5rem);line-height:1.03;margin:.2rem 0 1.2rem;text-shadow:0 2px 18px rgba(16,86,130,.35)}.hero p{font-size:1.15rem;color:#fff;max-width:650px}.rating-badge{display:inline-block;margin-top:1.25rem;background:#fff;color:var(--navy);padding:.75rem 1rem;border-radius:14px;box-shadow:var(--shadow);font-weight:900}.stars{color:#f4b400}.actions{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.6rem}.btn{display:inline-block;border-radius:999px;padding:.8rem 1.15rem;text-decoration:none;font-weight:900;border:2px solid transparent}.btn-primary{background:#fff;color:var(--navy)}.btn-light{border-color:#fff;color:#fff}.btn-navy{background:var(--navy);color:#fff}
.section{padding:5rem 0}.section-alt{background:#f5fbfd}.section-head{max-width:720px;margin-bottom:2.2rem}.section-head h2,.page-hero h1{color:var(--navy);font-size:clamp(2rem,4vw,3rem);line-height:1.12;margin:0 0 .7rem}.section-head p{color:var(--muted);font-size:1.05rem}.grid{display:grid;gap:1.2rem}.service-grid{grid-template-columns:repeat(3,1fr)}.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem;box-shadow:0 8px 24px rgba(16,86,130,.07)}.card h3{color:var(--navy);margin:.1rem 0 .5rem}.service-card{border-top:5px solid var(--primary);min-height:125px;display:flex;align-items:center}.proof-grid{grid-template-columns:repeat(3,1fr)}.proof{text-align:center}.proof strong{display:block;font-size:2rem;color:var(--navy)}.review-grid{grid-template-columns:repeat(3,1fr)}blockquote{margin:0;font-style:italic}.review footer{margin-top:1rem;color:var(--navy);font-weight:900}.contact-band{background:var(--primary);color:#052d3d}.contact-row{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:2.2rem 0}.contact-row h2{margin:0}.contact-row p{margin:.25rem 0 0}.contact-row .btn{background:var(--navy);color:#fff}
.page-hero{background:var(--pale);padding:4rem 0;border-bottom:4px solid var(--secondary)}.page-hero p{max-width:760px;color:var(--muted);font-size:1.1rem}.split{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center}.split img{border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/3;object-fit:cover}.fact-list{display:grid;gap:1rem}.fact{border-left:5px solid var(--primary);padding:1rem 1.2rem;background:var(--pale);border-radius:0 12px 12px 0}.fact strong{display:block;color:var(--navy)}.contact-grid{grid-template-columns:1fr 1fr}.contact-card h2{margin-top:0;color:var(--navy)}.detail-list{list-style:none;padding:0;margin:0}.detail-list li{padding:.8rem 0;border-bottom:1px solid var(--line)}.detail-list a{color:var(--navy);font-weight:800}.socials{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.2rem}
.site-footer{background:#071f2b;color:#c8d8df;padding:3rem 0 1.2rem}.footer-grid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:2rem}.site-footer h3{color:#fff}.site-footer a{display:block;color:#c8d8df;margin:.35rem 0}.footer-bottom{border-top:1px solid #29424e;margin-top:2rem;padding-top:1rem;text-align:center;font-size:.9rem}
@media(max-width:800px){.header-row{align-items:flex-start;flex-direction:column}.nav{width:100%}.split,.contact-grid{grid-template-columns:1fr}.hero{padding:5rem 0;min-height:540px}.hero::after{background:rgba(0,175,231,.78)}.service-grid,.proof-grid,.review-grid{grid-template-columns:1fr 1fr}.contact-row{align-items:flex-start;flex-direction:column}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.topbar .container{flex-direction:column;gap:.1rem}.brand img{width:175px;height:94px}.nav a{padding:.55rem .65rem;font-size:.9rem}.hero h1{font-size:2.55rem}.service-grid,.proof-grid,.review-grid,.footer-grid{grid-template-columns:1fr}.section{padding:3.8rem 0}.contact-row{padding:1.8rem 0}}
'''


def rel_asset(key: str) -> str:
    return 'assets/' + Path(DATA[key]).name


def canonical(filename: str) -> str:
    return BASE_URL + ('/' if filename == 'index.html' else '/' + filename)


def nav(filename: str) -> str:
    items=[]
    for page, meta in PAGES.items():
        href = '#top' if filename == 'index.html' and page == 'index.html' else ('index.html#top' if page == 'index.html' else page)
        current = ' aria-current="page"' if page == filename else ''
        items.append(f'<a href="{href}"{current}>{html.escape(meta["label"])}</a>')
    items.append(f'<a class="call" href="tel:{PHONE_HREF}">Call {html.escape(PHONE)}</a>')
    return ''.join(items)


def json_ld() -> str:
    obj={
        '@context':'https://schema.org','@type':'LocalBusiness','name':BUSINESS,
        'url':BASE_URL+'/','telephone':PHONE,
        'address':{'@type':'PostalAddress','streetAddress':'9506 Hansonville Rd','addressLocality':'Frederick','addressRegion':'MD','postalCode':'21702'},
        'openingHours':'Mo-Fr 08:00-16:00',
        'aggregateRating':{'@type':'AggregateRating','ratingValue':RATING,'reviewCount':REVIEWS},
        'sameAs':[FACEBOOK,TIKTOK],
    }
    return json.dumps(obj,separators=(',',':'))


def shell(filename: str, body: str) -> str:
    meta=PAGES[filename]
    home=filename=='index.html'
    can=canonical(filename)
    image=BASE_URL+'/assets/'+Path(DATA['images'][0]['local_path']).name
    structured=f'<script type="application/ld+json">{json_ld()}</script>' if home else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(meta['title'])}</title><meta name="description" content="{html.escape(meta['description'],quote=True)}">
<link rel="canonical" href="{can}"><link rel="icon" href="assets/{Path(DATA['favicon_path']).name}">
<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(meta['title'],quote=True)}"><meta property="og:description" content="{html.escape(meta['description'],quote=True)}"><meta property="og:url" content="{can}"><meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(meta['title'],quote=True)}"><meta name="twitter:description" content="{html.escape(meta['description'],quote=True)}"><meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="css/site.css">{structured}</head>
<body id="top" data-presentation-tier="{PRESENTATION_TIER}"><div class="concept-banner">📋 This is a free concept redesign — {html.escape(BUSINESS)}'s actual site is at <a href="{html.escape(ORIGINAL_SITE_URL,quote=True)}" target="_blank" rel="noopener">{html.escape(ORIGINAL_SITE_URL.removeprefix('https://').removeprefix('http://').rstrip('/'))}</a></div><a class="skip" href="#main-content">Skip to main content</a>
<div class="topbar"><div class="container"><span>Frederick &amp; surrounding counties</span><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></div>
<header class="site-header"><div class="container header-row"><a class="brand" href="{'#top' if home else 'index.html#top'}"><img src="{rel_asset('logo_path')}" alt="Dixon Pool Service logo"><span class="brand-copy"><strong>Dixon Pool Service</strong><span>Pool care in Frederick, Maryland</span></span></a><nav class="nav" aria-label="Main navigation">{nav(filename)}</nav></div></header>
{body}
<footer class="site-footer"><div class="container"><div class="footer-grid"><div><h3>Dixon Pool Service</h3><p>{html.escape(ADDRESS)}</p><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div><div><h3>Explore</h3><a href="about.html">About</a><a href="services.html">Services</a><a href="contact.html">Contact</a></div><div><h3>Hours &amp; social</h3><p>Monday–Friday<br>8 AM–4 PM</p><a href="{FACEBOOK}">Facebook</a><a href="{TIKTOK}">TikTok</a></div></div><div class="footer-bottom">Dixon Pool Service &bull; Frederick, Maryland</div></div></footer>
</body></html>'''


def service_cards() -> str:
    return ''.join(f'<article class="card service-card"><h3>{html.escape(s)}</h3></article>' for s in SERVICES)


def reviews(limit=3) -> str:
    out=[]
    for r in TESTIMONIALS[:limit]:
        out.append(f'''<article class="card review"><div class="stars" aria-label="{r['stars']} out of 5 stars">★★★★★</div><blockquote>“{html.escape(r['text'])}”</blockquote><footer>— {html.escape(r['author'])}</footer></article>''')
    return ''.join(out)


def home_page() -> str:
    hero_img='assets/'+Path(DATA['images'][0]['local_path']).name
    body=f'''<main id="main-content">
<section class="hero"><img class="hero-photo" src="{hero_img}" alt="Branded Dixon Pool Service company truck"><div class="container hero-grid"><div class="hero-copy"><p class="eyebrow">Pool care for Frederick &amp; surrounding counties</p><h1>Take care of your pool. Enjoy more summer.</h1><p>Openings, closings, weekly maintenance, equipment work, automation, heater repair, cleaning, and safety covers from Dixon Pool Service.</p><div class="actions"><a class="btn btn-primary" href="#services">Explore Services</a><a class="btn btn-light" href="#contact">Call Dixon Pool Service</a></div><div class="rating-badge"><span class="stars">★★★★★</span> {RATING} from {REVIEWS} Google reviews</div></div></div></section>
<section class="section" id="services"><div class="container"><div class="section-head"><p class="eyebrow">Pool services</p><h2>Pool care through every season</h2><p>Choose from seasonal openings and closings, weekly maintenance, equipment work, pool cleaning, and safety covers.</p></div><div class="grid service-grid">{service_cards()}</div><div class="actions"><a class="btn btn-navy" href="services.html">View all services</a></div></div></section>
<section class="section section-alt" id="why-dixon"><div class="container"><div class="section-head"><p class="eyebrow">Established locally</p><h2>A family pool service business since 2005</h2></div><div class="grid proof-grid"><article class="card proof"><strong>{RATING} ★</strong><span>{REVIEWS} Google reviews</span></article><article class="card proof"><strong>2005</strong><span>Year established</span></article><article class="card proof"><strong>Mon–Fri</strong><span>8 AM–4 PM</span></article></div></div></section>
<section class="section" id="reviews"><div class="container"><div class="section-head"><p class="eyebrow">Client feedback</p><h2>What customers say</h2></div><div class="grid review-grid">{reviews()}</div></div></section>
<section class="contact-band" id="contact"><div class="container contact-row"><div><h2>Ready to talk about your pool?</h2><p>Call Dixon Pool Service during listed business hours.</p></div><a class="btn" href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></section></main>'''
    return shell('index.html',body)


def about_page() -> str:
    img='assets/'+Path(DATA['images'][1]['local_path']).name
    body=f'''<main id="main-content"><section class="page-hero"><div class="container"><p class="eyebrow">About Dixon</p><h1>A Frederick-area family pool service</h1><p>Dixon Pool Service was established in 2005 by Thomas Dixon Sr. and serves Frederick and surrounding counties.</p></div></section><section class="section"><div class="container split"><div><div class="section-head"><h2>Local history, focused service</h2><p>The verified source describes Dixon Pool Service as a family business established in 2005. Its current service offering covers seasonal care, weekly maintenance, equipment, automation, heaters, cleaning, and safety covers.</p></div><div class="fact-list"><div class="fact"><strong>Established</strong>2005</div><div class="fact"><strong>Service area</strong>Frederick and surrounding counties</div><div class="fact"><strong>Business hours</strong>Monday–Friday, 8 AM–4 PM</div></div><div class="actions"><a class="btn btn-navy" href="services.html">Explore services</a><a class="btn btn-primary" href="contact.html">Contact Dixon</a></div></div><img src="{img}" alt="Pool service work by Dixon Pool Service"></div></section></main>'''
    return shell('about.html',body)


def services_page() -> str:
    img='assets/'+Path(DATA['images'][2]['local_path']).name
    body=f'''<main id="main-content"><section class="page-hero"><div class="container"><p class="eyebrow">Pool service list</p><h1>Pool services for Frederick-area homes</h1><p>Seasonal openings and closings, routine care, equipment work, and specialized pool systems.</p></div></section><section class="section"><div class="container"><div class="split"><div><div class="section-head"><h2>How Dixon can help</h2><p>Choose from the service offerings below.</p></div><div class="grid service-grid">{service_cards()}</div></div><img src="{img}" alt="Pool care project by Dixon Pool Service"></div></div></section><section class="contact-band"><div class="container contact-row"><div><h2>Ask about your pool service needs</h2><p>Call Monday through Friday, 8 AM–4 PM.</p></div><a class="btn" href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></section></main>'''
    return shell('services.html',body)


def contact_page() -> str:
    maps='https://www.google.com/maps/search/?api=1&query='+quote_plus(ADDRESS)
    body=f'''<main id="main-content"><section class="page-hero"><div class="container"><p class="eyebrow">Get in touch</p><h1>Contact Dixon Pool Service</h1><p>Call during listed hours or use the verified address below.</p></div></section><section class="section"><div class="container grid contact-grid"><article class="card contact-card"><h2>Contact details</h2><ul class="detail-list"><li><strong>Phone</strong><br><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></li><li><strong>Address</strong><br>{html.escape(ADDRESS)}<br><a href="{maps}">Open in Google Maps</a></li><li><strong>Hours</strong><br>Monday–Friday, 8 AM–4 PM</li></ul><div class="socials"><a class="btn btn-navy" href="{FACEBOOK}">Facebook</a><a class="btn btn-primary" href="{TIKTOK}">TikTok</a></div></article><article class="card contact-card"><h2>Services at a glance</h2><ul class="detail-list">{''.join(f'<li>{html.escape(s)}</li>' for s in SERVICES)}</ul><div class="actions"><a class="btn btn-navy" href="tel:{PHONE_HREF}">Call Dixon Pool Service</a></div></article></div></section></main>'''
    return shell('contact.html',body)


def build() -> None:
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    (PUBLIC/'assets').mkdir(parents=True)
    (PUBLIC/'css').mkdir(parents=True)
    for key in ('logo_path','favicon_path'):
        src=PIPELINE_ROOT/DATA[key]; shutil.copy2(src,PUBLIC/'assets'/src.name)
    for item in DATA['images']:
        src=PIPELINE_ROOT/item['local_path']; shutil.copy2(src,PUBLIC/'assets'/src.name)
    shutil.copy2(PIPELINE_ROOT/DATA['favicon_path'],PUBLIC/'favicon.ico')
    (PUBLIC/'css'/'site.css').write_text(CSS)
    outputs={'index.html':home_page(),'about.html':about_page(),'services.html':services_page(),'contact.html':contact_page()}
    for name,text in outputs.items(): (PUBLIC/name).write_text(text)
    urls='\n'.join(f'  <url><loc>{canonical(name)}</loc></url>' for name in PAGES)
    (PUBLIC/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (PUBLIC/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    (PUBLIC/'_redirects').write_text('/scan / 302\n')
    print(f'Built {len(outputs)} pages in {PUBLIC}')

if __name__=='__main__': build()
