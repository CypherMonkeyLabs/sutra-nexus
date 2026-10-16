"""Generates build/js/data.js (compact copy of the three data files) and build/js/content.js
(glossary, bridge ideas, sound tables, flashcards, quiz bank, curriculum, resources). Single source of truth for the app AND the guide bot KB."""
import json, random, shutil, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import *
A=load('ashtadhyayi'); M=load('maheshvara'); K=load('shiva_sutras_kashmir')
os.makedirs(f'{ROOT}/data',exist_ok=True)
for n in ['ashtadhyayi','maheshvara','shiva_sutras_kashmir']:
    if os.path.abspath(f'{SRC}/{n}.json')!=os.path.abspath(f'{ROOT}/data/{n}.json'): shutil.copyfile(f'{SRC}/{n}.json',f'{ROOT}/data/{n}.json')
j=lambda o: json.dumps(o,ensure_ascii=False,separators=(',',':'))
# ---------- data.js
rows=[[x['num'],x['devanagari'],x['iast'],x['padaccheda'],x['anuvritti'],x['type']] for x in A['sutras']]
data={'ashtaMeta':{k:v for k,v in A['meta'].items()},'ashta':rows,
 'mahaMeta':M['meta'],'maha':[[x['n'],x['devanagari'],x['iast'],x['sounds'],x['marker']] for x in M['sutras']],
 'shivaMeta':K['meta'],'shiva':[[x['num'],x['unmesha'],x['devanagari'],x['iast']] for x in K['sutras']],
 'shivaSource':K['sutras'][0]['source'],'shivaLicence':K['sutras'][0]['licence'],'shivaConf':K['sutras'][0]['confidence'],
 'ashtaSource':A['sutras'][0]['source'],'ashtaLicence':A['sutras'][0]['licence'],'ashtaConf':A['sutras'][0]['confidence']}
ashta_rows=data['ashta']; data['ashta']=[]
open(f'{ROOT}/js/data.js','w',encoding='utf8').write('window.NEXUS_DATA='+j(data)+';\n')
open(f'{ROOT}/js/data-ashta.js','w',encoding='utf8').write('window.NEXUS_DATA.ashta='+j(ashta_rows)+';document.dispatchEvent(new Event("nexus:data"));\n')
S={x['num']:x for x in A['sutras']}
# ---------- content
vow=[('अ','a'),('आ','ā'),('इ','i'),('ई','ī'),('उ','u'),('ऊ','ū'),('ऋ','ṛ'),('ॠ','ṝ'),('ऌ','ḷ'),('ए','e'),('ऐ','ai'),('ओ','o'),('औ','au'),('ं','ṃ'),('ः','ḥ')]
cons=[[('क','k'),('ख','kh'),('ग','g'),('घ','gh'),('ङ','ṅ')],[('च','c'),('छ','ch'),('ज','j'),('झ','jh'),('ञ','ñ')],[('ट','ṭ'),('ठ','ṭh'),('ड','ḍ'),('ढ','ḍh'),('ण','ṇ')],
 [('त','t'),('थ','th'),('द','d'),('ध','dh'),('न','n')],[('प','p'),('फ','ph'),('ब','b'),('भ','bh'),('म','m')]]
semi=[('य','y'),('र','r'),('ल','l'),('व','v')]; sib=[('श','ś'),('ष','ṣ'),('स','s'),('ह','h')]
varga=['ka-varga','ca-varga','ṭa-varga','ta-varga','pa-varga']
sthana=[
 ('Kaṇṭha (throat)','a ā, k kh g gh ṅ, h, ḥ','kantha'),
 ('Tālu (palate)','i ī, c ch j jh ñ, y, ś','talu'),
 ('Mūrdhan (roof of mouth)','ṛ ṝ, ṭ ṭh ḍ ḍh ṇ, r, ṣ','murdha'),
 ('Danta (teeth)','ḷ, t th d dh n, l, s','danta'),
 ('Oṣṭha (lips)','u ū, p ph b bh m','ostha'),
 ('Kaṇṭha-tālu (throat and palate)','e, ai','kt'),
 ('Kaṇṭha-oṣṭha (throat and lips)','o, au','ko'),
 ('Danta-oṣṭha (teeth and lips)','v','do'),
 ('Nāsikā (nose, added to the sthāna)','ṅ ñ ṇ n m, ṃ','nasika')]
glossary=[
('sūtra','सूत्र','A very short rule. The Aṣṭādhyāyī is a collection of such rules.'),
('Aṣṭādhyāyī','अष्टाध्यायी','Pāṇini\'s grammar of Sanskrit, in eight adhyāyas (chapters).'),
('adhyāya','अध्याय','A chapter. The Aṣṭādhyāyī has eight; each has four pādas.'),
('pāda','पाद','A quarter-chapter. Locus 6.1.77 means adhyāya 6, pāda 1, sūtra 77.'),
('Māheśvara sūtras','माहेश्वरसूत्र','The 14 lines of sounds, each ending in a marker, that open the pratyāhāra system.'),
('pratyāhāra','प्रत्याहार','A short label (for example ac) for a run of sounds in the 14 lines, from a first sound up to a marker.'),
('it (marker)','इत्','A sound used only as a boundary marker and not counted in the set. The last letter of each Māheśvara line is one.'),
('varṇa','वर्ण','A sound or letter-sound of the language.'),
('svara','स्वर','A vowel.'),
('vyañjana','व्यञ्जन','A consonant.'),
('sthāna','स्थान','The place of articulation: where in the mouth a sound is made.'),
('prayatna','प्रयत्न','The effort or manner of articulation.'),
('savarṇa','सवर्ण','Sounds with the same place and effort, treated as like one another (sūtra 1.1.9).'),
('saṃjñā','संज्ञा','A technical name or definition, for example guṇa and vṛddhi.'),
('paribhāṣā','परिभाषा','A rule about how other rules are read or applied.'),
('vidhi','विधि','An operative rule that says what happens.'),
('adhikāra','अधिकार','A heading rule whose words carry forward over a range of sūtras (in the data, code AD).'),
('anuvṛtti','अनुवृत्ति','Carrying a word forward from an earlier sūtra so a short rule can stay short.'),
('padaccheda','पदच्छेद','Splitting a sūtra into its separate words.'),
('sandhi','सन्धि','The joining of sounds at the boundary of words or parts of words.'),
('guṇa','गुण','The names given to a, e, o (sūtra 1.1.2).'),
('vṛddhi','वृद्धि','The names given to ā, ai, au (sūtra 1.1.1).'),
('lopa','लोप','Disappearance of a sound (sūtra 1.1.60).'),
('ādeśa','आदेश','A substitute: something that takes the place of something else.'),
('dhātu','धातु','A verb root.'),
('pratyaya','प्रत्यय','A suffix added to a base.'),
('śikṣā','शिक्षा','The tradition of phonetics: how sounds are made and taught.'),
('vyākaraṇa','व्याकरण','Grammar; the study of the analysis of language.'),
('unmeṣa','उन्मेष','A section of the Śiva Sūtras; the data file lists three, with 20, 10 and 45 sūtras.'),
('Devanāgarī','देवनागरी','The script used for Sanskrit in this app.'),
('IAST','','International Alphabet of Sanskrit Transliteration: the Latin-letter scheme with diacritics used in this app.')]
bridges={
'1.1.1':'ā, ai and au are given the name vṛddhi.','1.1.2':'a, e and o are given the name guṇa.',
'1.1.3':'guṇa and vṛddhi operate on the ik vowels (i, u, ṛ, ḷ).','1.1.9':'Sounds made in the same place with the same effort are called savarṇa.',
'1.1.60':'Lopa is the name for non-appearance, that is, disappearance of a sound.',
'1.1.71':'A first letter taken together with a final marker names itself and every sound between them. This is the pratyāhāra rule.',
'1.3.2':'A nasal vowel in the original teaching is a marker (it).','1.3.9':'That marker is dropped.',
'6.1.77':'An ik vowel (i, u, ṛ, ḷ) is replaced by a yaṇ semivowel (y, v, r, l) before a vowel.',
'6.1.87':'a followed by a vowel: guṇa replaces both.','6.1.88':'a followed by e, o, ai or au: vṛddhi replaces both.',
'6.1.101':'An ak vowel followed by a similar vowel: one long vowel replaces both.'}
for k in bridges: assert k in S,k
sandhi=[('6.1.87','guṇa','deva + indra','devendra','a + i → e'),('6.1.88','vṛddhi','tava + eva','tavaiva','a + e → ai'),
 ('6.1.77','yaṇ','iti + ādi','ityādi','i + ā → yā'),('6.1.101','dīrgha','vidyā + ālaya','vidyālaya','ā + ā → ā')]
# ---- facts computed
from collections import Counter
tc=Counter(x['type'] for x in A['sutras']); ac=Counter(x['adhyaya'] for x in A['sutras'])
pc=Counter((x['adhyaya'],x['pada']) for x in A['sutras']); anu=Counter(x['adhyaya'] for x in A['sutras'] if x['anuvritti'])
longest=max(A['sutras'],key=lambda x:len(x['devanagari'])); shortest=min(A['sutras'],key=lambda x:len(x['devanagari']))
facts=[
 f"The data holds {len(A['sutras']):,} Aṣṭādhyāyī sūtras.",
 f"Adhyāya {max(ac,key=ac.get)} has the most sūtras in this data ({max(ac.values())}); adhyāya {min(ac,key=ac.get)} has the fewest ({min(ac.values())}).",
 f"{tc['V']:,} of the {len(A['sutras']):,} sūtras carry the type code V (vidhi, operative rules) in the data.",
 f"{tc['S']} sūtras carry type code S (saṃjñā, definitions) and {tc['P']} carry P (paribhāṣā).",
 f"{sum(anu.values()):,} sūtras have anuvṛtti (carried-forward words) listed in the data.",
 f"The longest sūtra by character count is {longest['num']} ({len(longest['devanagari'])} characters).",
 "There are 14 Māheśvara lines; each ends with a marker that is not counted in the set.",
 f"The Śiva Sūtras file has {len(K['sutras'])} sūtras in three unmeṣas of 20, 10 and 45.",
 "The pratyāhāra hal runs from h in line 5 to the marker l in line 14 and holds 33 sounds.",
 "The pratyāhāra ac holds the 9 vowels a i u ṛ ḷ e o ai au.",
 f"Sūtra 1.1.1 is {S['1.1.1']['devanagari']} ({S['1.1.1']['iast']}), the very first sūtra in the data."]
stats=dict(total=len(A['sutras']),maha=len(M['sutras']),shiva=len(K['sutras']),types=dict(tc),adhyaya={str(k):v for k,v in sorted(ac.items())},
 pada={f'{a}.{p}':v for (a,p),v in sorted(pc.items())},anu={str(k):v for k,v in sorted(anu.items())},
 longest=[longest['num'],len(longest['devanagari'])],withAnu=sum(anu.values()),
 unmesha={str(k):v for k,v in sorted(Counter(x['unmesha'] for x in K['sutras']).items())})
prat=all_pratyaharas(M)
pr=[{k:v for k,v in p.items()} for p in prat]
# ---- flashcards
cards=[]
for t,d,m in glossary: cards.append(dict(deck='Glossary',f=t+(' · '+d if d else ''),b=m))
for l in M['sutras']: cards.append(dict(deck='Māheśvara lines',f=f"Line {l['n']}: {l['devanagari']} ({l['iast']})",b=f"Sounds: {' '.join(l['sounds'])}. Marker: {l['marker']}."))
for nm,sn in [('ac','a i u ṛ ḷ e o ai au'),('hal','33 consonants h y v r l ñ m ṅ ṇ n jh bh gh ḍh dh j b g ḍ d kh ph ch ṭh th c ṭ t k p ś ṣ s'),('ik','i u ṛ ḷ'),('yaṇ','y v r l'),('śar','ś ṣ s'),('ec','e o ai au')]:
    cards.append(dict(deck='Pratyāhāra',f=f'What does {nm} contain?',b=sn))
for n,t in bridges.items(): cards.append(dict(deck='Sūtras',f=f"{S[n]['devanagari']} ({S[n]['iast']}) · Aṣṭādhyāyī {n}",b=t+' (bridge idea, an interpretation)'))
for a,b,c in [(x[0],x[1],x[2]) for x in sthana]: cards.append(dict(deck='Sounds',f=f'Sthāna: {a}',b=b))
for n,nm,a,b,r in sandhi: cards.append(dict(deck='Sandhi',f=f'{a} (sūtra {n}, {nm})',b=f'{b} ({r}); textbook example'))
for i,c in enumerate(cards): c['id']=i
# ---- quiz bank
rnd=random.Random(2026); Q=[]
def mc(q,ans,wrong,why=''):
    opts=[ans]+[w for w in wrong if w!=ans][:3]; rnd.shuffle(opts); Q.append(dict(q=q,o=opts,a=opts.index(ans),why=why))
for nm,sn in [('ac','9'),('hal','33'),('ik','4'),('yaṇ','4'),('śar','3'),('al','42'),('ec','4'),('ak','5')]:
    got=len(next(p for p in prat if p['name']==nm)['sounds']) 
    mc(f'How many sounds does the pratyāhāra {nm} contain?',str(got),[str(got+i) for i in (1,2,-1,3)],'Computed from the 14 lines.')
for l in M['sutras']:
    mc(f"Which marker ends Māheśvara line {l['n']} ({l['devanagari']})?",l['marker'],[x['marker'] for x in M['sutras'] if x['marker']!=l['marker']][:6:2]+['t'],'Last letter of the line.')
for n,t in bridges.items():
    others=[v for k,v in bridges.items() if k!=n]; rnd.shuffle(others)
    mc(f"Which is a bridge idea for {S[n]['iast']} ({n})?",t,others[:3],'Interpretation, not from the data files.')
for t,d,m in glossary[:24]:
    others=[x[2] for x in glossary if x[0]!=t]; rnd.shuffle(others); mc(f'What is "{t}"?',m,others[:3])
for a,b,c in sthana[:8]:
    others=[x[0] for x in sthana if x[0]!=a]; rnd.shuffle(others); first=b.split(',')[-1].strip().split(' ')[0] if False else b.split(',')[0].strip()
    mc(f'Where is the sound group "{first}" made?',a,others[:3],'Standard śikṣā textbook table.')
mc('How many sūtras does the Aṣṭādhyāyī file in this app hold?','3,983',['3,959','4,000','3,500'],'Count from the data.')
mc('How many Śiva Sūtras are in the Kashmir file?','75',['77','108','20'],'Vārttika-recension numbering in the file.')
mc('Which adhyāya has the most sūtras in the data?','6',['1','3','8'],f"Adhyāya 6 has {ac[6]}.")
mc('What type code marks saṃjñā (definition) sūtras?','S',['V','P','AD'],'From the data meta.')
mc('What type code marks vidhi (operative) sūtras?','V',['S','P','AT'],'From the data meta.')
for i,q in enumerate(Q): q['id']=i
curr=[('Start Here','start',5,'Read the path and the four-step loop: sound, structure, meaning, use.'),
 ('Māheśvara lines','maheshvara',10,'Read the 14 lines; say each aloud and name its marker.'),
 ('Pratyāhāra builder','maheshvara',10,'Build ac, hal, ik, yaṇ and śar yourself and check the counts.'),
 ('Sound lab','sound',10,'Learn the five varga rows and the sthāna table.'),
 ('Aṣṭādhyāyī browser','ashtadhyayi',10,'Look up 1.1.1, 1.1.2 and 6.1.77; read the anuvṛtti.'),
 ('Śiva Sūtras','shiva',5,'Read the first unmeṣa and note the numbering caveat.'),
 ('Practice','practice',10,'One flashcard set and one quiz.')]
res=json.load(open(f'{ROOT}/tools/resources_verified.json'))
resources=[r for r in res if r['status']==200 and r['label']!='Wikipedia: Maheshwara Sutras' and 'Maheshvara_Sutras' not in r['url']]
content=dict(vow=vow,cons=cons,semi=semi,sib=sib,varga=varga,sthana=sthana,glossary=glossary,bridges=bridges,sandhi=sandhi,facts=facts,stats=stats,
 prat=pr,common=['ak','ac','ec','ik','yaṇ','jhal','hal','al','śar','jhaś','vaś','aṇ','yar','khar','jhay'],cards=cards,quiz=Q,curriculum=curr,resources=resources)
open(f'{ROOT}/js/content.js','w',encoding='utf8').write('window.NEXUS_CONTENT='+j(content)+';\n')
print('ok',len(cards),'cards',len(Q),'questions',len(pr),'pratyaharas')
