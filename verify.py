#!/usr/bin/env python3
"""Ad-hoc integrity checks for the generated Dixon preview."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib,json,re,struct

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
PAGES=['index.html','about.html','services.html','contact.html']

class Doc(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=set(); self.hrefs=[]; self.srcs=[]; self.h1=0; self.title=''; self.in_title=False; self.meta={}; self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        if tag=='a': self.hrefs.append(a.get('href'))
        if tag in ('img','script') and a.get('src'): self.srcs.append(a['src'])
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
    assert d.srcs.count('assets/js/shared.js')==1,(name,d.srcs)
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

home_text=(PUBLIC/'index.html').read_text()
for value in ('(301) 607-1011','9506 Hansonville Rd','4.8','17 Google reviews','2005'):
    assert value in home_text,value
for forbidden in ('fulfillment@alphamediausa.com','39.493658','-77.398795','Saturday','Sunday'):
    assert forbidden not in ''.join((PUBLIC/p).read_text() for p in PAGES),forbidden

for path in ['assets/logo.png','assets/favicon.ico','assets/Dixon-Pool-Van-scaled.jpg','assets/image1.jpg','assets/image2.jpg','assets/image3.jpg','assets/js/shared.js','favicon.ico','css/site.css']:
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
css=(PUBLIC/'css'/'site.css').read_text()
for color in ('#00afe7','#2ea3f2','#105682','#bfebf9'): assert color in css,color
assert 'border-bottom:4px solid var(--secondary)' in css
assert '.concept-banner{' in css
assert '.brand img{width:220px;height:118px' in css
assert '.site-header{background:#fff;border-bottom:1px solid var(--line);position:sticky' in css
assert '.site-header.is-condensed .brand img{' in css
assert '.hero-divider{' in css and '.reveal{opacity:1;transform:none}' in css
assert '@media(prefers-reduced-motion:reduce)' in css
js=(PUBLIC/'assets'/'js'/'shared.js').read_text()
for marker in ("classList.toggle('is-condensed'",'new IntersectionObserver','prefers-reduced-motion: reduce',"classList.add('reveal', 'reveal-pending')",'const revealPassed = () =>'):
    assert marker in js,marker
print('PASS: 4 pages, mandatory concept banners, casual UX polish, shared behavior, links, fragments, assets, SEO, verified facts, JSON-LD, and /scan rule')
