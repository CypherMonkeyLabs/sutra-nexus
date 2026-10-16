"""Generates guidebot/kb.js from the app's own content (build/js/content.js + the data files). Run after tools/gen_content.py.
Nothing in the knowledge base is written outside this script and the app content; answers that need data (sūtra lookup) are computed at runtime from NEXUS_DATA."""
import json, os, sys, re
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(ROOT,'tools'))
from nexus_lib import plain
C=json.loads(open(f'{ROOT}/js/content.js',encoding='utf8').read().split('=',1)[1].rstrip().rstrip(';'))
D=json.loads(open(f'{ROOT}/js/data.js',encoding='utf8').read().split('=',1)[1].rstrip().rstrip(';'))
D['ashta']=json.loads(open(f'{ROOT}/js/data-ashta.js',encoding='utf8').read().split('=',1)[1].split(';document')[0])
kb={'name':'Nexus Monkey','app':'Sūtra Nexus','tagline':'Ancient rules. Living systems.'}
E=[]  # entries: k = keyword phrases, a = answer, room = optional room to open, t = topic
def add(k,a,room=None,t='app'): E.append(dict(k=k,a=a,room=room,t=t))
add(['what is this','about','sutra nexus','what is sutra nexus','purpose','who made'],"Sūtra Nexus is a free, offline study app for Sanskrit sound and grammar, made by a lifelong student and AI enthusiast. It reads from three open data files: the Aṣṭādhyāyī (3,983 sūtras), the 14 Māheśvara lines and 75 Śiva Sūtras.",'about')
add(['start','where do i start','begin','new here','path','curriculum','one hour','1 hour'],"Open Start Here for a seven-step path of about one hour: Start Here, Māheśvara lines, the pratyāhāra builder, Sound lab, Aṣṭādhyāyī browser, Śiva Sūtras and Practice. I can walk you through it: say 'one hour path'.",'start')
add(['theme','themes','dark mode','colors','colours','contrast','font size','text size','bigger text','display','reduce motion','animation'],"The Display control at the top has A-, A and A+ for text size, a theme list (Aurora, Neon, Holographic, Cyberpunk Sunset, Light, High contrast) and a motion button. All are saved in this browser.")
add(['offline','internet','network','privacy','data','localstorage','save','progress'],"Everything runs from local files with no internet needed. Your progress, theme and text size are saved only in this browser. The bot's optional cloud endpoint is unset.")
add(['gita','bhagavad gita','geeta'],"The Bhagavad Gita is not part of this app's data, so I cannot quote it here.",None,'limits')
add(['translation','english meaning','meaning of sutra','translate','gloss'],"The data files carry no English meanings, so lines say 'meaning: UNKNOWN in source'. I show a short 'bridge idea' only for a few well-known sūtras, and label it as an interpretation. Edition and translator for any gloss: UNKNOWN.",'about','limits')
add(['75 77','recension','kshemaraja','kashmir numbering','how many shiva sutras'],"The Śiva Sūtras file holds 75 sūtras (20 + 10 + 45, Vārttika-recension numbering). The file's meta note says the common Kṣemarāja recension counts 22 + 10 + 45. Which sūtras differ: UNKNOWN beyond the source.",'shiva','shiva')
add(['licence','license','copyright','credit','source','sources','where does the data come from'],"Aṣṭādhyāyī and Māheśvara text: ashtadhyayi-com/data, free to use with credit. Śiva Sūtras: GRETIL electronic text (ed. Madhusudan Kaul Shastri 1925, input Oliver Hellwig). Transliteration is machine-converted and unchecked by a person.",'about')
add(['pratyahara','pratyahara builder','build pratyahara','how do pratyaharas work','it marker','marker','anubandha'],"A pratyāhāra is a two-letter label for a run of sounds in the 14 Māheśvara lines: start at the first sound, read to the marker, skip the markers. For example ac = a i u ṛ ḷ e o ai au. Try the builder in the Māheśvara room.",'maheshvara','pratyahara')
add(['sandhi','join sounds','guna','vriddhi','yan'],"Sandhi is the joining of sounds. Examples with the sūtras that govern them: a + i → e (6.1.87 guṇa), a + e → ai (6.1.88 vṛddhi), i + ā → yā (6.1.77 yaṇ), ā + ā → ā (6.1.101). Open the Sound lab for the flows.",'sound','sandhi')
add(['anuvritti','carry forward','inheritance of words'],"Anuvṛtti is carrying a word forward from an earlier sūtra. The data lists it per sūtra; for example 1.1.4 carries इकः and गुण-वृद्धी. Open any sūtra in the Aṣṭādhyāyī room to see it.",'ashtadhyayi','structure')
add(['types','sutra types','type codes','samjna','vidhi','paribhasha','adhikara'],"Type codes in the data: S = saṃjñā (definition), P = paribhāṣā (rule for reading rules), V = vidhi (operative rule), plus AD and AT, which the data does not expand. Counts: V "+f"{C['stats']['types']['V']:,}, S {C['stats']['types']['S']}, AT {C['stats']['types']['AT']}, AD {C['stats']['types']['AD']}, P {C['stats']['types']['P']}.",'ashtadhyayi','structure')
add(['sthana','places of articulation','mouth','throat','palate','lips','teeth'],"Sthāna means place of articulation: kaṇṭha (throat), tālu (palate), mūrdhan (roof of mouth), danta (teeth), oṣṭha (lips), plus combined places for e, ai, o, au and v. See the Sound lab (textbook summary, not from the data files).",'sound','sound')
add(['quiz','test me','score'],"Say 'quiz me' for a five-question quiz here, or open the Practice room for ten questions.",'practice')
add(['flashcards','cards','spaced','ladder','leitner','review'],"Flashcards use a spaced ladder: a correct answer moves a card up a box (gaps of today, 1, 3, 7, 14 and 30 days); a miss returns it to box 1. Say 'flashcard' to try one here.",'practice')
add(['hello','hi','hey','namaste'],"Namaste. I am the monkey guide for Sūtra Nexus. Ask me about sūtras, pratyāhāras, sounds or this app, or use the chips below.")
add(['thanks','thank you'],"You are welcome. Keep saying the lines aloud; it helps.")
add(['contact','report a concern','remove content'],"If something should be removed or corrected, please use the contact section at https://cyphermonkeylabs.com/#contact. The project is free and learning-only.",'about')
add(['who is lucky','creator','author'],"A lifelong student and AI enthusiast from systems, networking, voice and contact center work, growing into AI omni-channel agents, sharing what he learns for free.",'about')
for t,d,m in C['glossary']:
    add([t.lower(),plain(t)]+([d] if d else []),f"{t}{' ('+d+')' if d else ''}: {m}",'ecosystem','glossary')
for l in D['maha']:
    add([f"line {l[0]}",f"maheshvara line {l[0]}",l[2],l[1]],f"Māheśvara line {l[0]}: {l[1]} ({l[2]}). Sounds: {' '.join(l[3])}. Marker: {l[4]} (not counted). Meaning: UNKNOWN in source beyond this structure.",'maheshvara','maheshvara')
seen={}
for p in C['prat']:
    seen.setdefault(p['name'],[]).append(p)
for nm,ps in seen.items():
    if len(nm)<2: continue
    if len(ps)==1:
        p=ps[0]; a=f"{nm}: {len(p['sounds'])} sounds, from {p['start']} (line {p['start_line']}) to the marker {p['marker']} of line {p['marker_line']}: {' '.join(p['sounds'])}."
    else:
        a=f"{nm} can end at different markers: "+'; '.join(f"to marker of line {p['marker_line']}: {len(p['sounds'])} sounds ({' '.join(p['sounds'])})" for p in ps)+'. The data does not say which is meant in a given sūtra.'
    add(['pratyahara '+nm,nm,'what is '+nm,plain(nm)],a,'maheshvara','prat')
for n,tx in C['bridges'].items():
    r=next(x for x in D['ashta'] if x[0]==n)
    add([n,r[2],r[1],plain(r[2])],f"Aṣṭādhyāyī {n}: {r[1]} ({r[2]}), type {r[5]}. Bridge idea (an interpretation): {tx}",'ashtadhyayi','sutra')
add(['how many sutras','count','total'],f"The data holds {D['ashtaMeta']['count']:,} Aṣṭādhyāyī sūtras, 14 Māheśvara lines and 75 Śiva Sūtras.",'start','facts')
kb['entries']=E
kb['syn']={'rule':'sutra','rules':'sutra','aphorism':'sutra','verse':'sutra','letter':'varna','sound':'varna','vowel':'svara','consonant':'vyanjana','pronunciation':'sthana','pronounce':'sthana','articulation':'sthana','grammar':'vyakarana','panini':'ashtadhyayi','ashtadhyayi':'ashtadhyayi','markers':'marker','shiva':'shiva','siva':'shiva','shivasutra':'shiva','abbreviation':'pratyahara','abbreviations':'pratyahara','pratyaharas':'pratyahara','joining':'sandhi','combine':'sandhi','colour':'theme','color':'theme','dark':'theme','light':'theme','larger':'font','smaller':'font','test':'quiz','flashcard':'cards','flashcards':'cards'}
kb['facts']=C['facts']+["Every one of the 14 Māheśvara lines ends in a marker; the markers are ṇ k ṅ c ṭ ṇ m ñ ṣ ś v y r l.","The sūtra 6.1.77 iko yaṇaci (ik becomes yaṇ before a vowel) is in the data with type V."]
kb['quiz']=C['quiz']; kb['cards']=C['cards']; kb['curriculum']=C['curriculum']
kb['stats']=C['stats']
kb['rooms']={
 'start':{'help':'This is the starting room: counters, the seven-step path, the learning loop and the mind map. Tap a step to open that room.','chips':['One hour path','Quick tour','Fun fact']},
 'maheshvara':{'help':'Pick a first sound, then a marker; the builder computes the set from the 14 lines. Try hal, or tap Try a known one.','chips':['What is a pratyāhāra?','Tell me about ac','Teach me pratyāhāra']},
 'ashtadhyayi':{'help':'Search by number (6.1.77), Devanāgarī or IAST, filter by adhyāya, pāda or type, and tap a row for its detail. Charts are at the bottom.','chips':['Tell me about 1.1.1','What are the type codes?','Teach me structure']},
 'shiva':{'help':'The 75 Śiva Sūtras from the GRETIL text, with numbering notes. Meanings are UNKNOWN in source.','chips':['Why 75 and not 77?','Where does the text come from?']},
 'sound':{'help':'The sthāna chart, script tables, the five rows and four sandhi flows. These tables are a textbook summary.','chips':['What is sthāna?','Explain sandhi','Teach me sounds']},
 'practice':{'help':'Flashcards use a spaced ladder; the quiz draws ten questions; the daily challenge is five questions.','chips':['Quiz me','Flashcard','Daily challenge']},
 'ecosystem':{'help':'Glossary, mind map, bridges (analogies, labelled as interpretations), sister topics and future hooks.','chips':['What is anuvṛtti?','What is sandhi?']},
 'resources':{'help':'Only links I opened and checked, as of 2026-10.','chips':['Where does the data come from?']},
 'downloads':{'help':'Cheat-sheet PDFs, a slide deck and a single-file copy of the app. No ZIP files.','chips':['What is in the cheat sheets?']},
 'about':{'help':'Purpose, sources and licences, gaps, privacy and the disclaimer.','chips':['What is not included?']}}
kb['tours']={
 'quick':{'title':'Quick tour','steps':[['start',None,'This is Start Here: the counters come from the data, and the path has seven steps.'],['maheshvara','#bStart','Here is the pratyāhāra builder. Pick a first sound, then a marker.'],['ashtadhyayi','#aq','Search any of the 3,983 sūtras by number, Devanāgarī or IAST.'],['shiva',None,'The 75 Śiva Sūtras, with the numbering note.'],['sound',None,'The Sound lab: places of articulation, scripts and sandhi flows.'],['practice',None,'Flashcards, a quiz and a daily challenge. Your progress is saved in this browser only.']]},
 'pratyahara':{'title':'Pratyāhāra tour','steps':[['maheshvara','#mlines','These are the 14 lines. Each ends with a marker that is not counted.'],['maheshvara','#bStart','Choose a first sound here.'],['maheshvara','#bMark','Then a marker. Markers before your first sound are disabled.'],['maheshvara','#selftest','The app checks itself against known examples: ac, ik, yaṇ, śar, ak, ec, hal and al.']]},
 'sutras':{'title':'Sūtra browser tour','steps':[['ashtadhyayi','#aq','Type 6.1.77 here to find iko yaṇaci.'],['ashtadhyayi','#afeat','These chips jump to well-known sūtras.'],['ashtadhyayi','#alist','Tap a row for its word split, anuvṛtti, type and citation.']]}}
kb['lessons']={
 'pratyahara':['The Māheśvara lines are 14 short lists of sounds. Each list ends with a marker.','A pratyāhāra is a short name made from a first sound and a marker. It means: that sound, every sound after it, up to the marker.','Markers are not counted. So ac is a i u ṛ ḷ e o ai au: 9 sounds.','The builder in the Māheśvara room lets you try this. Next, try hal: from h in line 5 to the marker l in line 14 gives 33 consonants.'],
 'sounds':['Every sound has a place of articulation, a sthāna: throat, palate, roof of the mouth, teeth, lips.','The consonants sit in five rows, each moving from the back of the mouth to the front: k, c, ṭ, t, p.','The last sound of each row is the nasal: ṅ ñ ṇ n m.','Say each row aloud and feel where the sound is made. That is the drill.'],
 'sandhi':['Sandhi is the joining of sounds, for example a + i → e.','Sūtra 6.1.87 (ādguṇaḥ) is the rule for a + vowel giving guṇa.','Sūtra 6.1.88 (vṛddhireci) gives vṛddhi: a + e → ai.','Sūtra 6.1.77 (iko yaṇaci) replaces i, u, ṛ, ḷ by y, v, r, l before a vowel: iti + ādi → ityādi.'],
 'structure':['The Aṣṭādhyāyī has 8 adhyāyas, each with 4 pādas. A locus like 6.1.77 is adhyāya 6, pāda 1, sūtra 77.',f"This data holds {D['ashtaMeta']['count']:,} sūtras. Adhyāya 6 is the largest here with {C['stats']['adhyaya']['6']}.",'Most are type V (vidhi). Others define terms (S) or say how to read rules (P).','Anuvṛtti carries words forward so that short sūtras can stay short.']}
kb['generated']='generated by guidebot/gen_kb.py from the app content'
open(f'{HERE}/kb.js','w',encoding='utf8').write('window.NEXUS_KB='+json.dumps(kb,ensure_ascii=False,separators=(',',':'))+';\n')
print('entries',len(E),'size',os.path.getsize(f'{HERE}/kb.js'))
