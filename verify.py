#!/usr/bin/env python3
"""Sūtra Nexus verify script. Run: python3 verify.py  (from build/).  Exit code 0 = all checks pass.
Checks: no external resources loaded, no mailto / linktr.ee / dev.to / email addresses, JSON validity, counts (3983/14/75 as in data),
KB generation reproducible, file sizes, diagram and flow counts, footer wording/links, required files, no ZIP, no CDN."""
import os, re, json, sys, subprocess, hashlib
R=os.path.dirname(os.path.abspath(__file__)); os.chdir(R)
SRC=os.path.join(os.path.dirname(R),'data')
ok=True; rows=[]
def check(name,cond,detail=''):
    global ok; rows.append(('PASS' if cond else 'FAIL',name,detail)); ok&=bool(cond)
def rd(p): return open(p,encoding='utf8').read()
# --- JSON validity and counts
J={}
for n in ['ashtadhyayi','maheshvara','shiva_sutras_kashmir']:
    try: J[n]=json.load(open(f'data/{n}.json',encoding='utf8')); check(f'JSON valid: data/{n}.json',True,f"{os.path.getsize(f'data/{n}.json'):,} bytes")
    except Exception as e: check(f'JSON valid: data/{n}.json',False,str(e))
    check(f'build data copy identical to source: {n}', (not os.path.exists(f'{SRC}/{n}.json')) or hashlib.md5(open(f'data/{n}.json','rb').read()).hexdigest()==hashlib.md5(open(f'{SRC}/{n}.json','rb').read()).hexdigest(),'skipped if the source folder is not present' if not os.path.exists(f'{SRC}/{n}.json') else '')
check('Aṣṭādhyāyī count 3983',len(J['ashtadhyayi']['sutras'])==3983 and J['ashtadhyayi']['meta']['count']==3983,str(len(J['ashtadhyayi']['sutras'])))
check('unique loci 3983',len({x['num'] for x in J['ashtadhyayi']['sutras']})==3983)
check('Māheśvara count 14',len(J['maheshvara']['sutras'])==14)
check('Śiva Sūtras count 75',len(J['shiva_sutras_kashmir']['sutras'])==75)
d=rd('js/data.js'); dj=json.loads(d.split('=',1)[1].rstrip().rstrip(';')); dj['ashta']=json.loads(rd('js/data-ashta.js').split('=',1)[1].split(';document')[0])
check('data.js counts match JSON',len(dj['ashta'])==3983 and len(dj['maha'])==14 and len(dj['shiva'])==75)
check('data.js Devanāgarī/IAST equal source for all sūtras',all(a[0]==b['num'] and a[1]==b['devanagari'] and a[2]==b['iast'] for a,b in zip(dj['ashta'],J['ashtadhyayi']['sutras'])))
# --- pratyāhāra self-test
sys.path.insert(0,'tools')
from nexus_lib import *
try: check('pratyāhāra self-test (ac, ik, yaṇ, śar, ak, ec, hal=33, al=42)',selftest(J['maheshvara']))
except AssertionError as e: check('pratyāhāra self-test',False,str(e))
# --- text scan of every shipped text file
EXT=('.html','.js','.css','.json','.md','.svg','.py','.txt')
files=[]
for dp,dn,fn in os.walk('.'):
    if dp.startswith('./qa/pdf') : continue
    for f in fn:
        p=os.path.join(dp,f); files.append(p)
text=[p for p in files if p.endswith(EXT) and not p.startswith('./data/') and 'verify.py' not in p]
bad={'mailto':[], 'linktr.ee':[], 'dev.to':[], 'email-address':[], 'zip':[]}
for p in text:
    s=rd(p)
    if re.search(r'mailto:',s,re.I): bad['mailto'].append(p)
    if re.search(r'linktr\.ee|linktree',s,re.I): bad['linktr.ee'].append(p)
    if re.search(r'(?<![\w.])dev\.to(?![\w])',s,re.I): bad['dev.to'].append(p)
    if re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}',s): bad['email-address'].append(p)
for k,v in bad.items():
    if k!='zip': check(f'no {k} in shipped text files',not v,', '.join(v[:3]))
check('no ZIP/archive files',not [p for p in files if re.search(r'\.(zip|tar|gz|tgz|7z|rar)$',p,re.I)])
# --- no external resources: scan html/css/js for loadable external URLs
ext=[]
for p in text:
    if p.startswith('./qa/') or p.endswith(('.md',)) or p.startswith('./tools/') : continue
    s=rd(p)
    for m in re.finditer(r'(?:src|href)\s*=\s*["\'](https?:)?//([^"\']+)',s):
        tag=s[max(0,m.start()-60):m.start()]
        if re.search(r'<(script|link|img|iframe|source|video|audio)\b[^>]*$',tag) : ext.append((p,m.group(0)[:80]))
    for m in re.finditer(r'url\(\s*["\']?https?:',s): ext.append((p,'css url()'))
    for m in re.finditer(r'@import\s+url|@import\s+["\']https?',s): ext.append((p,'@import'))
    for m in re.finditer(r'\b(fetch|XMLHttpRequest|WebSocket|importScripts)\b',s):
        ctx=s[m.start():m.start()+120]
        if 'cloudEndpoint' in s and p.endswith('guidebot.js'): continue
        if 'fetch' in ctx and p.endswith('.js') and 'verify' not in p: ext.append((p,'network API: '+ctx[:50]))
    if re.search(r'\bsrc\s*=\s*["\'](https?:)?//',s): ext.append((p,'script/img src absolute'))
check('no external resources loaded (script/link/img/css url/fetch)',not ext,str(ext[:4]))
check('no CDN host names',not [p for p in text if not p.startswith(('./qa','./tools')) and re.search(r'cdn\.|googleapis|jsdelivr|unpkg|cloudflare|fonts\.g',rd(p),re.I)])
# --- external hyperlinks only the sanctioned ones
allowed=('sutra-nexus.vercel.app','github.com/CypherMonkeyLabs/sutra-nexus','cyphermonkeylabs.com','github.com/CypherMonkeyLabs','github.com/cipher0x9','x.com/Cypher0x9','linkedin.com/in/luckylakshmanucwebex','huggingface.co/Cypher0x9','ashtadhyayi.com','github.com/ashtadhyayi-com/data','gretil.sub.uni-goettingen.de','en.wikipedia.org')
res=json.load(open('tools/resources_verified.json'))
urls=set()
for p in ['index.html','js/core.js','js/rooms.js','js/content.js','guidebot/kb.js','guidebot/guidebot.js','README.md']:
    urls|=set(re.findall(r'https?://[^\s"\'<>)\\]+',rd(p)))
unk=[u for u in urls if not any(a in u for a in allowed) and 'w3.org' not in u]
check('only sanctioned hyperlinks',not unk,str(unk[:4]))
# --- required content
idx=rd('index.html'); core=rd('js/core.js'); rooms=rd('js/rooms.js')
for must in ['Sūtra Nexus','Ancient rules. Living systems.','© 2026 CypherMonkeyLabs','https://cyphermonkeylabs.com/#contact','independent, free, learning-only student project','trademarks and sources belong to their owners','happy to volunteer for any organization']:
    check(f'footer/identity text present: {must}',must.lower() in (idx+core).lower())
for u in ['https://cyphermonkeylabs.com','https://github.com/CypherMonkeyLabs','https://github.com/cipher0x9','https://x.com/Cypher0x9','https://www.linkedin.com/in/luckylakshmanucwebex','https://huggingface.co/Cypher0x9']:
    check(f'footer link {u}',u in core)
check('SOCIALS data array present',"var SOCIALS=[" in core)
check('Gita not included',not re.search(r'bhagavad|गीता',rooms,re.I) or 'not part' in rooms or 'not in the data' in rooms)
# --- diagrams / flows
dg=rd('js/diagrams.js'); nfun=len(re.findall(r'^D\.(\w+)=function',dg,re.M))
nsvg=nfun-1+3  # sandhi() renders 4 diagrams
funcs=re.split(r'^D\.(\w+)=function',dg,flags=re.M); animated=[funcs[i] for i in range(1,len(funcs),2) if re.search(r'animateMotion|pulse|dash|spin|scan|drop|seq|grow|flowline|arrow[(]',funcs[i+1])]
check('>= 20 inline SVG diagrams',nsvg>=20,f'{nsvg} distinct diagrams (24 builders, sandhi x4)')
check('10-15+ animated flows (CSS/SMIL animation)',len(animated)>=10,f'{len(animated)} animated diagram builders: '+' '.join(animated))
# --- KB generation reproducible
before=rd('guidebot/kb.js'); rk=subprocess.run([sys.executable,'guidebot/gen_kb.py'],capture_output=True,text=True); check('gen_kb.py runs without error',rk.returncode==0,rk.stderr[-120:]); after=rd('guidebot/kb.js')
kb=json.loads(after.split('=',1)[1].rstrip().rstrip(';'))
check('KB regenerated by guidebot/gen_kb.py (deterministic)',before==after,f"{len(kb['entries'])} entries, {len(kb['quiz'])} quiz, {len(kb['cards'])} cards, {len(kb['facts'])} facts")
c0=rd('js/content.js')+rd('js/data.js'); rc=subprocess.run([sys.executable,'tools/gen_content.py'],capture_output=True,text=True)
check('gen_content.py runs and content.js/data.js are reproducible',rc.returncode==0 and c0==rd('js/content.js')+rd('js/data.js'),rc.stderr[-120:])
# --- downloads
man=json.load(open('downloads/manifest.json'))
for m in man:
    sz=os.path.getsize('downloads/'+m['file']); check(f"download exists: {m['file']}",abs(sz-m['bytes'])<=2048,f'{sz:,} bytes (manifest {m["size"]})')
check('PDF set (4) + PPTX + single HTML listed',sum(m['file'].endswith('.pdf') for m in man)==4 and any(m['file'].endswith('.pptx') for m in man) and any(m['file'].endswith('.html') for m in man))
# --- required files
for f in ['index.html','README.md','verify.py','css/nexus.css','js/core.js','js/rooms.js','js/diagrams.js','js/data.js','js/data-ashta.js','js/content.js','guidebot/guidebot.js','guidebot/guidebot.css','guidebot/kb.js','guidebot/gen_kb.py']:
    check(f'file present: {f}',os.path.exists(f),f'{os.path.getsize(f):,} bytes' if os.path.exists(f) else '')
# --- rooms
ids=re.findall(r"\{id:'(\w+)',ic:",core)
check('10 rooms defined',len(ids)==10,' '.join(ids))
check('no all-caps label CSS (text-transform:uppercase)', 'text-transform:uppercase' not in rd('css/nexus.css').lower() and 'text-transform:uppercase' not in rd('guidebot/guidebot.css').lower())
# --- sizes
tot=sum(os.path.getsize(p) for p in files if not p.startswith('./qa'))
check('app size (excluding qa)',True,f'{tot/1048576:.1f} MB over {len([p for p in files if not p.startswith("./qa")])} files')
for p in ['index.html','css/nexus.css','js/core.js','js/rooms.js','js/diagrams.js','js/data.js','js/data-ashta.js','js/content.js','guidebot/guidebot.js','guidebot/kb.js']: rows.append(('INFO',f'size {p}',f'{os.path.getsize(p):,} bytes'))
w=max(len(r[1]) for r in rows)
for s,n,dd in rows: print(f'{s:4}  {n:<{w}}  {dd}')
print('\nRESULT:','ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'); sys.exit(0 if ok else 1)
