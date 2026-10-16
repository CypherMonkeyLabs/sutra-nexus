"""Fetch each candidate resource link and record HTTP status + page title. Output: resources_verified.json (as of 2026-10)."""
import urllib.request, re, json, sys
C=[("Aṣṭādhyāyī online (ashtadhyayi.com)","https://ashtadhyayi.com/","Browse and search the sūtras with commentaries (site's own content; licences vary)"),
("ashtadhyayi-com/data on GitHub","https://github.com/ashtadhyayi-com/data","The open data repository this app's sūtra text comes from"),
("GRETIL: Śiva Sūtras with Vārttika","https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_zivasUtra-with-vArttika.htm","Electronic text used for the 75 Śiva Sūtras"),
("Wikipedia: Pāṇini","https://en.wikipedia.org/wiki/P%C4%81%E1%B9%87ini","Background on the grammarian"),
("Wikipedia: Shiva Sutras","https://en.wikipedia.org/wiki/Shiva_Sutras","Background on the Kashmir Śiva Sūtras"),
("Wikipedia: Shiksha","https://en.wikipedia.org/wiki/Shiksha","Background on Vedic phonetics"),
("Wikipedia: Sandhi","https://en.wikipedia.org/wiki/Sandhi","Background on sound-joining rules"),
("Wikipedia: Ashtadhyayi","https://en.wikipedia.org/wiki/Ashtadhyayi","Background on the Aṣṭādhyāyī"),
("Wikipedia: Devanagari","https://en.wikipedia.org/wiki/Devanagari","Background on the script"),
("Wikipedia: IAST","https://en.wikipedia.org/wiki/International_Alphabet_of_Sanskrit_Transliteration","Background on the transliteration scheme"),
("Wikipedia: Pratyahara","https://en.wikipedia.org/wiki/Pratyahara_(Sanskrit_grammar)","candidate"),
("Wikipedia: Shiva Sutras of Panini","https://en.wikipedia.org/wiki/Shiva_Sutras_(Panini)","candidate"),
("Wikipedia: Maheshwara Sutras","https://en.wikipedia.org/wiki/Maheshvara_Sutras","candidate")]
out=[]
for t,u,d in C:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)
        html=r.read(200000).decode('utf8','ignore'); m=re.search(r'<title[^>]*>([^<]*)',html)
        out.append(dict(label=t,url=u,desc=d,status=r.status,final=r.geturl(),title=(m.group(1).strip() if m else '')))
    except Exception as e: out.append(dict(label=t,url=u,desc=d,status=str(e)[:40],final='',title=''))
    print(out[-1]['status'],u,'|',out[-1]['title'][:70])
json.dump(out,open('resources_verified.json','w'),ensure_ascii=False,indent=1)
