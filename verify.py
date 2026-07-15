#!/usr/bin/env python3
"""Ad-hoc integrity checks for the generated Dixon preview."""
from html.parser import HTMLParser
from pathlib import Path
import json,re

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
    assert d.h1==1,(name,d.h1)
    assert d.title.strip() and d.meta.get('description'),name
    titles.append(d.title.strip())
    assert 'rel="canonical"' in text and 'property="og:title"' in text and 'name="twitter:card"' in text
    assert 'static.cloudflareinsights.com' not in text and 'data-cf-beacon' not in text
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

for path in ['assets/logo.png','assets/favicon.ico','assets/image1.jpg','assets/image2.jpg','assets/image3.jpg','favicon.ico','css/site.css']:
    p=PUBLIC/path; assert p.is_file() and p.stat().st_size>0,p

ld=re.search(r'<script type="application/ld\+json">(.*?)</script>',home_text,re.S)
assert ld
obj=json.loads(ld.group(1)); assert obj['@type']=='LocalBusiness' and 'geo' not in obj and 'email' not in obj
print('PASS: 4 pages, links, fragments, assets, SEO, verified facts, JSON-LD, and /scan rule')
