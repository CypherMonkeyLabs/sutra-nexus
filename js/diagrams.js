/* Sūtra Nexus · inline SVG diagrams (no external assets). Colours come from CSS variables so every theme works. */
(function(){
'use strict';
var D=window.NexusDiagrams={}; var C=window.NEXUS_CONTENT, X=window.NEXUS_DATA;
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function t(x,y,s,cls,anc,extra){return '<text x="'+x+'" y="'+y+'" class="'+(cls||'tx')+'" text-anchor="'+(anc||'middle')+'" '+(extra||'')+'>'+esc(s)+'</text>';}
function box(x,y,w,h,cls,rx){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+(rx==null?12:rx)+'" class="'+(cls||'bx')+'"/>';}
function arrow(x1,y1,x2,y2,cls){return '<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" class="'+(cls||'flowline')+'" marker-end="url(#ah)"/>';}
var DEFS='<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="f2"/></marker></defs>';
function svg(w,h,body,label,cls){return '<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="'+esc(label)+'" class="dg '+(cls||'')+'" xmlns="http://www.w3.org/2000/svg">'+DEFS+body+'</svg>';}
D.meta={};
/* 1 mouth map */
D.mouth=function(){var pts=[['Kaṇṭha',75,'a k h'],['Tālu',148,'i c y ś'],['Mūrdhan',215,'ṛ ṭ r ṣ'],['Danta',285,'ḷ t l s'],['Oṣṭha',355,'u p']];
 var b='<path d="M30 200 C20 120 70 40 170 40 C270 40 330 70 380 110 L420 120 L420 160 L380 165 C330 190 300 205 250 215 C170 235 60 250 30 200Z" class="bx"/>';
 b+='<path d="M60 150 C140 120 260 125 380 140" class="s2" fill="none" stroke-width="3" stroke-linecap="round"/>';
 pts.forEach(function(p,i){var y=140-(i==0?8:i==1?22:i==2?24:i==3?8:0); b+='<circle cx="'+p[1]+'" cy="'+y+'" r="9" class="f1 pulse" style="animation-delay:'+(i*.6)+'s"/>'+t(p[1],y-16,p[0],'tx sm')+t(p[1],236+(i%2)*20,p[2],'tm sm');});
 b+=t(240,24,'Stylised side view: throat left, lips right','tm sm'); return svg(440,290,b,'Stylised side view of the mouth with five places of articulation: throat, palate, roof of mouth, teeth and lips');};
/* 2 pratyahara example */
D.pratFlow=function(){var L=X.maha,b='';var cw=104;
 [0,1,2,3].forEach(function(i){var l=L[i];b+=box(10+i*cw+i*2,50,cw-6,64,'bx'+(i<4?' hl':''))+t(10+i*cw+i*2+(cw-6)/2,78,l[1],'dev tx')+t(10+i*cw+i*2+(cw-6)/2,100,l[2],'tm sm')+t(10+i*cw+i*2+(cw-6)/2,40,'line '+l[0],'tm sm');});
 b+='<path d="M20 140 H410" class="flowline" marker-end="url(#ah)"/>'+t(20,160,'start at a','f1t sm','start')+t(405,160,'stop at marker c','f1t sm','end');
 b+=t(215,188,'ac = a i u ṛ ḷ e o ai au','tx b')+t(215,208,'9 sounds. The marker c is only a boundary, not counted.','tm sm');
 return svg(440,226,b,'Pratyāhāra ac: start at a in line 1, read through line 4 and stop at the marker c');};
/* sandhi 4 */
D.sandhi=function(k){var S=C.sandhi.filter(function(s){return s[1]==k})[0]; var parts=S[2].split(' + ');var b='';
 b+=box(10,40,120,52,'bx')+t(70,73,parts[0],'tx b')+t(145,73,'+','f2t b')+box(160,40,120,52,'bx')+t(220,73,parts[1],'tx b');
 b+=arrow(290,66,340,66)+box(345,40,120,52,'bx hl')+t(405,73,S[3],'tx b');
 b+=t(240,22,'Sūtra '+S[0]+' · '+S[1],'f1t sm')+t(240,125,S[4],'tx')+t(240,148,'textbook example; rule gloss is an interpretation','tm sm');
 return svg(480,160,b,'Sandhi flow '+S[1]+': '+S[2]+' gives '+S[3]);};
/* 7 taxonomy */
D.taxonomy=function(){var T=C.stats.types,order=['V','S','P','AD','AT'],name={V:'vidhi (operative rule)',S:'saṃjñā (definition)',P:'paribhāṣā (reading rule)',AD:'code AD',AT:'code AT'};
 var b=box(150,8,180,40,'bx hl')+t(240,34,'Aṣṭādhyāyī sūtras: '+C.stats.total.toLocaleString('en-US'),'tx b');
 order.forEach(function(k,i){var y=76+i*50; b+='<path d="M240 48 V'+(y+20)+' H70" class="flowline" fill="none"/>'+box(70,y,340,40,'bx')+'<rect x="70" y="'+y+'" width="'+Math.max(6,340*T[k]/C.stats.total)+'" height="40" rx="12" class="f'+(i%4+1)+' o3"/>'+t(84,y+25,k+' · '+name[k],'tx sm','start')+t(400,y+25,T[k].toLocaleString('en-US'),'tx b','end');});
 b+=t(240,336,'Codes S, P, V are expanded in the data meta; AD and AT are not.','tm sm');
 return svg(480,350,b,'Taxonomy of sutra type codes with counts from the data');};
/* 8 anuvrtti */
D.anuvritti=function(){var R=X.ashta;function g(n){return R.filter(function(r){return r[0]==n})[0]}
 var rows=['1.1.3','1.1.4','1.1.5'].map(g),b='';
 rows.forEach(function(r,i){var y=20+i*92;b+=box(10,y,460,76,'bx'+(i==0?' hl':''))+t(24,y+22,r[0],'f1t b','start')+t(100,y+24,r[1],'dev tx','start')+t(24,y+46,r[2],'tm sm','start')+t(24,y+66,'carried forward: '+(r[4].join(' · ')||'none'),'f2t sm','start');
  if(i<2)b+=arrow(240,y+78,240,y+92+4);});
 return svg(480,300,b,'Anuvṛtti flow: words carried forward through sūtras 1.1.3, 1.1.4 and 1.1.5, taken from the data');};
/* 9 adhyaya bars */
D.adhyayaBars=function(){var A=C.stats.adhyaya,mx=Math.max.apply(null,Object.keys(A).map(function(k){return A[k]})),b='';
 Object.keys(A).forEach(function(k,i){var y=14+i*38,w=300*A[k]/mx;b+=t(8,y+20,'Adhyāya '+k,'tx sm','start')+'<rect x="100" y="'+y+'" width="'+w+'" height="26" rx="8" class="f'+(i%4+1)+' grow" style="animation-delay:'+(i*.12)+'s;transform-origin:100px '+(y+13)+'px"/>'+t(106+w,y+19,String(A[k]),'tx b','start');});
 return svg(480,325,b,'Bar chart of sutra counts per adhyaya computed from the data');};
/* 10 donut */
D.typeDonut=function(){var T=C.stats.types,tot=C.stats.total,cx=110,cy=110,r=70,cum=0,b='',keys=['V','S','AT','AD','P'];
 keys.forEach(function(k,i){var f=T[k]/tot,a0=cum*2*Math.PI-Math.PI/2;cum+=f;var a1=cum*2*Math.PI-Math.PI/2,lg=f>.5?1:0;
  b+='<path d="M'+(cx+r*Math.cos(a0))+' '+(cy+r*Math.sin(a0))+' A'+r+' '+r+' 0 '+lg+' 1 '+(cx+r*Math.cos(a1))+' '+(cy+r*Math.sin(a1))+'" fill="none" stroke-width="30" class="s'+(i%4+1)+'"/>';
  b+='<rect x="250" y="'+(40+i*34)+'" width="16" height="16" rx="4" class="f'+(i%4+1)+'"/>'+t(274,'53'.replace('53',String(53+i*34)),k+' · '+T[k].toLocaleString('en-US')+' ('+(100*f).toFixed(1)+'%)','tx sm','start');});
 b+=t(cx,cy+6,'3,983','tx b')+t(cx,cy+26,'sūtras','tm sm');
 return svg(480,220,b,'Donut chart of sutra types computed from the data');};
/* 11 pada heat */
D.padaHeat=function(){var P=C.stats.pada,mx=Math.max.apply(null,Object.keys(P).map(function(k){return P[k]})),b='';
 for(var a=1;a<=8;a++){b+=t(46,50+(a-1)*30,'Adh. '+a,'tm sm','end');for(var p=1;p<=4;p++){var v=P[a+'.'+p]||0,o=.18+.82*v/mx;b+='<rect x="'+(56+(p-1)*96)+'" y="'+(32+(a-1)*30)+'" width="90" height="26" rx="6" class="f1" style="opacity:'+o.toFixed(2)+'"/>'+t(56+(p-1)*96+45,50+(a-1)*30,String(v),'heatn');}}
 for(var q=1;q<=4;q++)b+=t(56+(q-1)*96+45,20,'Pāda '+q,'tm sm');
 return svg(450,282,b,'Heat map of sutra counts per pada across the eight adhyayas');};
/* 12 maheshvara strip */
D.mahaStrip=function(){var L=X.maha,b='';L.forEach(function(l,i){var col=i%2,row=Math.floor(i/2),x=10+col*230,y=8+row*52;
 b+=box(x,y,220,44,'bx seq')+'<g class="seqg" style="animation-delay:'+(i*.45)+'s">'+box(x,y,220,44,'hl2')+'</g>'+t(x+18,y+28,String(l[0]),'f1t b','middle')+t(x+44,y+29,l[1],'dev tx sm','start')+t(x+212,y+28,'marker '+l[4],'f2t sm','end');});
 return svg(470,380,b,'The fourteen Māheśvara lines lighting up one after another, each with its marker');};
/* 13 ladder */
D.ladder=function(){var b='';var rows=[['plain vowel','a','अ'],['guṇa (1.1.2)','a e o','अ ए ओ'],['vṛddhi (1.1.1)','ā ai au','आ ऐ औ']];
 rows.forEach(function(r,i){var y=150-i*60;b+=box(60+i*22,y,300,48,'bx'+(i==2?' hl':''))+t(80+i*22,y+30,r[0],'tx sm','start')+t(340+i*22-22,y+31,r[1]+'  '+r[2],'f1t b','end');if(i<2)b+='<line x1="'+(210+i*22)+'" y1="'+(y)+'" x2="'+(210+i*22)+'" y2="'+(y-12)+'" class="flowline" marker-end="url(#ah)"/>';});
 b+=t(220,205,'Names from sūtras 1.1.2 and 1.1.1; layout is my reading','tm sm');
 return svg(440,222,b,'Ladder showing the plain vowel a, the guna set a e o and the vrddhi set ā ai au');};
/* 14 unmesha */
D.unmesha=function(){var U=C.stats.unmesha,b='';Object.keys(U).forEach(function(k,i){var h=U[k]*4.4,x=60+i*130;b+='<rect x="'+x+'" y="'+(250-h)+'" width="90" height="'+h+'" rx="10" class="f'+(i+1)+' growy" style="animation-delay:'+(i*.2)+'s;transform-origin:'+(x+45)+'px 250px"/>'+t(x+45,243-h,String(U[k]),'tx b')+t(x+45,274,'Unmeṣa '+k,'tx sm');});
 return svg(440,290,b,'Bar chart of Śiva Sūtras per unmeṣa: 20, 10 and 45');};
/* 15 anatomy */
D.anatomy=function(){var r=X.ashta.filter(function(r){return r[0]=='6.1.77'})[0],b='';
 b+=box(60,20,360,70,'bx hl')+t(240,66,r[1],'dev tx big');
 var items=[['locus',r[0],'adhyāya 6 · pāda 1 · sūtra 77'],['transliteration',r[2],'machine-converted, not human-checked'],['padaccheda',r[3],'word split from the source'],['type',r[5],'code V: vidhi'],['anuvṛtti',r[4].join(' · ')||'none listed','words carried in']];
 items.forEach(function(it,i){var y=108+i*44;b+=arrow(240,y-6,240,y+4,'flowline')+box(30,y,420,38,'bx')+t(44,y+24,it[0],'f1t sm','start')+t(436,y+24,it[1],'tx sm','end');});
 return svg(480,340,b,'Anatomy of one sutra record, sutra 6.1.77, from the data fields');};
/* 16 mind map */
D.mindmap=function(){var N=[['Sounds','sound',-1,-1],['Pratyāhāra','maheshvara',1,-1],['Aṣṭādhyāyī','ashtadhyayi',-1,1],['Śiva Sūtras','shiva',1,1],['Practice','practice',0,-1.4],['Sources','resources',0,1.4]],b='';
 N.forEach(function(n,i){var x=240+n[2]*150,y=150+n[3]*88;b+='<line x1="240" y1="150" x2="'+x+'" y2="'+y+'" class="flowline"/>'+'<a href="#/'+n[1]+'"><rect x="'+(x-62)+'" y="'+(y-22)+'" width="124" height="44" rx="22" class="f'+(i%4+1)+' o3 mm"/><text x="'+x+'" y="'+(y+6)+'" class="tx b" text-anchor="middle">'+n[0]+'</text></a>';});
 b+='<circle cx="240" cy="150" r="46" class="f1 pulse"/><text x="240" y="146" class="onc b" text-anchor="middle">Sūtra</text><text x="240" y="164" class="onc b" text-anchor="middle">Nexus</text>';
 return svg(480,300,b,'Mind map linking sounds, pratyahara, Ashtadhyayi, Shiva Sutras, practice and sources');};
/* 17 roadmap */
D.roadmap=function(){var cu=C.curriculum,b='<path d="M30 60 H450" class="flowline dash" fill="none"/>';
 cu.forEach(function(c,i){var x=30+i*70;b+='<circle cx="'+x+'" cy="60" r="16" class="f'+(i%4+1)+'"/>'+t(x,66,String(i+1),'onc b')+t(x,100+(i%2)*36,c[0].split(' ')[0],'tx sm')+t(x,116+(i%2)*36,c[2]+' min','tm sm');});
 b+='<circle r="7" class="f3"><animateMotion dur="6s" repeatCount="indefinite" path="M30 60 H450"/></circle>'+t(240,190,'About '+cu.reduce(function(a,c){return a+c[2]},0)+' minutes in total','tm sm');
 return svg(480,205,b,'Roadmap of seven steps in the one-hour path');};
/* 18 varga grid */
D.varga=function(){var b='',rows=C.cons,nm=C.varga;rows.forEach(function(r,i){var y=14+i*46;b+=t(8,y+28,nm[i],'tm sm','start');r.forEach(function(c,j){var x=96+j*76;b+=box(x,y,68,40,'bx'+(j==4?' hl':''),10)+t(x+34,y+22,c[0],'dev tx')+t(x+34,y+36,c[1],'tm sm');});});
 b+=t(280,254,'Last column: the nasal of each row','f1t sm')+'<rect x="90" y="8" width="10" height="236" rx="5" class="f2 o3 scan"/>';
 return svg(480,266,b,'Grid of the five consonant rows with the nasal of each row highlighted');};
/* 19 loop */
D.loop=function(){var w=['Sound','Structure','Meaning','Use'],b='<circle cx="200" cy="120" r="80" class="s2" fill="none" stroke-width="2" stroke-dasharray="6 8"/>';
 w.forEach(function(s,i){var a=i*Math.PI/2-Math.PI/2,x=200+80*Math.cos(a),y=120+80*Math.sin(a);b+='<circle cx="'+x+'" cy="'+y+'" r="32" class="f'+(i+1)+'"/>'+t(x,y+5,s,'onc sm b');});
 b+='<g class="spin" style="transform-origin:200px 120px"><circle cx="200" cy="40" r="6" class="f3"/></g>'+t(200,125,'say it aloud','tm sm');
 return svg(400,250,b,'Four-step learning loop: sound, structure, meaning, use');};
/* 20 recension */
D.recension=function(){var b='',rows=[['This file (Vārttika numbering)',75,'20 + 10 + 45'],['Common recension per file note',77,'22 + 10 + 45']];
 rows.forEach(function(r,i){var y=40+i*80;b+=t(10,y-8,r[0]+' · '+r[2],'tx sm','start')+'<rect x="10" y="'+y+'" width="'+r[1]*5+'" height="34" rx="9" class="f'+(i*2+1)+' grow" style="transform-origin:10px '+(y+17)+'px;animation-delay:'+i*.3+'s"/>'+t(r[1]*5-6,y+23,String(r[1]),'onc b','end');});
 b+=t(10,200,'From the data meta note only.','tm sm','start')+t(10,220,'Which sūtras differ: UNKNOWN beyond the source.','tm sm','start');
 return svg(480,234,b,'Comparison of the 75 sutra count in this file with the 77 count noted for the common recension');};
/* 21 pipeline */
D.pipeline=function(){var s=['Open data files','Generator scripts','Local data.js','This app','Guide bot KB'],b='';
 s.forEach(function(n,i){var y=10+i*54;b+=box(120,y,240,40,'bx'+(i==3?' hl':''))+t(240,y+26,n,'tx');if(i<4)b+=arrow(240,y+42,240,y+62);});
 b+='<circle r="6" class="f3"><animateMotion dur="5s" repeatCount="indefinite" path="M240 30 V250"/></circle>';
 return svg(480,282,b,'Pipeline from open data files through generator scripts to the app and the guide bot');};
/* 22 leitner */
D.leitner=function(){var iv=[['Box 1','today'],['Box 2','1 day'],['Box 3','3 days'],['Box 4','7 days'],['Box 5','14 days']],b='';
 iv.forEach(function(v,i){var x=10+i*92,h=40+i*22;b+='<rect x="'+x+'" y="'+(130-h)+'" width="84" height="'+h+'" rx="10" class="f'+(i%4+1)+' o3"/>'+t(x+42,126-h+22,v[0],'tx sm b')+t(x+42,146,v[1],'tx sm');});
 b+='<path d="M60 168 C200 200 320 200 440 168" class="flowline dash" fill="none"/>'+t(240,196,'Right: move up a box · Wrong: back to box 1','tm sm');
 return svg(480,208,b,'Spaced ladder of five boxes with review gaps of today, 1, 3, 7 and 14 days');};
/* 23 it marker */
D.itMarker=function(){var b='';['a','i','u'].forEach(function(s,i){b+=box(30+i*80,40,68,56,'bx')+t(64+i*80,76,s,'tx big');});
 b+=box(270,40,68,56,'bx dim')+t(304,76,'ṇ','tm big')+'<g class="drop">'+'<line x1="270" y1="100" x2="338" y2="36" class="s3" stroke-width="4"/></g>'+t(304,120,'marker','tm sm')+t(135,120,'counted in the set','f1t sm');
 b+=t(220,160,'aṇ here = a i u. The marker is dropped','tx sm')+t(220,180,'(1.3.9 tasya lopaḥ; my reading)','tm sm')+t(220,200,'Another aṇ reaches the ṇ of line 6.','tm sm');
 return svg(440,212,b,'The marker ṇ is dropped, leaving a i u for the pratyahara an');};
/* 24 length histogram */
D.lenHist=function(){var bins=[0,0,0,0,0,0,0,0],lab=['≤5','6-10','11-15','16-20','21-30','31-45','46-80','81+'];
 X.ashta.forEach(function(r){var n=r[1].replace(/[\s]/g,'').length,i=n<=5?0:n<=10?1:n<=15?2:n<=20?3:n<=30?4:n<=45?5:n<=80?6:7;bins[i]++;});
 var mx=Math.max.apply(null,bins),b='';bins.forEach(function(v,i){var h=150*v/mx,x=20+i*55;b+='<rect x="'+x+'" y="'+(170-h)+'" width="46" height="'+h+'" rx="6" class="f'+(i%4+1)+' growy" style="animation-delay:'+i*.1+'s;transform-origin:'+(x+23)+'px 170px"/>'+t(x+23,164-h,String(v),'tx sm b')+t(x+23,190,lab[i],'tm sm');});
 b+=t(235,212,'Characters per sūtra, computed from the data','tm sm');
 return svg(470,226,b,'Histogram of sutra length in characters computed from the data');};
/* 25 anuvrtti share */
D.anuBars=function(){var A=C.stats.adhyaya,N=C.stats.anu,b='';Object.keys(A).forEach(function(k,i){var y=14+i*34,f=N[k]/A[k];b+=t(8,y+19,'Adhyāya '+k,'tx sm','start')+box(100,y,300,24,'bx',8)+'<rect x="100" y="'+y+'" width="'+300*f+'" height="24" rx="8" class="f2 grow" style="transform-origin:100px '+(y+12)+'px;animation-delay:'+i*.1+'s"/>'+t(408,y+18,Math.round(f*100)+'%','tx sm b','start');});
 b+=t(240,296,'Share of sūtras with anuvṛtti listed in the data','tm sm');
 return svg(480,310,b,'Share of sutras with anuvritti listed, per adhyaya, computed from the data');};
/* 26 hierarchy */
D.hierarchy=function(){var b=box(160,8,160,38,'bx hl')+t(240,33,'Aṣṭādhyāyī','tx b')+arrow(240,48,240,66)+box(90,68,300,38,'bx')+t(240,93,'8 adhyāyas (chapters)','tx')+arrow(240,108,240,126)+box(90,128,300,38,'bx')+t(240,153,'32 pādas (quarters)','tx')+arrow(240,168,240,186)+box(90,188,300,38,'bx hl')+t(240,213,C.stats.total.toLocaleString('en-US')+' sūtras in this data','tx b');
 b+=t(240,250,'Locus 6.1.77 = adhyāya 6 · pāda 1 · sūtra 77','tm sm');return svg(480,264,b,'Hierarchy of the Ashtadhyayi from adhyayas to padas to sutras');};
/* 27 sthana table bars (sound group counts) */
D.sthanaBars=function(){var rows=C.sthana,b='';rows.forEach(function(r,i){var y=10+i*36;b+=box(10,y,460,30,'bx',9)+'<rect x="10" y="'+y+'" width="8" height="30" rx="4" class="f'+(i%4+1)+'"/>'+t(26,y+20,r[0].split(' (')[0],'tx sm','start')+t(466,y+20,r[1].split(',')[0],'tm sm','end');});
 return svg(480,340,b,'List of the nine places of articulation with their first sound group');};
D.count=function(){return Object.keys(D).filter(function(k){return typeof D[k]=='function'&&k!='count'}).length};
})();
