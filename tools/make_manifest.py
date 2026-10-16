"""Writes js/downloads.js (file list with real sizes) and downloads/manifest.json. Run after the PDFs, deck and single file exist."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));D=f'{R}/downloads'
def sz(n):
    return f'{n/1024:.0f} KB' if n<1048576 else f'{n/1048576:.1f} MB'
items=[('sutra-nexus-pratyahara-cheat-sheet.pdf','Pratyāhāra cheat sheet','The 14 lines and common pratyāhāras with counts','PDF, A4, 2 pages'),
('sutra-nexus-sound-and-sthana-chart.pdf','Sound and sthāna chart','Scripts, places and manner of articulation','PDF, A4, 2 pages'),
('sutra-nexus-sutra-type-guide.pdf','Sūtra type guide','Types, counts per adhyāya and well-known sūtras','PDF, A4, 2 pages'),
('sutra-nexus-shiva-sutras-one-pager.pdf','Śiva Sūtras one-pager','All 75 sūtras on one sheet','PDF, A4, 1 page'),
('sutra-nexus-slide-deck.pptx','Slide deck','15 pastel slides with the same footer and disclaimer','PowerPoint'),
('sutra-nexus-single-file.html','Single-file app','The whole app in one HTML file for offline use','HTML')]
L=[]
for f,t,d,k in items:
    p=f'{D}/{f}'
    if os.path.exists(p): L.append(dict(file=f,title=t,desc=d,kind=k,size=sz(os.path.getsize(p)),bytes=os.path.getsize(p),path='downloads/'+f))
open(f'{R}/js/downloads.js','w',encoding='utf8').write('window.NEXUS_DOWNLOADS='+json.dumps(L,ensure_ascii=False)+';\n')
json.dump(L,open(f'{D}/manifest.json','w'),ensure_ascii=False,indent=1);print(len(L),'items')
