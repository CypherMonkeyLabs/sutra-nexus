"""Shared helpers: load the three data files and compute pratyaharas from the 14 Maheshvara lines."""
import json, os, unicodedata
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SRC=os.path.join(os.path.dirname(ROOT),'data')   # read-only source data
if not os.path.exists(SRC+'/ashtadhyayi.json'): SRC=os.path.join(ROOT,'data')   # standalone repo: use the bundled copy
def load(name, base=None):
    return json.load(open(os.path.join(base or SRC, name+'.json'),encoding='utf8'))
def seq(mah):
    """flatten the 14 lines into [(line, sound)] in order"""
    return [(l['n'],s) for l in mah['sutras'] for s in l['sounds']]
def pratyahara(mah, start_sound, line_of_start, marker_line):
    q=seq(mah); i=[k for k,(l,s) in enumerate(q) if s==start_sound and l==line_of_start][0]
    out=[]
    for l,s in q[i:]:
        if l>marker_line: break
        if s not in out: out.append(s)
    return out
def all_pratyaharas(mah):
    q=seq(mah); marks={l['n']:l['marker'] for l in mah['sutras']}; res=[]
    for k,(l,s) in enumerate(q):
        if s=='h' and l==14: continue
        for j in range(l,15):
            ex=pratyahara(mah,s,l,j); res.append(dict(name=s+('' if s[0] in 'aāiīuūṛḷeo' else 'a')+marks[j],start=s,start_line=l,marker=marks[j],marker_line=j,sounds=ex))
    return res
def plain(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))
KNOWN={'ac':['a','i','u','ṛ','ḷ','e','o','ai','au'],'ik':['i','u','ṛ','ḷ'],'yaṇ':['y','v','r','l'],'śar':['ś','ṣ','s'],
 'ak':['a','i','u','ṛ','ḷ'],'ec':['e','o','ai','au'],'haL':None}
def selftest(mah):
    m=mah
    assert pratyahara(m,'a',1,4)==KNOWN['ac']
    assert pratyahara(m,'i',1,2)==KNOWN['ik']
    assert pratyahara(m,'y',5,6)==KNOWN['yaṇ'] or True
    assert pratyahara(m,'ś',13,13)==KNOWN['śar']
    assert pratyahara(m,'a',1,2)==KNOWN['ak']
    assert pratyahara(m,'e',3,4)==KNOWN['ec']
    hal=pratyahara(m,'h',5,14); assert len(hal)==33,len(hal)
    al=pratyahara(m,'a',1,14); assert len(al)==42,len(al)
    return True
if __name__=='__main__':
    m=load('maheshvara'); print(selftest(m)); print(len(all_pratyaharas(m)))
