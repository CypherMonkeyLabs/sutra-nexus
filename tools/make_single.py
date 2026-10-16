"""Builds downloads/sutra-nexus-single-file.html: the whole app (CSS, data, scripts, guide bot) inlined into ONE file. No ZIP, no external requests."""
import os, re
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE)
rd=lambda p: open(f'{R}/{p}',encoding='utf8').read()
html=rd('index.html')
css=rd('css/nexus.css')+'\n'+rd('guidebot/guidebot.css')
html=re.sub(r'<link rel="stylesheet" href="css/nexus.css">\s*<link rel="stylesheet" href="guidebot/guidebot.css">','<style>'+css.replace('\\','\\\\')+'</style>',html)
def inl(m): return ''
scripts=['js/data.js','js/data-ashta.js','js/content.js','js/downloads.js','js/diagrams.js','js/core.js','js/rooms.js','guidebot/kb.js','guidebot/guidebot.js']
body=html.split('<script src="js/data.js">')[0]
js='<script>window.NEXUS_STANDALONE=true;</script>\n'+'\n'.join('<script>'+rd(s).replace('</script>','<\\/script>')+'</script>' for s in scripts)
out=body+js+'\n</body>\n</html>\n'
open(f'{R}/downloads/sutra-nexus-single-file.html','w',encoding='utf8').write(out)
print(len(out))
