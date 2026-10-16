"""Cheat-sheet PDFs via the cypher-visual-forge print kit (pastel, A4, one-sided friendly). Output: build/downloads/*.pdf"""
import sys, os, json, subprocess, html
sys.path.insert(0,'/workspace/visual-craft/masters/cypher-visual-forge/templates')
from forge import *
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import *
OUT=f'{ROOT}/downloads'; os.makedirs(OUT,exist_ok=True); TMP='/tmp/nexus_pdf'; os.makedirs(TMP,exist_ok=True)
C=json.loads(open(f'{ROOT}/js/content.js',encoding='utf8').read().split('=',1)[1].rstrip().rstrip(';'))
A=load('ashtadhyayi');M=load('maheshvara');K=load('shiva_sutras_kashmir')
S={x['num']:x for x in A['sutras']}
FOOT='Sūtra Nexus · Ancient rules. Living systems. · © 2026 CypherMonkeyLabs'
LEGAL=('<div style="font-size:7pt;line-height:1.35;color:var(--mute);border-top:1px dashed var(--line);padding-top:2mm;margin-top:auto">'
 'Sūtra Nexus is an independent, free, learning-only student project. It respects every company, tradition and vendor; trademarks and sources belong to their owners. '
 'If something should be removed or corrected, it will be handled promptly via https://cyphermonkeylabs.com/#contact. Nothing here is sold; happy to volunteer for any organization. '
 'Sources: ashtadhyayi-com/data (free to use with credit) and GRETIL (Śiva Sūtras, ed. Madhusudan Kaul Shastri 1925, input O. Hellwig). Transliteration is machine-converted and not checked by a person. '
 'CypherMonkey Labs https://cyphermonkeylabs.com · GitHub https://github.com/CypherMonkeyLabs · X https://x.com/Cypher0x9 · LinkedIn https://www.linkedin.com/in/luckylakshmanucwebex · Hugging Face https://huggingface.co/Cypher0x9 · GitHub https://github.com/cipher0x9 · © 2026 CypherMonkeyLabs</div>')
DV='font-family:var(--dev,"Noto Sans Devanagari",sans-serif)'
def dv(s,size='11pt'): return f'<span style=\'font-family:"Noto Sans Devanagari","Mangal",sans-serif;font-size:{size}\'>{html.escape(s)}</span>'
def build(name,title,sub,sheets,kicker='Sūtra Nexus · cheat sheet'):
    top=f'<div><span class="kicker">{kicker}</span><div style="font-family:var(--font-display);font-size:26pt;font-weight:900;color:var(--c1);line-height:1.05;margin:2mm 0">{title}</div><div style="height:1.6mm;width:34mm;border-radius:2mm;background:linear-gradient(90deg,var(--c1),var(--c2));margin:1mm 0 2mm"></div><p style="margin:0;color:var(--mute)">{sub}</p></div>'
    import re as _re
    pages=[sheet((top+_re.sub(r'<header class="sec-band".*?</header>','',s,count=1,flags=_re.S) if i==0 else s)+LEGAL) for i,s in enumerate(sheets)]
    h=doc(title,pages,domain='d-07',foot=FOOT,date='2026-10',head_extra='<style>*{text-transform:none!important;font-variant:normal!important}th{letter-spacing:0!important}.kicker{letter-spacing:.02em!important}</style>')
    f=f'{TMP}/{name}.html'; open(f,'w',encoding='utf8').write(h)
    r=subprocess.run(['python3','/workspace/visual-craft/masters/cypher-visual-forge/templates/pdf_render.py','pdf',f,f'{TMP}/{name}.pdf'],capture_output=True,text=True)
    import shutil; shutil.copyfile(f'{TMP}/{name}.pdf',f'{OUT}/{name}.pdf'); qd=f'{ROOT}/qa/pdf/{name}'; os.makedirs(qd,exist_ok=True)
    for fn in os.listdir(f'{TMP}/{name}_qa'): 
        if fn.endswith('.png'): shutil.copyfile(f'{TMP}/{name}_qa/{fn}',f'{qd}/{fn}')
    print(name,r.stdout[-300:],r.stderr[-300:])
# 1 pratyahara
rows=[[str(l['n']),dv(l['devanagari']),l['iast'],' '.join(l['sounds']),f"<b>{l['marker']}</b>"] for l in M['sutras']]
p1=sec_band('l','The 14 Māheśvara lines','Each line ends with a marker (it) that is not counted in a sound set.')+table(['Line','Devanāgarī','IAST','Sounds','Marker'],rows)+'<p style="font-size:9pt">Rule behind pratyāhāras: sūtra 1.1.71 ādirantyena sahetā. A first letter with a final marker names itself and every sound between them. Meaning of the lines: UNKNOWN in source beyond this structure.</p>'
common=['ak','ac','ec','ik','yaṇ','jhal','hal','al','śar','jhaś','vaś','yar','khar','jhay','aṇ']
pr=C['prat']; rowsp=[]
for nm in common:
    for p in [x for x in pr if x['name']==nm]:
        rowsp.append([f"<b>{nm}</b>",f"{p['start']} (line {p['start_line']}) → {p['marker']} (line {p['marker_line']})",str(len(p['sounds'])),' '.join(p['sounds'])])
p2=sec_band('c','Common pratyāhāras, computed','Computed from the 14 lines; hal, al, ac, ik, yaṇ and śar match the standard textbook sets.')+table(['Name','From → to marker','Count','Sounds'],rowsp)+'<p style="font-size:9pt">Names that fit two markers (for example aṇ with ṇ in line 1 or line 6) are listed separately. Which one is meant depends on the sūtra that uses it.</p>'
build('sutra-nexus-pratyahara-cheat-sheet','Pratyāhāra cheat sheet','The 14 lines and the sets they make',[p1,p2])
# 2 sounds
V=' '.join(f'<span class="chip">{dv(a,"13pt")} {b}</span>' for a,b in C['vow'])
cr=[[C['varga'][i]]+[f"{dv(c[0],'13pt')} {c[1]}" for c in r] for i,r in enumerate(C['cons'])]
cr.append(['y r l v']+[f"{dv(c[0],'13pt')} {c[1]}" for c in C['semi']]+['']); cr.append(['ś ṣ s h']+[f"{dv(c[0],'13pt')} {c[1]}" for c in C['sib']]+[''])
q1=sec_band('s','Sounds and scripts','Devanāgarī and IAST side by side.')+'<div style="margin:2mm 0">'+V+'</div>'+table(['Row','1','2','3','4','5'],cr)+'<p style="font-size:9pt">Standard textbook tables (not from the three data files).</p>'
q2=sec_band('t','Sthāna: where sounds are made','Textbook summary of the places of articulation.')+table(['Sthāna','Sounds'],[[a,b] for a,b,_ in C['sthana']])+'<h3>Prayatna: how they are made</h3>'+table(['Group','Sounds'],[['Sparśa (touch)','k to m, the 25 in five rows'],['Antaḥstha (semivowels)','y r l v'],['Ūṣman','ś ṣ s h'],['Svara (vowels)','a ā i ī u ū ṛ ṝ ḷ e ai o au'],['Aghoṣa / ghoṣa','unvoiced: 1st and 2nd of each row, ś ṣ s / voiced: 3rd, 4th, 5th, y r l v h and vowels'],['Alpaprāṇa / mahāprāṇa','1st, 3rd, 5th / 2nd, 4th']])
build('sutra-nexus-sound-and-sthana-chart','Sound and sthāna chart','Scripts, places and manner of articulation',[q1,q2])
# 3 types
T=C['stats']['types'];tn={'V':'vidhi (operative rule)','S':'saṃjñā (definition)','P':'paribhāṣā (rule for reading rules)','AD':'code AD, not expanded in the data','AT':'code AT, not expanded in the data'}
t1=sec_band('y','Sūtra types','Counts computed from the Aṣṭādhyāyī data.')+table(['Code','Meaning','Count'],[[k,tn[k],f'{T[k]:,}'] for k in ['V','S','AT','AD','P']])+'<h3>Sūtras per adhyāya</h3>'+table(['Adhyāya']+[str(i) for i in range(1,9)]+['Total'],[['Sūtras']+[str(C['stats']['adhyaya'][str(i)]) for i in range(1,9)]+[f"{C['stats']['total']:,}"],['With anuvṛtti']+[str(C['stats']['anu'][str(i)]) for i in range(1,9)]+[f"{C['stats']['withAnu']:,}"]])+'<p style="font-size:9pt">Locus 6.1.77 = adhyāya 6 · pāda 1 · sūtra 77. Anuvṛtti: words carried forward from earlier sūtras so that short sūtras stay short.</p>'
ex=[[n,dv(S[n]['devanagari']),S[n]['iast'],S[n]['type'],' · '.join(S[n]['anuvritti']) or 'none',C['bridges'][n]] for n in C['bridges']]
t2=sec_band('e','Well-known sūtras','Text and type from the data; the last column is a bridge idea (an interpretation).')+table(['Locus','Devanāgarī','IAST','Type','Anuvṛtti','Bridge idea'],ex)+'<p style="font-size:9pt">English meaning from source: UNKNOWN. Edition and translator for any gloss: UNKNOWN.</p>'
build('sutra-nexus-sutra-type-guide','Sūtra type guide','Types, structure and well-known sūtras',[t1,t2])
# 4 Shiva one pager
def rows_(items): return ''.join(f'<div style="display:flex;gap:1.5mm;border-bottom:.2mm solid var(--line);padding:.1mm 0;font-size:6.2pt;line-height:1.15"><b style="color:var(--c1);min-width:6.5mm;flex:none">{x["num"]}</b><span style=\'font-family:"Noto Sans Devanagari",sans-serif;min-width:17mm;flex:none\'>{html.escape(x["devanagari"])}</span><span style="min-width:0;overflow-wrap:anywhere">{html.escape(x["iast"])}</span></div>' for x in items)
U={u:[x for x in K['sutras'] if x['unmesha']==u] for u in (1,2,3)}
one=sec_band('k','Śiva Sūtras (75)','Vārttika-recension numbering: 20 + 10 + 45. Meanings: UNKNOWN in source.')+'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm"><div><b>Unmeṣa 1 (20)</b>'+rows_(U[1])+'<b style="display:block;margin-top:2mm">Unmeṣa 2 (10)</b>'+rows_(U[2])+'</div><div><b>Unmeṣa 3 (45), part 1</b>'+rows_(U[3][:23])+'</div><div><b>Unmeṣa 3, part 2</b>'+rows_(U[3][23:])+'</div></div><p style="font-size:7.5pt;margin:1mm 0">Source: GRETIL, ed. Madhusudan Kaul Shastri 1925, input O. Hellwig. The file’s meta note says the common Kṣemarāja recension counts 22 + 10 + 45; which sūtras differ is UNKNOWN beyond the source. Devanāgarī is machine-converted from IAST and unverified. No translation included.</p>'
build('sutra-nexus-shiva-sutras-one-pager','Śiva Sūtras one-pager','All 75 sūtras of the Kashmir text on one sheet',[one])
