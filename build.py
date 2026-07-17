#!/usr/bin/env python3
"""Generate the Dixon Pool Service static preview from verified Stage 1 data."""
from __future__ import annotations

import html
import hashlib
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

# Verbatim service and FAQ copy transcribed from the saved Stage 1 services.html.
SERVICE_DESCRIPTIONS = {
    'Pool Openings': 'Opening an in-ground swimming pool can be a daunting task. If not done properly, it could take weeks for your pool to be ready to swim. Let the pro’s at Dixon Pool Service open your pool. We see problems that could prevent your pool from being ready in a timely manner',
    'Pool Closings': 'Pool closings are the most important service that we offer. A quality pool closing helps ensure a cleaner, smother opening in the spring. It also helps prevent potential damage to your equipment and plumbing lines. Let us put your pool to bed for the winter and help remove any worries of freeze damage.',
    'Weekly Pool Maintenance': 'For those of you who just want to swim and not have to deal with the pool, we offer Weekly Pool Service. We come out once a week and take care of everything, so all you have to do is enjoy clear, sparkling water. Short of us occasionally asking you to add water to the pool, all you do is swim.',
    'Pool Automation Repairs & Upgrades': 'Looking to adjust your pool pump, or control your pool or spa temperatures, lighting, and other equipment wirelessly through your smartphone or tablet? Dixon Pool Service can recommend a wide variety of energy-efficient swimming pool automation products that can save you time and money.',
    'Heater Repairs': 'Pool heater tune-up, repair, and troubleshooting can be a very daunting task—not typically a do-it-yourself project. Intelligent pool owners know that spending a little on preventive maintenance now can save them money and headaches later.',
    'Custom Mesh Safety Pool Covers': 'Need a New Safety Cover for Your Pool? Give us a call and we’ll help you get a custom-designed cover to match the exact specifications of your pool.',
    'Pool Cleaning (one-time / party service)': 'Yes, Dixon Pool service is happy to help get your pool cleaned up or provide a party service for a special occasion.',
    'Safety Cover Installation': 'Yes! Dixon Pool Service can provide you with a free quote to add or remake a swimming pool safety cover.',
}

assert DATA['faq_page_authorized'] is True
FAQS = [(pair['question'], pair['answer']) for pair in DATA['faq_pairs']]
assert len(FAQS) == 11

BEFORE_AFTER_PAIR = DATA['before_after_pairs'][0]
assert BEFORE_AFTER_PAIR['approved'] is True
BEFORE_AFTER_ASSETS = {
    role: PIPELINE_ROOT / BEFORE_AFTER_PAIR[role]['local_path']
    for role in ('before', 'after')
}

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
        'description': 'Explore Dixon Pool Service offerings, including openings, closings, weekly maintenance, equipment work, automation, heaters, cleaning, and safety covers.',
    },
    'faq.html': {
        'label': 'FAQ',
        'title': 'Pool Service FAQ | Dixon Pool Service',
        'description': 'Read Dixon Pool Service answers about cleaning, equipment, estimates, weekly service, safety covers, accepted payments, and seasonal timing.',
    },
    'contact.html': {
        'label': 'Contact',
        'title': 'Contact Dixon Pool Service | Frederick, Maryland',
        'description': 'Call Dixon Pool Service at (301) 607-1011 or visit 9506 Hansonville Rd in Frederick, Maryland. Hours are Monday through Friday, 8 AM to 4 PM.',
    },
    'privacy.html': {
        'label': 'Privacy',
        'title': 'Privacy Policy | Dixon Pool Service Concept Redesign',
        'description': 'Privacy information for the Dixon Pool Service concept redesign and its service request form.',
        'footer_only': True,
    },
    'terms.html': {
        'label': 'Terms',
        'title': 'Terms of Use | Dixon Pool Service Concept Redesign',
        'description': 'Terms of use for the Dixon Pool Service concept redesign preview.',
        'footer_only': True,
    },
}

CSS = r'''
:root{--primary:#00afe7;--secondary:#2ea3f2;--navy:#105682;--ink:#22313b;--muted:#5b6972;--pale:#bfebf9;--white:#fff;--line:#cce8f2;--shadow:0 14px 35px rgba(16,86,130,.13);--radius:18px}
*{box-sizing:border-box}html{scroll-behavior:smooth;max-width:100%;overflow-x:clip}body{margin:0;max-width:100%;overflow-x:clip;color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.6;background:#fff}img{max-width:100%;display:block}a{color:inherit}.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;background:#fff;padding:.7rem 1rem;z-index:20}
.concept-banner{position:relative;z-index:10;padding:.65rem 1rem;background:#fff3bf;color:#2b250d;text-align:center;font-size:.9rem;font-weight:700;border-bottom:1px solid #eadb8a;overflow-wrap:anywhere}.concept-banner a{color:#105682;font-weight:900}
.container{width:min(1120px,calc(100% - 2rem));margin:auto}.topbar{background:var(--primary);color:#052d3d;font-size:.9rem}.topbar .container{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0}.topbar a{font-weight:800;text-decoration:none}.site-header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:90;box-shadow:0 4px 18px rgba(16,86,130,.12);transition:box-shadow .22s ease}.header-row{display:flex;align-items:flex-start;flex-direction:column;gap:.5rem;padding:.65rem 0;transition:padding .22s ease;min-width:0}.brand{display:flex;align-items:center;gap:1rem;text-decoration:none;min-width:0;max-width:100%}.brand img{width:220px;height:118px;max-width:100%;object-fit:contain;transition:width .22s ease,height .22s ease}.brand-copy{display:none}.nav{width:100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:center;gap:.35rem;min-width:0}.nav a{width:100%;padding:.65rem .9rem;text-decoration:none;font-weight:800;color:var(--navy);border-radius:999px;transition:padding .22s ease,background .15s ease;min-width:0;overflow-wrap:anywhere;text-align:center}.nav a:hover,.nav a:focus,.nav a[aria-current=page]{background:var(--pale);color:#006b91}.nav .call{background:var(--primary);color:#072f40}.site-header.is-condensed .header-row{padding:.2rem 0}.site-header.is-condensed .brand img{width:175px;height:94px}.site-header.is-condensed .nav a{padding:.45rem .72rem}main [id]{scroll-margin-top:8rem}
.hero{position:relative;overflow:hidden;background:var(--primary);color:#fff;padding:7rem 0;min-height:590px;display:flex;align-items:center}.hero-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0}.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,175,231,.91) 0%,rgba(0,175,231,.78) 46%,rgba(0,175,231,.35) 100%);z-index:1}.hero-grid{position:relative;z-index:2}.hero-copy{max-width:700px}.eyebrow{margin:0 0 .8rem;color:#fff;text-transform:uppercase;letter-spacing:.13em;font-weight:900;font-size:.8rem}.hero h1{font-size:clamp(2.4rem,5vw,4.5rem);line-height:1.03;margin:.2rem 0 1.2rem;text-shadow:0 2px 18px rgba(16,86,130,.35)}.hero p{font-size:1.15rem;color:#fff;max-width:650px}.rating-badge{display:inline-block;margin-top:1.25rem;background:#fff;color:var(--navy);padding:.75rem 1rem;border-radius:14px;box-shadow:var(--shadow);font-weight:900}.stars{color:#f4b400}.actions{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.6rem}.btn{display:inline-block;border-radius:999px;padding:.8rem 1.15rem;text-decoration:none;font-weight:900;border:2px solid transparent}.btn-primary{background:#fff;color:var(--navy)}.btn-light{border-color:#fff;color:#fff}.btn-navy{background:var(--navy);color:#fff}
.section{padding:5rem 0}.section-alt{background:#f5fbfd}.section-head{max-width:720px;margin-bottom:2.2rem}.section-head h2,.page-hero h1{color:var(--navy);font-size:clamp(2rem,4vw,3rem);line-height:1.12;margin:0 0 .7rem}.section-head p{color:var(--muted);font-size:1.05rem}.grid{display:grid;gap:1.2rem;min-width:0}.service-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.card{min-width:0;overflow-wrap:anywhere;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem;box-shadow:0 8px 24px rgba(16,86,130,.07)}.card h3{color:var(--navy);margin:.1rem 0 .5rem}.service-card{border-top:5px solid var(--primary);min-height:125px}.service-card p{margin:.5rem 0 0;color:var(--muted)}.proof-grid{grid-template-columns:repeat(3,1fr)}.proof{text-align:center}.proof strong{display:block;font-size:2rem;color:var(--navy)}.review-grid{grid-template-columns:repeat(3,1fr)}blockquote{margin:0;font-style:italic}.review footer{margin-top:1rem;color:var(--navy);font-weight:900}.contact-band{background:var(--primary);color:#052d3d}.contact-row{display:flex;align-items:center;justify-content:space-between;gap:2rem;padding:2.2rem 0}.contact-row h2{margin:0}.contact-row p{margin:.25rem 0 0}.contact-row .btn{background:var(--navy);color:#fff}
.page-hero{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:4.75rem 0;border-bottom:4px solid var(--secondary)}.page-hero-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;opacity:.28}.page-hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(16,86,130,.96),rgba(0,175,231,.58))}.page-hero .container{position:relative;z-index:1}.page-hero h1{color:#fff}.page-hero p{max-width:760px;color:#fff;font-size:1.1rem}.split{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center}.split>img{border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/3;object-fit:cover}.fact-list{display:grid;gap:1rem}.fact{border-left:5px solid var(--primary);padding:1rem 1.2rem;background:var(--pale);border-radius:0 12px 12px 0}.fact strong{display:block;color:var(--navy)}.contact-grid{grid-template-columns:1fr 1fr}.contact-card h2{margin-top:0;color:var(--navy)}.detail-list{list-style:none;padding:0;margin:0}.detail-list li{padding:.8rem 0;border-bottom:1px solid var(--line)}.detail-list a{color:var(--navy);font-weight:800}.socials{display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.2rem}.inquiry-form{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.form-field{display:grid;gap:.35rem}.form-field-full{grid-column:1/-1}.form-field label{font-weight:800;color:var(--navy)}.form-field input,.form-field textarea{width:100%;padding:.8rem;border:1px solid #8cb8ca;border-radius:10px;font:inherit;color:var(--ink);background:#fff}.form-field textarea{min-height:150px;resize:vertical}.form-field input:focus,.form-field textarea:focus{outline:3px solid rgba(0,175,231,.25);border-color:var(--primary)}.form-note{grid-column:1/-1;color:var(--muted);font-size:.92rem}.honeypot{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}.inquiry-form .btn{cursor:pointer;border:0;justify-self:start}
.comparison{max-width:900px;margin:0 auto}.comparison-stage{position:relative;overflow:hidden;border-radius:var(--radius);box-shadow:var(--shadow);aspect-ratio:4/3;background:var(--navy)}.comparison-stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.comparison-after{clip-path:inset(0 calc(100% - var(--comparison-position,50%)) 0 0)}.comparison-label{position:absolute;top:1rem;z-index:2;padding:.35rem .65rem;border-radius:999px;background:rgba(7,31,43,.82);color:#fff;font-weight:900}.comparison-label-before{right:1rem}.comparison-label-after{left:1rem}.comparison-control{display:grid;gap:.35rem;margin-top:1rem}.comparison-control label{font-weight:800;color:var(--navy)}.comparison-control input{width:100%;accent-color:var(--primary)}.faq-list{display:grid;gap:1rem}.faq-list details{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1rem 1.2rem;box-shadow:0 6px 18px rgba(16,86,130,.06)}.faq-list summary{cursor:pointer;color:var(--navy);font-weight:900}.faq-list p{margin:.8rem 0 .2rem}.legal{max-width:820px}.legal h2{color:var(--navy);margin-top:2rem}
.hero-divider{height:40px;margin-top:-40px;position:relative;z-index:3;overflow:hidden;line-height:0;pointer-events:none}.hero-divider svg{display:block;width:100%;height:100%}.hero-divider path{fill:#fff}.reveal{opacity:1;transform:none}.reveal.reveal-pending{opacity:0;transform:translateY(14px);transition:opacity .42s ease,transform .42s ease}.reveal.is-visible{opacity:1;transform:none}
.site-footer{background:#071f2b;color:#c8d8df;padding:3rem 0 1.2rem}.footer-grid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:2rem}.site-footer h3{color:#fff}.site-footer a{display:block;color:#c8d8df;margin:.35rem 0}.footer-bottom{border-top:1px solid #29424e;margin-top:2rem;padding-top:1rem;text-align:center;font-size:.9rem}
@media(min-width:1401px){.container{margin-left:1rem;margin-right:auto}.concept-banner{text-align:left}}
@media(max-width:1400px){.header-row{align-items:flex-start;flex-direction:column;gap:.5rem}.nav{width:100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.nav a{width:100%}.split,.contact-grid{grid-template-columns:minmax(0,1fr)}.hero{padding:5rem 0;min-height:540px}.hero::after{background:rgba(0,175,231,.78)}.service-grid,.proof-grid,.review-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.contact-row{align-items:flex-start;flex-direction:column;min-width:0}.contact-row>*{max-width:100%}.btn{max-width:100%;white-space:normal;overflow-wrap:anywhere;text-align:center}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.topbar .container{flex-direction:column;gap:.1rem}.brand img{width:175px;height:94px}.site-header.is-condensed .header-row{gap:.25rem}.site-header.is-condensed .brand img{width:135px;height:72px}.nav{grid-template-columns:repeat(2,minmax(0,1fr))}.nav a{padding:.55rem .45rem;font-size:.86rem}.site-header.is-condensed .nav a{padding:.4rem .35rem;font-size:.8rem}main [id]{scroll-margin-top:14rem}.hero h1{font-size:2.55rem}.service-grid,.proof-grid,.review-grid,.footer-grid,.inquiry-form{grid-template-columns:minmax(0,1fr)}.form-field-full{grid-column:auto}.section{padding:3.8rem 0}.contact-row{padding:1.8rem 0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.header-row,.brand img,.nav a,.reveal.reveal-pending,.comparison-after{transition:none}.reveal.reveal-pending{opacity:1;transform:none}}
'''

JS = r'''(() => {
  const header = document.querySelector('[data-sticky-header]');
  if (header) {
    const syncHeader = () => header.classList.toggle('is-condensed', window.scrollY > 48);
    syncHeader();
    window.addEventListener('scroll', syncHeader, { passive: true });
  }

  document.querySelectorAll('[data-comparison]').forEach((comparison) => {
    const range = comparison.querySelector('input[type="range"]');
    if (!range) return;
    const sync = () => comparison.style.setProperty('--comparison-position', `${range.value}%`);
    range.addEventListener('input', sync);
    sync();
  });

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

WORKER_JS = r'''// Public audit source: hash this placeholder-bearing file; the deployed Worker substitutes that SHA-256 and returns it in x-handler-evidence-sha256.
const HANDLER_EVIDENCE_SHA256 = "__EVIDENCE_SHA256__";
const ORIGINAL_CONTACT = "https://dixonpoolsmd.com/contact/";
const MAX_BODY_BYTES = 32 * 1024;

function responsePage(status, title, message) {
  const safe = (value) => String(value).replace(/[&<>"']/g, (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  return new Response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${safe(title)} | Dixon Pool Service</title><body><div>📋 This is a free concept redesign — Dixon Pool Service's actual site is at <a href="https://dixonpoolsmd.com/">dixonpoolsmd.com</a></div><main><h1>${safe(title)}</h1><p>${safe(message)}</p><p><a href="/contact">Return to Request Service</a></p></main></body></html>`, {status, headers:{"content-type":"text/html; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff","referrer-policy":"no-referrer","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
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
      if (request.method !== "POST") return new Response("Method Not Allowed", {status:405, headers:{allow:"POST","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
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
        if meta.get('footer_only'): continue
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
<link rel="stylesheet" href="css/site.css?v=cycle3d">{structured}</head>
<body id="top"><div class="concept-banner">📋 This is a free concept redesign — {html.escape(BUSINESS)}'s actual site is at <a href="{html.escape(ORIGINAL_SITE_URL,quote=True)}" target="_blank" rel="noopener">{html.escape(ORIGINAL_SITE_URL.removeprefix('https://').removeprefix('http://').rstrip('/'))}</a></div><a class="skip" href="#main-content">Skip to main content</a>
<div class="topbar"><div class="container"><span>Frederick &amp; surrounding counties</span><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></div>
<header class="site-header" data-sticky-header><div class="container header-row"><a class="brand" href="{'#top' if home else 'index.html#top'}"><img src="{rel_asset('logo_path')}" alt="Dixon Pool Service logo"><span class="brand-copy"><strong>Dixon Pool Service</strong><span>Pool care in Frederick, Maryland</span></span></a><nav class="nav" aria-label="Main navigation">{nav(filename)}</nav></div></header>
{body}
<footer class="site-footer"><div class="container"><div class="footer-grid"><div><h3>Dixon Pool Service</h3><p>{html.escape(ADDRESS)}</p><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div><div><h3>Explore</h3><a href="about.html">About</a><a href="services.html">Services</a><a href="faq.html">FAQ</a><a href="contact.html">Contact</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Use</a></div><div><h3>Hours &amp; social</h3><p>Monday–Friday<br>8 AM–4 PM</p><a href="{FACEBOOK}">Facebook</a><a href="{TIKTOK}">TikTok</a></div></div><div class="footer-bottom">Dixon Pool Service &bull; Frederick, Maryland</div></div></footer>
<script src="assets/js/shared.js" defer></script>
</body></html>'''


def service_cards() -> str:
    cards=[]
    for service in SERVICES:
        description=SERVICE_DESCRIPTIONS.get(service)
        copy=f'<p>{html.escape(description)}</p>' if description else ''
        cards.append(f'<article class="card service-card"><h3>{html.escape(service)}</h3>{copy}</article>')
    return ''.join(cards)


def page_hero(eyebrow: str, title: str, description: str) -> str:
    image='assets/'+Path(DATA['images'][0]['local_path']).name
    return f'''<section class="page-hero"><img class="page-hero-photo" src="{image}" alt="Branded Dixon Pool Service company truck"><div class="container"><p class="eyebrow">{html.escape(eyebrow)}</p><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div></section>'''


def comparison() -> str:
    return '''<figure class="comparison" data-comparison><div class="comparison-stage"><img src="assets/pool-before.jpg" alt="Pool before Dixon Pool Service care"><img class="comparison-after" src="assets/pool-after.jpg" alt="Pool after Dixon Pool Service care"><span class="comparison-label comparison-label-after">After</span><span class="comparison-label comparison-label-before">Before</span></div><div class="comparison-control"><label for="pool-comparison">Move slider to compare before and after</label><input id="pool-comparison" type="range" min="0" max="100" value="50"></div></figure>'''


def faq_list() -> str:
    return ''.join(f'<details><summary>{html.escape(question)}</summary><p>{html.escape(answer)}</p></details>' for question,answer in FAQS)


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
    body=f'''<main id="main-content">{page_hero('About Dixon','A Frederick-area family pool service','Dixon Pool Service was established in 2005 by Thomas Dixon Sr. and serves Frederick and surrounding counties.')}<section class="section"><div class="container split"><div><div class="section-head"><h2>Who We Are</h2><p>Dixon Pool Service was established in 2005 by Thomas Dixon, Sr. A twenty-five-year veteran in the pool and spa industry. He first started in the above ground pool business and later graduated to run the largest retail pool parts department in New Jersey. Shortly after that, he discovered he had a knack for repairing the equipment customers were trying to replace.</p><p>After moving his family to Maryland, Thom started working for a small inground pool service company. Due to his efforts, the company grew and became a major force in the pool and spa industry.</p><p>Seeing that customers were not getting their customer service needs properly met, Thom started Dixon Pool Service. He was joined that first year by his son, Thomas Jr. who now manages most of the day-to-day operations.</p><p>The company grew quickly and now includes his son-in-law and grandson making this a true family business. The rest of the crew may not be family but has been with the company for years, making Dixon Pool Service the premiere pool service company in the Frederick area.</p></div><div class="actions"><a class="btn btn-navy" href="services.html">Explore services</a><a class="btn btn-primary" href="contact.html">Contact Dixon</a></div></div><img src="{img}" alt="Pool service work by Dixon Pool Service"></div></section><section class="section section-alt"><div class="container split"><img src="assets/image2.jpg" alt="Pool maintained by Dixon Pool Service"><div><div class="section-head"><h2>Why Choose Dixon?</h2><p>Dixon Pool Service does not sell just one brand of pool equipment, we sell the best models of the various categories from all the major brand names. There’s no brand loyalty. We sell superior products, along with superior service, to give our customers the superior experience!</p><p>We want our customers satisfied and happy with their service and have grown our company with this strong customer service model in place.</p><p>The pool service industry, compared to other trades is quite small and extremely specialized. You can’t get a plumber to replace your pump motor. You can’t get an electrician to re-plumb your pool filter. They don’t know why your pool keeps turning green or how to make it sparkling clear. We are plumbers, electricians, chemists and sometimes salesmen all rolled into one</p><p>Dixon Pool Service is highly rated across all major review platforms.</p></div></div></div></section></main>'''
    return shell('about.html',body)


def services_page() -> str:
    body=f'''<main id="main-content">{page_hero('Pool service list','Pool services for Frederick-area homes','Seasonal openings and closings, routine care, equipment work, and specialized pool systems.')}<section class="section"><div class="container"><div class="section-head"><h2>How Dixon can help</h2><p>Choose from the service offerings below.</p></div><div class="grid service-grid">{service_cards()}</div></div></section><section class="section section-alt"><div class="container"><div class="section-head"><p class="eyebrow">Real results</p><h2>See the Dixon difference</h2><p>Move the control to compare a real before-and-after pair from Dixon Pool Service.</p></div>{comparison()}</div></section><section class="contact-band"><div class="container contact-row"><div><h2>Ask about your pool service needs</h2><p>Call Monday through Friday, 8 AM–4 PM.</p></div><a class="btn" href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></div></section></main>'''
    return shell('services.html',body)


def faq_page() -> str:
    body=f'''<main id="main-content">{page_hero('Helpful answers','Frequently Asked Questions','Answers from Dixon Pool Service about pool care, equipment, estimates, payment, and scheduling.')}<section class="section"><div class="container"><div class="faq-list">{faq_list()}</div><div class="actions"><a class="btn btn-navy" href="contact.html">Ask a question</a></div></div></section></main>'''
    return shell('faq.html',body)


def privacy_page() -> str:
    body=f'''<main id="main-content">{page_hero('Concept preview','Privacy Policy','How information is handled on this concept redesign.')}<section class="section"><div class="container legal" data-content-lineage="approved-preview-policy"><p>This concept redesign does not intentionally store the personal information entered into its Request Service form. When you submit that form, Cloudflare Turnstile first processes anti-spam verification and the request is then sent to Dixon Pool Service’s existing contact system.</p><h2>Website analytics</h2><p>Cloudflare Web Analytics may collect limited, privacy-focused usage information about visits to this preview.</p><h2>Your choices</h2><p>You may contact Dixon Pool Service by telephone instead of using the online form. For information about the business’s own website practices, visit the <a href="{html.escape(ORIGINAL_SITE_URL,quote=True)}">actual Dixon Pool Service website</a>.</p></div></section></main>'''
    return shell('privacy.html',body)


def terms_page() -> str:
    body=f'''<main id="main-content">{page_hero('Concept preview','Terms of Use','Important information about this free concept redesign.')}<section class="section"><div class="container legal" data-content-lineage="approved-preview-policy"><p>This website is a free concept redesign and is not Dixon Pool Service’s actual website. It is provided to demonstrate a possible updated presentation of information captured from the business’s website.</p><h2>Business information</h2><p>Service availability, pricing, scheduling, and other business arrangements must be confirmed directly with Dixon Pool Service. The <a href="{html.escape(ORIGINAL_SITE_URL,quote=True)}">actual Dixon Pool Service website</a> remains the authoritative business website.</p><h2>Acceptable use</h2><p>Do not misuse this preview, attempt to interfere with its operation, or submit unlawful or abusive material through its Request Service form.</p></div></section></main>'''
    return shell('terms.html',body)


def contact_page() -> str:
    maps='https://www.google.com/maps/search/?api=1&query='+quote_plus(ADDRESS)
    body=f'''<main id="main-content">{page_hero('Get in touch','Request Pool Service','Send a service request or call during listed business hours.')}<section class="section"><div class="container grid contact-grid"><article class="card contact-card"><h2>Request Service</h2><p>This form preserves the original site's service-inquiry purpose and sends requests through Dixon Pool Service's existing contact system.</p><form class="inquiry-form" action="/api/request-service" method="post"><div class="honeypot" aria-hidden="true"><label for="company-website">Company website</label><input id="company-website" name="company_website" type="text" tabindex="-1" autocomplete="off"></div><div class="form-field"><label for="request-name">Name</label><input id="request-name" name="name" type="text" autocomplete="name" required maxlength="120"></div><div class="form-field"><label for="request-phone">Phone Number</label><input id="request-phone" name="phone" type="tel" autocomplete="tel" required maxlength="40"></div><div class="form-field form-field-full"><label for="request-email">Email Address</label><input id="request-email" name="email" type="email" autocomplete="email" required maxlength="254"></div><div class="form-field form-field-full"><label for="request-service">Service(s) Needed</label><input id="request-service" name="service" type="text" autocomplete="off" maxlength="240"></div><div class="form-field form-field-full"><label for="request-message">Message</label><textarea id="request-message" name="message" required maxlength="4000"></textarea></div><div class="form-field form-field-full"><div class="cf-turnstile" data-sitekey="{html.escape(TURNSTILE_SITEKEY, quote=True)}"></div></div><p class="form-note">Cloudflare verifies the anti-spam check, then the demo forwards your request to Dixon Pool Service's original contact system. The demo does not intentionally store inquiry details.</p><button class="btn btn-navy" type="submit">Send Service Request</button></form></article><article class="card contact-card"><h2>Contact details</h2><ul class="detail-list"><li><strong>Phone</strong><br><a href="tel:{PHONE_HREF}">{html.escape(PHONE)}</a></li><li><strong>Address</strong><br>{html.escape(ADDRESS)}<br><a href="{maps}">Open in Google Maps</a></li><li><strong>Hours</strong><br>Monday–Friday, 8 AM–4 PM</li></ul><div class="socials"><a class="btn btn-navy" href="{FACEBOOK}">Facebook</a><a class="btn btn-primary" href="{TIKTOK}">TikTok</a></div></article></div></section><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script></main>'''
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
    for role,src in BEFORE_AFTER_ASSETS.items():
        shutil.copy2(src,PUBLIC/'assets'/f'pool-{role}.jpg')
    shutil.copy2(PIPELINE_ROOT/DATA['favicon_path'],PUBLIC/'favicon.ico')
    (PUBLIC/'css'/'site.css').write_text(CSS)
    (PUBLIC/'assets'/'js'/'shared.js').write_text(JS)
    evidence_dir = PUBLIC / '.well-known'
    evidence_dir.mkdir()
    evidence = WORKER_JS
    evidence_hash = hashlib.sha256(evidence.encode()).hexdigest()
    (evidence_dir/'request-service-handler.js').write_text(evidence)
    (PUBLIC/'_worker.js').write_text(WORKER_JS.replace('__EVIDENCE_SHA256__', evidence_hash))
    outputs={'index.html':home_page(),'about.html':about_page(),'services.html':services_page(),'faq.html':faq_page(),'contact.html':contact_page(),'privacy.html':privacy_page(),'terms.html':terms_page()}
    for name,text in outputs.items(): (PUBLIC/name).write_text(text)
    urls='\n'.join(f'  <url><loc>{canonical(name)}</loc></url>' for name in PAGES)
    (PUBLIC/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (PUBLIC/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    (PUBLIC/'_redirects').write_text('/scan / 302\n')
    print(f'Built {len(outputs)} pages in {PUBLIC}')

if __name__=='__main__': build()
