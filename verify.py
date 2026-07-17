#!/usr/bin/env python3
"""Ad-hoc integrity checks for the generated Dixon preview."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib,json,re,struct

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
PAGES=['index.html','about.html','services.html','faq.html','contact.html','privacy.html','terms.html']
DATA=json.loads(Path('/home/chris/pitch-pipeline/01_scraped/dixon-pool-service.json').read_text())

class Doc(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=set(); self.hrefs=[]; self.srcs=[]; self.stylesheets=[]; self.scripts=[]; self.h1=0; self.title=''; self.in_title=False; self.meta={}; self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='a': self.hrefs.append(a.get('href'))
        if tag=='link' and a.get('rel')=='stylesheet': self.stylesheets.append(a.get('href'))
        if tag in ('img','script') and a.get('src'): self.srcs.append(a['src'])
        if tag=='script': self.scripts.append(a)
        if tag=='img': self.images.append(a)
        if tag=='h1': self.h1+=1
        if tag=='title': self.in_title=True
        if tag=='meta' and a.get('name'): self.meta[a['name']]=a.get('content','')
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
    def handle_data(self,data):
        if self.in_title: self.title+=data

def local_target(page,ref):
    clean=ref.split('?',1)[0]
    path,_,frag=clean.partition('#')
    if not path: target=page
    else: target=PUBLIC/path
    return target,frag

assert sorted(p.name for p in PUBLIC.glob('*.html'))==sorted(PAGES)
assert (PUBLIC/'_redirects').read_text()=='/scan / 302\n'
assert '/scan' not in (PUBLIC/'sitemap.xml').read_text()
assert 'User-agent:' in (PUBLIC/'robots.txt').read_text()

docs={}
titles=[]
for name in PAGES:
    page=PUBLIC/name; text=page.read_text(); d=Doc(); d.feed(text); docs[name]=d
    banners=re.findall(r'<div class="concept-banner">(.*?)</div>',text,re.S)
    assert len(banners)==1,(name,len(banners))
    assert "This is a free concept redesign — Dixon Pool Service's actual site is at" in re.sub(r'<[^>]+>','',banners[0]),name
    assert re.findall(r'href="([^"]+)"',banners[0])==['https://dixonpoolsmd.com/'],name
    assert re.search(r'<body[^>]*><div class="concept-banner">',text),name
    assert re.search(r'<html[^>]*data-presentation-tier="casual"[^>]*>',text),name
    assert not re.search(r'<body[^>]*data-presentation-tier=',text),name
    assert d.h1==1,(name,d.h1)
    assert d.title.strip() and d.meta.get('description'),name
    titles.append(d.title.strip())
    assert 'rel="canonical"' in text and 'property="og:title"' in text and 'name="twitter:card"' in text
    assert 'static.cloudflareinsights.com' not in text and 'data-cf-beacon' not in text
    assert not re.search(r'<style\b',text,re.I),name
    assert not re.search(r'\sstyle=["\']',text,re.I),name
    assert d.stylesheets==['css/site.css?v=cycle3d'],(name,d.stylesheets)
    assert d.srcs.count('assets/js/shared.js')==1,(name,d.srcs)
    assert all(script.get('src') or script.get('type')=='application/ld+json' for script in d.scripts),name
    assert text.count('class="hero-divider hero-divider--wave"')==1,name
    assert text.count('data-sticky-header')==1,name
    assert not any(h is None or h=='' or h.lower().startswith('javascript:') for h in d.hrefs)
    assert all(img.get('alt','').strip() for img in d.images),name
    for ref in d.hrefs+d.srcs:
        if not ref or re.match(r'^(https?:|mailto:|tel:)',ref): continue
        target,frag=local_target(page,ref)
        assert target.exists(),(name,ref,target)
        if frag:
            td=d if target==page else Doc();
            if target!=page: td.feed(target.read_text())
            assert frag in td.ids,(name,ref,frag)
assert len(set(titles))==len(PAGES)

home=docs['index.html']
for ident in ('top','services','why-dixon','reviews','contact'): assert ident in home.ids
for href in ('#top','#services','#contact'): assert href in home.hrefs
for name in PAGES[1:]: assert 'index.html#top' in docs[name].hrefs
for name in PAGES:
    for href in ('about.html','services.html','faq.html','contact.html','privacy.html','terms.html'):
        assert href in docs[name].hrefs,(name,href)

home_text=(PUBLIC/'index.html').read_text()
for value in ('(301) 607-1011','9506 Hansonville Rd','4.8','17 Google reviews','2005'):
    assert value in home_text,value
for forbidden in ('fulfillment@alphamediausa.com','39.493658','-77.398795','Saturday','Sunday'):
    assert forbidden not in ''.join((PUBLIC/p).read_text() for p in PAGES),forbidden

for path in ['assets/logo.png','assets/favicon.ico','assets/Dixon-Pool-Van-scaled.jpg','assets/image1.jpg','assets/image2.jpg','assets/image3.jpg','assets/pool-before.jpg','assets/pool-after.jpg','assets/js/shared.js','favicon.ico','css/site.css','_worker.js','.well-known/request-service-handler.js']:
    p=PUBLIC/path; assert p.is_file() and p.stat().st_size>0,p

logo=PUBLIC/'assets/logo.png'
with logo.open('rb') as f:
    assert f.read(8)==b'\x89PNG\r\n\x1a\n'
    length=struct.unpack('>I',f.read(4))[0]; assert f.read(4)==b'IHDR' and length==13
    width,height=struct.unpack('>II',f.read(8))
assert (width,height)==(1831,1112),(width,height)
assert hashlib.sha256(logo.read_bytes()).hexdigest()=='023bbdabc7b8bce4139236cda5c8b4b223deded3a432b93e14009758f18cedd4'

ld=re.search(r'<script type="application/ld\+json">(.*?)</script>',home_text,re.S)
assert ld
obj=json.loads(ld.group(1)); assert obj['@type']=='LocalBusiness' and 'geo' not in obj and 'email' not in obj
assert 'class="hero-photo" src="assets/Dixon-Pool-Van-scaled.jpg"' in home_text
assert 'alt="Branded Dixon Pool Service company truck"' in home_text
for name in PAGES[1:]:
    page_text=(PUBLIC/name).read_text()
    assert 'class="page-hero-photo" src="assets/Dixon-Pool-Van-scaled.jpg"' in page_text,name
    assert 'alt="Branded Dixon Pool Service company truck"' in page_text,name

services=(PUBLIC/'services.html').read_text()
source_services=Path('/home/chris/pitch-pipeline/01_scraped/dixon-pool-service-assets/source/services.html').read_text()
assert DATA['faq_page_authorized'] is True and len(DATA['faq_pairs']) == 11
pair=DATA['before_after_pairs'][0]
assert pair['id']=='services-weekly-maintenance-pair-1' and pair['approved'] is True
assert 'dsm_before_after_image_1' in source_services
for copy in (
    'Opening an in-ground swimming pool can be a daunting task.',
    'Pool closings are the most important service that we offer.',
    'For those of you who just want to swim and not have to deal with the pool',
    'Looking to adjust your pool pump, or control your pool or spa temperatures',
    'Pool heater tune-up, repair, and troubleshooting can be a very daunting task',
    'Need a New Safety Cover for Your Pool?',
):
    assert copy in source_services,copy
    assert copy in services,copy
assert services.count('data-comparison')==1
assert '<input id="pool-comparison" type="range" min="0" max="100" value="50">' in services
assert 'assets/pool-before.jpg' in services and 'assets/pool-after.jpg' in services
for role,name in [('before','pool-before.jpg'),('after','pool-after.jpg')]:
    source=Path('/home/chris/pitch-pipeline')/pair[role]['local_path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==pair[role]['sha256'],name
    assert (PUBLIC/'assets'/name).read_bytes()==source.read_bytes(),name

about=(PUBLIC/'about.html').read_text()
source_about=Path('/home/chris/pitch-pipeline/01_scraped/dixon-pool-service-assets/source/about.html').read_text()
for copy in ('Dixon Pool Service was established in 2005 by Thomas Dixon, Sr.','Seeing that customers were not getting their customer service needs properly met','The company grew quickly and now includes his son-in-law and grandson','Dixon Pool Service does not sell just one brand of pool equipment'):
    assert copy in source_about,copy
    assert copy in about,copy

faq=(PUBLIC/'faq.html').read_text()
assert faq.count('<details>')==11 and faq.count('<summary>')==11
for question in ('Do you clean pools?','Do you replace pool equipment?','Do you re-plaster pools?','Do you give free estimates?','Do you deliver pool water?','Do you work on above ground pools?','Do you have a store?','Do you install safety covers?','Do you offer weekly pool service?','Do you take credit cards?','When should I open my pool?'):
    assert question in source_services,question
    assert question in faq,question
assert '<h1>Privacy Policy</h1>' in (PUBLIC/'privacy.html').read_text()
assert '<h1>Terms of Use</h1>' in (PUBLIC/'terms.html').read_text()
for name in ('privacy.html','terms.html'):
    assert 'class="container legal" data-content-lineage="approved-preview-policy"' in (PUBLIC/name).read_text(),name
css=(PUBLIC/'css'/'site.css').read_text()
for color in ('#00afe7','#2ea3f2','#105682','#bfebf9'): assert color in css,color
assert 'border-bottom:4px solid var(--secondary)' in css
assert '.concept-banner{' in css
assert '.brand img{width:220px;height:118px' in css
assert '.site-header{background:#fff;border-bottom:1px solid var(--line);position:sticky' in css
assert '.site-header.is-condensed .brand img{' in css
assert '.hero-divider{' in css and '.reveal{opacity:1;transform:none}' in css
assert '@media(prefers-reduced-motion:reduce)' in css
for responsive in ('overflow-x:clip','repeat(3,minmax(0,1fr))','repeat(2,minmax(0,1fr))','overflow-wrap:anywhere'):
    assert responsive in css,responsive
evidence=PUBLIC/'.well-known/request-service-handler.js'
evidence_hash=hashlib.sha256(evidence.read_bytes()).hexdigest()
assert '__EVIDENCE_SHA256__' in evidence.read_text()
js=(PUBLIC/'assets'/'js'/'shared.js').read_text()
for marker in ("classList.toggle('is-condensed'",'new IntersectionObserver','prefers-reduced-motion: reduce',"classList.add('reveal', 'reveal-pending')",'const revealPassed = () =>',"querySelectorAll('[data-comparison]')",'--comparison-position'):
    assert marker in js,marker

contact=(PUBLIC/'contact.html').read_text()
assert '<h1>Request Pool Service</h1>' in contact
assert '<h2>Request Service</h2>' in contact
form=re.search(r'<form class="inquiry-form" action="/api/request-service" method="post">(.*?)</form>',contact,re.S)
assert form
form_html=form.group(1)
for field,label in [('name','Name'),('phone','Phone Number'),('email','Email Address'),('service','Service(s) Needed'),('message','Message')]:
    assert f'name="{field}"' in form_html,(field,'missing field')
    assert label in form_html,(field,'missing label')
for required in ('name','phone','email','message'):
    assert re.search(rf'name="{required}"[^>]*required',form_html),(required,'not required')
assert 'name="company_website"' in form_html and 'type="submit">Send Service Request</button>' in form_html
assert 'class="cf-turnstile"' in form_html and 'data-sitekey=' in form_html
assert 'https://challenges.cloudflare.com/turnstile/v0/api.js' in contact
worker=(PUBLIC/'_worker.js').read_text()
for marker in ('url.pathname === "/api/request-service"','request.method !== "POST"','status:405','responsePage(422','ORIGINAL_CONTACT','et_pb_contact_name_0','_wpnonce-et-pb-contact-form-submitted-0','et_pb_contact_captcha_0','TURNSTILE_SECRET','turnstile/v0/siteverify','request.body.getReader()','total > maxBytes','origin !== new URL(request.url).origin','plain === "Thanks for contacting us"','formStillPresent','env.ASSETS.fetch(request)'):
    assert marker in worker,marker
assert 'chris@leadfilament.com' not in worker and 'preventDefault' not in contact
assert evidence_hash in worker
assert 'x-handler-evidence-sha256' in worker
for control in ('request.body.getReader()','const ORIGINAL_CONTACT = "https://dixonpoolsmd.com/contact/"','catch (error)','plain === "Thanks for contacting us"','formStillPresent'):
    assert control in evidence.read_text(),control
for key,record in DATA['colors']['evidence'].items():
    source=Path('/home/chris/pitch-pipeline')/record['source_path']
    assert source.is_file(),(key,source)
    source_text=source.read_text().lower()
    assert record['value'].lower() in source_text,(key,record['value'])
    assert record['selector'] and record['property'] and record['original_role'],key
print('PASS: 7 pages, sourced About/Services/FAQ copy, accessible before/after comparison, subpage hero media, legal pages, mandatory concept banners, hardened Request Service bridge, casual UX polish, links, assets, SEO, JSON-LD, and /scan rule')
