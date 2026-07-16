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
TURNSTILE_SITEKEY = (ROOT / 'turnstile-sitekey.txt').read_text().strip()

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
.container{width:min(1120px,calc(100% - 2rem));margin:auto}.topbar{background:var(--primary);color:#052d3d;font-size:.9rem}.topbar .container{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0}.topbar a{font-weight:800;text-decoration:none}.site-header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:90;box-shadow:0 4px 18px rgba(16,86,130,.12);transition:box-shadow .22s ease}.header-row{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:.65rem 0;transition:padding .22s ease}.brand{display:flex;align-items:center;gap:1rem;text-decoration:none}.brand img{width:220px;height:118px;object-fit:contain;transition:width .22s ease,height .22s ease}.brand-copy{display:none}.nav{display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}.nav a{padding:.65rem .9rem;text-decoration:none;font-weight:800;color:var(--navy);border-radius:999px;transition:padding .22s ease,background .15s ease}.nav a:hover,.nav a:focus,.nav a[aria-current=page]{background:var(--pale);color:#006b91}.nav .call{background:var(--primary);color:#072f40}.site-header.is-condensed .header-row{padding:.2rem 0}.site-header.is-condensed .brand img{width:175px;height:94px}.site-header.is-condensed .nav a{padding:.45rem .72rem}main [id]{scroll-margin-top:8rem}
.hero{position:relative;overflow:hidden;background:var(--primary);color:#fff;padding:7rem 0;min-height:590px;display:flex;align-items:center}.hero-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0}.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,175,231,.91) 0%,rgba(0,175,231,.78) 46%,rgba(0,175,231,.35) 100%);z-index:1}.hero-grid{position:relative;z-index:2}.hero-copy{max-width:700px}.eyebrow{margin:0 0 .8rem;color:#fff;text-transform:uppercase;letter-spacing:.13em;font-weight:900;font-size:.8rem}.hero h1{font-size:clamp(2.4rem,5vw,4.5rem);line-height:1.03;margin:.2rem 0 1.2rem;text-shadow:0 2px 18px rgba(16,86,130,.35)}.hero p{font-size:1.15rem;color:#fff;max-width:650px}.rating-badge{display:inline-block;margin-top:1.25rem;background:#fff;color:var(--navy);padding:.75rem 1rem;border-radius:14px;box-shadow:var(--shadow);font-weight:900}.stars{color:#f4b400}.actions{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.6rem}.btn{display:inline-block;border-radius:999px;padding:.8rem 1.15rem;text-decoration:none;font-weight:900;border:2px solid transparent}.btn-primary{background:#fff;color:var(--navy)}.btn-light{border-color:#fff;color:#fff}.btn-navy{background:var(--navy);color:#fff}
.section{padding:5rem 0}.section-alt{background:#f5fbfd}.section-head{max-width:720px;margin-bottom:2.2rem}.section-head h2,.page-hero h1{color:var(--navy);font-size:clamp(2rem,4vw,3rem);line-height:1.12;margin:0 0 .7rem}.section-head p{color:var(--muted);font-size:1.05rem}.grid{display:grid;gap:1.2rem}.service-grid{grid-template-columns:repeat(3,1fr)}.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem;box-shadow:0 8px 24px rgba(16,86,130,.07)}.card h3{color:var(--navy);margin:.1rem 0 .5rem}.service-card{border-top:5px solid var(--primary);min-height:125px;display:flex;align-items:center}.proof-grid{grid-template-columns:repeat(3,1fr)}.proof{text-align:center}.proof strong{display:block;font-size:2rem;color:var(--navy)}.review-grid{grid-template-columns:repeat(3,1fr)}blockquote{margin:0;font-style:italic}.review footer{margin-top:1rem;color:var(--navy);font-weight:900}.contact-band{background:var(--primary);color:#052d3d}.contact-row{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:2.2rem 0}.contact-row h2{margin:0}.contact-row p{margin:.25rem 0 0}.contact-row .btn{background:var(--navy);color:#fff}
.page-hero{background:var(--pale);padding:4rem 0;border-bottom:4px solid var(--secondary)}.page-hero p{max-width:760px;color:var(--muted);font-size:1.1rem}.split{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center}.split img{border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/3;object-fit:cover}.fact-list{display:grid;gap:1rem}.fact{border-left:5px solid var(--primary);padding:1rem 1.2rem;background:var(--pale);border-radius:0 12px 12px 0}.fact strong{display:block;color:var(--navy)}.contact-grid{grid-template-columns:1fr 1fr}.contact-card h2{margin-top:0;color:var(--navy)}.detail-list{list-style:none;padding:0;margin:0}.detail-list li{padding:.8rem 0;border-bottom:1px solid var(--line)}.detail-list a{color:var(--navy);font-weight:800}.socials{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.2rem}.inquiry-form{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.form-field{display:grid;gap:.35rem}.form-field-full{grid-column:1/-1}.form-field label{font-weight:800;color:var(--navy)}.form-field input,.form-field textarea{width:100%;padding:.8rem;border:1px solid #8cb8ca;border-radius:10px;font:inherit;color:var(--ink);background:#fff}.form-field textarea{min-height:150px;resize:vertical}.form-field input:focus,.form-field textarea:focus{outline:3px solid rgba(0,175,231,.25);border-color:var(--primary)}.form-note{grid-column:1/-1;color:var(--muted);font-size:.92rem}.honeypot{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}.inquiry-form .btn{cursor:pointer;border:0;justify-self:start}
.hero-divider{height:40px;margin-top:-40px;position:relative;z-index:3;overflow:hidden;line-height:0;pointer-events:none}.hero-divider svg{display:block;width:100%;height:100%}.hero-divider path{fill:#fff}.reveal{opacity:1;transform:none}.reveal.reveal-pending{opacity:0;transform:translateY(14px);transition:opacity .42s ease,transform .42s ease}.reveal.is-visible{opacity:1;transform:none}
.site-footer{background:#071f2b;color:#c8d8df;padding:3rem 0 1.2rem}.footer-grid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:2rem}.site-footer h3{color:#fff}.site-footer a{display:block;color:#c8d8df;margin:.35rem 0}.footer-bottom{border-top:1px solid #29424e;margin-top:2rem;padding-top:1rem;text-align:center;font-size:.9rem}
@media(max-width:800px){.header-row{align-items:flex-start;flex-direction:column}.nav{width:100%}.split,.contact-grid{grid-template-columns:1fr}.hero{padding:5rem 0;min-height:540px}.hero::after{background:rgba(0,175,231,.78)}.service-grid,.proof-grid,.review-grid{grid-template-columns:1fr 1fr}.contact-row{align-items:flex-start;flex-direction:column}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.topbar .container{flex-direction:column;gap:.1rem}.brand img{width:175px;height:94px}.site-header.is-condensed .header-row{gap:.25rem}.site-header.is-condensed .brand img{width:135px;height:72px}.nav a{padding:.55rem .65rem;font-size:.9rem}.site-header.is-condensed .nav a{padding:.4rem .5rem;font-size:.84rem}main [id]{scroll-margin-top:14rem}.hero h1{font-size:2.55rem}.service-grid,.proof-grid,.review-grid,.footer-grid,.inquiry-form{grid-template-columns:1fr}.form-field-full{grid-column:auto}.section{padding:3.8rem 0}.contact-row{padding:1.8rem 0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.header-row,.brand img,.nav a,.reveal.reveal-pending{transition:none}.reveal.reveal-pending{opacity:1;transform:none}}
'''

JS = r'''(() => {
  const header = document.querySelector('[data-sticky-header]');
  if (header) {
    const syncHeader = () => header.classList.toggle('is-condensed', window.scrollY > 48);
    syncHeader();
    window.addEventListener('scroll', syncHeader, { passive: true });
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion || !('IntersectionObserver' in window)) return;

  const targets = [...document.querySelectorAll('main > section:not(.hero):not(.page-hero)')];
  const pending = new Set(targets);
  targets.forEach((target) => target.classList.add('reveal', 'reveal-pending'));

  const reveal = (target) => {
    if (!pending.delete(target)) return;
    target.classList.remove('reveal-pending');
    target.classList.add('is-visible');
    observer.unobserve(target);
    if (!pending.size) {
      window.removeEventListener('scroll', revealPassed);
      window.removeEventListener('hashchange', revealPassed);
    }
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) reveal(entry.target);
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -24px' });
  const revealPassed = () => pending.forEach((target) => {
    if (target.getBoundingClientRect().top < window.innerHeight * 0.92) reveal(target);
  });

  targets.forEach((target) => observer.observe(target));
  revealPassed();
  window.addEventListener('scroll', revealPassed, { passive: true });
  window.addEventListener('hashchange', revealPassed);
})();
'''

WORKER_JS = r'''const ORIGINAL_CONTACT = "https://dixonpoolsmd.com/contact/";
const MAX_BODY_BYTES = 32 * 1024;

function responsePage(status, title, message) {
  const safe = (value) => String(value).replace(/[&<>"']/g, (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  return new Response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${safe(title)} | Dixon Pool Service</title><body><div>📋 This is a free concept redesign — Dixon Pool Service's actual site is at <a href="https://dixonpoolsmd.com/">dixonpoolsmd.com</a></div><main><h1>${safe(title)}</h1><p>${safe(message)}</p><p><a href="/contact">Return to Request Service</a></p></main></body></html>`, {status, headers:{"content-type":"text/html; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff","referrer-policy":"no-referrer"}});
}

function extract(source, pattern, label) {
  const match = source.match(pattern);
  if (!match) throw new Error(`Original contact form is missing ${label}`);
  return match[1];
}

function field(form, name, max) {
  const value = form.get(name);
  if (value === null) return "";
  const clean = value.trim();
  if (clean.length > max) throw new RangeError(`${name} is too long`);
  return clean;
}

async function readBoundedBody(request, maxBytes) {
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maxBytes) {
      await reader.cancel();
      throw new RangeError("Request body is too large");
    }
    chunks.push(value);
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
  return new TextDecoder("utf-8", {fatal:true}).decode(body);
}

async function forwardToOriginal(request, env) {
 try {
  const origin = request.headers.get("origin");
  if (origin !== new URL(request.url).origin) return responsePage(403, "Submission blocked", "Please use the Request Service form on this site.");
  const type = request.headers.get("content-type") || "";
  if (!type.includes("application/x-www-form-urlencoded")) {
    return responsePage(415, "Unsupported submission", "Please use the Request Service form.");
  }
  const raw = await readBoundedBody(request, MAX_BODY_BYTES);
  const form = new URLSearchParams(raw);
  if (field(form, "company_website", 240)) return responsePage(200, "Request received", "Thank you.");
  const values = {
    name: field(form, "name", 120),
    phone: field(form, "phone", 40),
    email: field(form, "email", 254),
    service: field(form, "service", 240),
    message: field(form, "message", 4000),
  };
  if (!values.name || !values.phone || !values.email || !values.message) {
    return responsePage(422, "Please complete the form", "Name, phone number, email address, and message are required.");
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) return responsePage(422, "Check your email", "Enter a valid email address.");
  const turnstile = field(form, "cf-turnstile-response", 4096);
  if (!turnstile || !env.TURNSTILE_SECRET) return responsePage(422, "Verification required", "Complete the anti-spam check and try again.");
  const verifyBody = new URLSearchParams({secret:env.TURNSTILE_SECRET,response:turnstile,remoteip:request.headers.get("CF-Connecting-IP") || ""});
  const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {method:"POST",headers:{"content-type":"application/x-www-form-urlencoded"},body:verifyBody.toString()});
  const verdict = await verify.json();
  if (!verify.ok || verdict.success !== true) return responsePage(422, "Verification failed", "Complete the anti-spam check and try again.");

  const page = await fetch(ORIGINAL_CONTACT, {headers:{"user-agent":"Website Rescue contact-form bridge/1.0","accept":"text/html"}});
  if (!page.ok) return responsePage(502, "Service temporarily unavailable", "Please call Dixon Pool Service at (301) 607-1011.");
  const source = await page.text();
  let nonce, first, second;
  try {
    nonce = extract(source, /name="_wpnonce-et-pb-contact-form-submitted-0" value="([^"]+)"/, "security token");
    const captchaTag = extract(source, /(<input[^>]*name="et_pb_contact_captcha_0"[^>]*>)/, "CAPTCHA field");
    first = Number(extract(captchaTag, /data-first_digit="(\d+)"/, "first CAPTCHA digit"));
    second = Number(extract(captchaTag, /data-second_digit="(\d+)"/, "second CAPTCHA digit"));
  } catch (_) {
    return responsePage(502, "Service temporarily unavailable", "Please call Dixon Pool Service at (301) 607-1011.");
  }
  const upstream = new URLSearchParams({
    et_pb_contact_name_0: values.name,
    et_pb_contact_phone_number_0: values.phone,
    et_pb_contact_email_0: values.email,
    et_pb_contact_service_0: values.service,
    et_pb_contact_message_0: values.message,
    et_pb_contact_captcha_0: String(first + second),
    et_pb_contactform_submit_0: "et_contact_proccess",
    et_builder_submit_button: "Submit",
    "_wpnonce-et-pb-contact-form-submitted-0": nonce,
    _wp_http_referer: "/contact/",
  });
  const sent = await fetch(ORIGINAL_CONTACT, {method:"POST", headers:{"content-type":"application/x-www-form-urlencoded","user-agent":"Website Rescue contact-form bridge/1.0","referer":ORIGINAL_CONTACT}, body:upstream.toString(), redirect:"follow"});
  if (!sent.ok) return responsePage(502, "Request not sent", "Please call Dixon Pool Service at (301) 607-1011.");
  const result = await sent.text();
  const message = result.match(/<div class="et-pb-contact-message">([\s\S]*?)<\/div>/i);
  const plain = message ? message[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim() : "";
  const formStillPresent = /<form class="et_pb_contact_form\b/i.test(result);
  const confirmed = plain === "Thanks for contacting us";
  if (!confirmed || formStillPresent) return responsePage(502, "Request not confirmed", "Please call Dixon Pool Service at (301) 607-1011.");
  return responsePage(200, "Request sent", "Dixon Pool Service's original contact system accepted your request.");
 } catch (error) {
  const status = error instanceof RangeError ? 413 : 502;
  const title = status === 413 ? "Request too large" : "Service temporarily unavailable";
  return responsePage(status, title, "Please call Dixon Pool Service at (301) 607-1011.");
 }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/request-service") {
      if (request.method !== "POST") return new Response("Method Not Allowed", {status:405, headers:{allow:"POST"}});
      return forwardToOriginal(request, env);
    }
    return env.ASSETS.fetch(request);
  }
};
'''

WAVE_DIVIDER = '''<div class="hero-divider hero-divider--wave" aria-hidden="true">
<svg viewBox="0 0 1440 72" preserveAspectRatio="none" focusable="false"><path d="M0,24 C240,72 480,0 720,30 C960,60 1200,6 1440,36 L1440,72 L0,72 Z"></path></svg>
</div>'''


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


def add_casual_wave(body: str) -> str:
    hero_end = body.find('</section>')
    if hero_end < 0:
        raise ValueError('page is missing its hero section')
    insert_at = hero_end + len('</section>')
    return body[:insert_at] + WAVE_DIVIDER + body[insert_at:]


def shell(filename: str, body: str) -> str:
    meta=PAGES[filename]
    home=filename=='index.html'
    can=canonical(filename)
    image=BASE_URL+'/assets/'+Path(DATA['images'][0]['local_path']).name
    structured=f'<script type="application/ld+json">{json_ld()}</script>' if home else ''
    body=add_casual_wave(body)
    return f'''<!doctype html>
<html lang="en" data-presentation-tier="{PRESENTATION_TIER}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(meta['title'])}</title><meta name="description" content="{html.escape(meta['description'],quote=True)}">
<link rel="canonical" href="{can}"><link rel="icon" href="assets/{Path(DATA['favicon_path']).name}">
<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(meta['title'],quote=True)}"><meta property="og:description" content="{html.escape(meta['description'],quote=True)}"><meta property="og:url" content="{can}"><meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(meta['title'],quote=True)}"><meta name="twitter:description" content="{html.escape(meta['description'],quote=True)}"><meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="css/site.css">{structured}</head>
<body id="top"><div class="concept-banner">📋 This is a free concept redesign — {html.escape(BUSINESS)}'s actual site is at <a href="{html.escape(ORIGINAL_SITE_URL,quote=True)}" target="_blank" rel="noopener">{html.escape(ORIGINAL_SITE_URL.removeprefix('https://').removeprefix('http://').rstrip('/'))}</a></div><a class="skip" href="#main-content">Skip to main content</a>
<div class="topbar"><div class="container"><span>Frederick &amp; surrounding counties</span><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></div>
<header class="site-header" data-sticky-header><div class="container header-row"><a class="brand" href="{'#top' if home else 'index.html#top'}"><img src="{rel_asset('logo_path')}" alt="Dixon Pool Service logo"><span class="brand-copy"><strong>Dixon Pool Service</strong><span>Pool care in Frederick, Maryland</span></span></a><nav class="nav" aria-label="Main navigation">{nav(filename)}</nav></div></header>
{body}
<footer class="site-footer"><div class="container"><div class="footer-grid"><div><h3>Dixon Pool Service</h3><p>{html.escape(ADDRESS)}</p><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div><div><h3>Explore</h3><a href="about.html">About</a><a href="services.html">Services</a><a href="contact.html">Contact</a></div><div><h3>Hours &amp; social</h3><p>Monday–Friday<br>8 AM–4 PM</p><a href="{FACEBOOK}">Facebook</a><a href="{TIKTOK}">TikTok</a></div></div><div class="footer-bottom">Dixon Pool Service &bull; Frederick, Maryland</div></div></footer>
<script src="assets/js/shared.js" defer></script>
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
    body=f'''<main id="main-content"><section class="page-hero"><div class="container"><p class="eyebrow">Get in touch</p><h1>Request Pool Service</h1><p>Send a service request or call during listed business hours.</p></div></section><section class="section"><div class="container grid contact-grid"><article class="card contact-card"><h2>Request Service</h2><p>This form preserves the original site's service-inquiry purpose and sends requests through Dixon Pool Service's existing contact system.</p><form class="inquiry-form" action="/api/request-service" method="post"><div class="honeypot" aria-hidden="true"><label for="company-website">Company website</label><input id="company-website" name="company_website" type="text" tabindex="-1" autocomplete="off"></div><div class="form-field"><label for="request-name">Name</label><input id="request-name" name="name" type="text" autocomplete="name" required maxlength="120"></div><div class="form-field"><label for="request-phone">Phone Number</label><input id="request-phone" name="phone" type="tel" autocomplete="tel" required maxlength="40"></div><div class="form-field form-field-full"><label for="request-email">Email Address</label><input id="request-email" name="email" type="email" autocomplete="email" required maxlength="254"></div><div class="form-field form-field-full"><label for="request-service">Service(s) Needed</label><input id="request-service" name="service" type="text" autocomplete="off" maxlength="240"></div><div class="form-field form-field-full"><label for="request-message">Message</label><textarea id="request-message" name="message" required maxlength="4000"></textarea></div><div class="form-field form-field-full"><div class="cf-turnstile" data-sitekey="{html.escape(TURNSTILE_SITEKEY, quote=True)}"></div></div><p class="form-note">Cloudflare verifies the anti-spam check, then the demo forwards your request to Dixon Pool Service's original contact system. The demo does not intentionally store inquiry details.</p><button class="btn btn-navy" type="submit">Send Service Request</button></form></article><article class="card contact-card"><h2>Contact details</h2><ul class="detail-list"><li><strong>Phone</strong><br><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></li><li><strong>Address</strong><br>{html.escape(ADDRESS)}<br><a href="{maps}">Open in Google Maps</a></li><li><strong>Hours</strong><br>Monday–Friday, 8 AM–4 PM</li></ul><div class="socials"><a class="btn btn-navy" href="{FACEBOOK}">Facebook</a><a class="btn btn-primary" href="{TIKTOK}">TikTok</a></div></article></div></section><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script></main>'''
    return shell('contact.html',body)


def build() -> None:
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    (PUBLIC/'assets').mkdir(parents=True)
    (PUBLIC/'assets'/'js').mkdir(parents=True)
    (PUBLIC/'css').mkdir(parents=True)
    for key in ('logo_path','favicon_path'):
        src=PIPELINE_ROOT/DATA[key]; shutil.copy2(src,PUBLIC/'assets'/src.name)
    for item in DATA['images']:
        src=PIPELINE_ROOT/item['local_path']; shutil.copy2(src,PUBLIC/'assets'/src.name)
    shutil.copy2(PIPELINE_ROOT/DATA['favicon_path'],PUBLIC/'favicon.ico')
    (PUBLIC/'css'/'site.css').write_text(CSS)
    (PUBLIC/'assets'/'js'/'shared.js').write_text(JS)
    (PUBLIC/'_worker.js').write_text(WORKER_JS)
    outputs={'index.html':home_page(),'about.html':about_page(),'services.html':services_page(),'contact.html':contact_page()}
    for name,text in outputs.items(): (PUBLIC/name).write_text(text)
    urls='\n'.join(f'  <url><loc>{canonical(name)}</loc></url>' for name in PAGES)
    (PUBLIC/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (PUBLIC/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    (PUBLIC/'_redirects').write_text('/scan / 302\n')
    print(f'Built {len(outputs)} pages in {PUBLIC}')

if __name__=='__main__': build()
