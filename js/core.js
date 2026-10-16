/* Sūtra Nexus · core: display control, routing, menu, footer, progress. No network. */
(function(){
'use strict';
var N=window.Nexus={version:'1.0.0'};
var LS={get:function(k,d){try{var v=localStorage.getItem('nexus.'+k);return v==null?d:JSON.parse(v)}catch(e){return d}},set:function(k,v){try{localStorage.setItem('nexus.'+k,JSON.stringify(v))}catch(e){}}};
N.store=LS;
N.$=function(s,r){return (r||document).querySelector(s)};N.$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
N.esc=function(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')};
N.rooms=[
 {id:'start',ic:'🧭',label:'Start Here',desc:'A short path through the app and what each part offers'},
 {id:'maheshvara',ic:'🥁',label:'Māheśvara sūtras',desc:'The 14 lines and a pratyāhāra builder you can try'},
 {id:'ashtadhyayi',ic:'📜',label:'Aṣṭādhyāyī',desc:'Search and browse 3,983 sūtras with anuvṛtti and charts'},
 {id:'shiva',ic:'🔱',label:'Śiva Sūtras',desc:'The 75 sūtras of the Kashmir text, with source notes'},
 {id:'sound',ic:'🗣️',label:'Sound lab',desc:'Places of articulation, scripts, sandhi flows and drills'},
 {id:'practice',ic:'🎯',label:'Practice',desc:'Flashcards with a spaced ladder, quizzes and daily challenge'},
 {id:'ecosystem',ic:'🕸️',label:'Ecosystem',desc:'Glossary, mind map, sister topics, bridges and future hooks'},
 {id:'resources',ic:'🔗',label:'Resources',desc:'Links opened and checked as of 2026-10'},
 {id:'downloads',ic:'📥',label:'Downloads',desc:'Cheat sheets, a slide deck and a single-file copy'},
 {id:'about',ic:'ℹ️',label:'About',desc:'Purpose, sources, licences and the disclaimer'}];
/* ---------- display control ---------- */
var STEPS=[.85,1,1.15,1.3,1.5],root=document.documentElement;
var THEMES=[['aurora','Aurora'],['neon','Neon'],['holo','Holo'],['sunset','Sunset'],['light','Light'],['contrast','Contrast']];
function applyFs(i){i=Math.max(0,Math.min(STEPS.length-1,i));root.style.setProperty('--fscale',STEPS[i]);LS.set('fs',i);N.fs=i;
 var s=N.$('#fsReset');if(s)s.title='Text size '+Math.round(STEPS[i]*100)+'% (click for normal)'}
function applyTheme(t){root.setAttribute('data-theme',t);LS.set('theme',t);var s=N.$('#themeSel');if(s)s.value=t}
function applyMotion(off){root.setAttribute('data-motion',off?'off':'on');LS.set('motion',off?'off':'on');var b=N.$('#motionBtn');if(b){b.setAttribute('aria-pressed',off?'true':'false');b.title=off?'Motion is reduced. Click to turn animation on':'Click to reduce motion'}}
var reduced=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
applyFs(LS.get('fs',1));applyTheme(LS.get('theme','aurora'));applyMotion((LS.get('motion',reduced?'off':'on'))==='off');
function displayHTML(){return '<div id="display" role="group" aria-label="Display"><button type="button" id="fsDown" aria-label="Smaller text">A-</button><button type="button" id="fsReset" aria-label="Reset text size to normal" title="Normal text size">A</button><button type="button" id="fsUp" aria-label="Larger text">A+</button><label class="sr" for="themeSel">Theme</label><select id="themeSel">'+THEMES.map(function(t){return '<option value="'+t[0]+'">'+t[1]+'</option>'}).join('')+'</select><button type="button" id="motionBtn" aria-pressed="false" aria-label="Reduce motion">🎞️ <span class="sr">Reduce motion</span></button></div>'}
/* ---------- progress ---------- */
var P=LS.get('progress',{visited:{},quizBest:0,quizRuns:0,cards:{},badges:[],xp:0,daily:{},built:0,tours:0,facts:0});
N.progress=P;function save(){LS.set('progress',P)}
N.badgeDefs={explorer:['Explorer','Visited five rooms'],builder:['Builder','Built a pratyāhāra'],quiz80:['Sharp ear','Scored 80% or more on a quiz'],cards20:['Card keeper','Reviewed 20 flashcards'],daily:['Daily step','Finished a daily challenge'],tour:['Tourist','Finished a guided tour'],reader:['Reader','Opened five sūtras in the browser']};
N.award=function(id){if(P.badges.indexOf(id)<0){P.badges.push(id);P.xp+=25;save();N.toast('Badge earned: '+N.badgeDefs[id][0]);document.dispatchEvent(new CustomEvent('nexus:badge',{detail:id}))}};
N.bump=function(k,n){P[k]=(P[k]||0)+(n||1);save();if(k==='built'&&P.built>=1)N.award('builder');if(k==='opened'&&P.opened>=5)N.award('reader')};
N.addXp=function(n){P.xp+=n;save()};N.saveProgress=save;
N.toast=function(m){var t=N.$('#toast');if(!t){t=document.createElement('div');t.id='toast';t.setAttribute('role','status');t.style.cssText='position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:var(--c1);color:var(--onc);padding:10px 16px;border-radius:14px;z-index:300;font-weight:600;max-width:90vw;text-align:center;box-shadow:0 0 24px var(--glow)';document.body.appendChild(t)}
 t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(function(){t.style.display='none'},3200)};
/* ---------- shell ---------- */
var SOCIALS=[
 {id:'github',label:'GitHub',url:'https://github.com/cipher0x9',icon:'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'},
 {id:'x',label:'X',url:'https://x.com/Cypher0x9',icon:'M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z'},
 {id:'linkedin',label:'LinkedIn',url:'https://www.linkedin.com/in/luckylakshmanucwebex',icon:'M3 3h18v18H3z M7.2 9.8h2.4V17H7.2z M8.4 6.4a1.4 1.4 0 110 2.8 1.4 1.4 0 010-2.8z M11 9.8h2.3v1c.4-.7 1.2-1.2 2.3-1.2 2.2 0 2.7 1.4 2.7 3.3V17h-2.4v-3.5c0-.9 0-1.8-1.2-1.8s-1.3.9-1.3 1.8V17H11z',note:'simple mark'},
 {id:'hf',label:'Hugging Face',url:'https://huggingface.co/Cypher0x9',icon:'M12.025 1.13c-5.77 0-10.449 4.647-10.449 10.378 0 1.112.178 2.181.503 3.185.064-.222.203-.444.416-.577a.96.96 0 0 1 .524-.15c.293 0 .584.124.84.284.278.173.48.408.71.694.226.282.458.611.684.951v-.014c.017-.324.106-.622.264-.874s.403-.487.762-.543c.3-.047.596.06.787.203s.31.313.4.467c.15.257.212.468.233.542.01.026.653 1.552 1.657 2.54.616.605 1.01 1.223 1.082 1.912.055.537-.096 1.059-.38 1.572.637.121 1.294.187 1.967.187.657 0 1.298-.063 1.921-.178-.287-.517-.44-1.041-.384-1.581.07-.69.465-1.307 1.081-1.913 1.004-.987 1.647-2.513 1.657-2.539.021-.074.083-.285.233-.542.09-.154.208-.323.4-.467a1.08 1.08 0 0 1 .787-.203c.359.056.604.29.762.543s.247.55.265.874v.015c.225-.34.457-.67.683-.952.23-.286.432-.52.71-.694.257-.16.547-.284.84-.285a.97.97 0 0 1 .524.151c.228.143.373.388.43.625l.006.04a10.3 10.3 0 0 0 .534-3.273c0-5.731-4.678-10.378-10.449-10.378'}];
N.SOCIALS=SOCIALS;
var BADGES=[{label:'CypherMonkey Labs',url:'https://cyphermonkeylabs.com',icon:'M12 2a10 10 0 100 20 10 10 0 000-20zm0 2c.9 1 1.7 2.6 2.1 5H9.9C10.3 6.6 11.1 5 12 4zM4.3 11h3.6c-.1.7-.1 1.3-.1 2s0 1.3.1 2H4.3a8 8 0 010-4zm1 6h3c.3 1.4.8 2.600 1.400 3.600A8 8 0 015.300 17zm3-10h-3a8 8 0 014.400-3.600C8.700 4.400 8.600 5.600 8.300 7zM12 20c-.9-1-1.7-2.600-2.100-5h4.200c-.4 2.400-1.200 4-2.100 5zm2.300-7c.1-.7.1-1.300.1-2s0-1.300-.1-2h-4.600c-.1.700-.1 1.300-.1 2s0 1.300.1 2zm.9 7.600c.6-1 1.100-2.200 1.400-3.600h3a8 8 0 01-4.400 3.600zM16.100 15c.1-.7.1-1.300.1-2s0-1.300-.1-2h3.600a8 8 0 010 4zM15.700 9c-.3-1.400-.8-2.600-1.400-3.600A8 8 0 0118.700 9z'},
 {label:'GitHub organization',url:'https://github.com/CypherMonkeyLabs',icon:SOCIALS[0].icon},{label:'Socials',panel:true,icon:'M16 11a3 3 0 100-6 3 3 0 000 6zM8 11a3 3 0 100-6 3 3 0 000 6zm0 2c-2.3 0-7 1.200-7 3.500V19h14v-2.500C15 14.200 10.300 13 8 13zm8 0c-.3 0-.6 0-1 .1 1.100.800 2 1.900 2 3.400V19h6v-2.500c0-2.300-4.700-3.500-7-3.500z'}];
function ic(p){return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="'+p+'"/></svg>'}
function build(){
 var banner=N.$('#banner');
 banner.innerHTML='<div class="bn-top"><a class="brand" href="#/start"><span class="logo" aria-hidden="true">🪔</span><span class="bt"><b>Sūtra Nexus</b><small>Ancient rules. Living systems.</small></span></a><div class="bn-id">A lifelong student sharing what he learns about Sanskrit sound and grammar, free to use.</div>'+displayHTML()+'</div><nav class="bn-nav" aria-label="Rooms">'+N.rooms.map(function(r){return '<a href="#/'+r.id+'" data-room="'+r.id+'" title="'+N.esc(r.desc)+'"><span class="ic" aria-hidden="true">'+r.ic+'</span><span>'+N.esc(r.label)+'</span></a>'}).join('')+'</nav>';
 var w=document.createElement('button');w.id='wheel';w.type='button';w.setAttribute('aria-label','Open the full menu');w.setAttribute('aria-expanded','false');
 w.innerHTML='<svg viewBox="0 0 48 48" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="24" cy="24" r="20"/><circle cx="24" cy="24" r="6"/>'+[0,1,2,3,4,5,6,7].map(function(i){return '<line x1="24" y1="4" x2="24" y2="18" transform="rotate('+i*45+' 24 24)"/>'}).join('')+'</g></svg>';
 document.body.appendChild(w);
 var sc=document.createElement('div');sc.id='scrim';document.body.appendChild(sc);
 var d=document.createElement('nav');d.id='drawer';d.setAttribute('aria-label','Full menu');d.setAttribute('aria-hidden','true');
 d.innerHTML='<h2><span>Sūtra Nexus menu</span><button class="x" type="button" aria-label="Close menu">✕</button></h2>'+N.rooms.map(function(r){return '<a href="#/'+r.id+'" data-room="'+r.id+'"><span class="ic" aria-hidden="true">'+r.ic+'</span><span><b>'+N.esc(r.label)+'</b><span class="d">'+N.esc(r.desc)+'</span></span></a>'}).join('');
 document.body.appendChild(d);
 function open(o){d.classList.toggle('on',o);sc.classList.toggle('on',o);d.setAttribute('aria-hidden',o?'false':'true');w.setAttribute('aria-expanded',o?'true':'false');if(o){w.classList.add('show');setTimeout(function(){var a=N.$('a[aria-current=page]',d)||N.$('a',d);a&&a.focus()},60)}else{w.focus&&0}}
 N.menu=open;
 w.addEventListener('click',function(){open(!d.classList.contains('on'))});
 sc.addEventListener('click',function(){open(false)});N.$('.x',d).addEventListener('click',function(){open(false);w.focus()});
 d.addEventListener('click',function(e){if(e.target.closest('a'))open(false)});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&d.classList.contains('on')){open(false);w.focus()}});
 /* auto-hide: reveal on scroll up / pointer near edge / touch, hide after 3s idle */
 var hideT;function reveal(){w.classList.add('show');clearTimeout(hideT);hideT=setTimeout(function(){if(!d.classList.contains('on')&&document.activeElement!==w)w.classList.remove('show')},3200)}
 var lastY=scrollY;addEventListener('scroll',function(){if(scrollY<lastY)reveal();lastY=scrollY},{passive:true});
 addEventListener('mousemove',function(e){if(e.clientX<40)reveal()},{passive:true});addEventListener('touchstart',function(e){if(e.touches[0].clientX<40)reveal()},{passive:true});
 /* display events */
 N.$('#fsDown').onclick=function(){applyFs(N.fs-1)};N.$('#fsUp').onclick=function(){applyFs(N.fs+1)};N.$('#fsReset').onclick=function(){applyFs(1)};
 N.$('#themeSel').onchange=function(e){applyTheme(e.target.value)};N.$('#motionBtn').onclick=function(){applyMotion(root.getAttribute('data-motion')!=='off')};
 applyFs(N.fs);applyTheme(LS.get('theme','aurora'));applyMotion(root.getAttribute('data-motion')==='off');
 /* footer */
 var f=N.$('#site');
 f.innerHTML='<div class="ft-in"><h2 style="margin:0 0 6px">Sūtra Nexus · Ancient rules. Living systems.</h2><p>Sūtra Nexus is an independent, free, learning-only student project. It respects every company, tradition and vendor; trademarks and sources belong to their owners. If something should be removed or corrected, it will be handled promptly: please write through <a href="https://cyphermonkeylabs.com/#contact" rel="noopener">https://cyphermonkeylabs.com/#contact</a>. Nothing here is sold, and I am happy to volunteer for any organization.</p><div class="badges">'+BADGES.map(function(b,i){return b.panel?'<button type="button" class="badge3d" id="socBtn" aria-expanded="false" aria-controls="socials">'+ic(b.icon)+'<span>'+b.label+'</span></button>':'<a class="badge3d" href="'+b.url+'" rel="noopener" target="_blank">'+ic(b.icon)+'<span>'+b.label+'</span></a>'}).join('')+'</div><div id="socials" role="region" aria-label="Socials">'+SOCIALS.map(function(s){return '<a href="'+s.url+'" rel="noopener" target="_blank">'+ic(s.icon)+'<span>'+s.label+' · '+s.url.replace('https://','')+'</span></a>'}).join('')+'</div><p style="text-align:center;margin-top:14px">© 2026 CypherMonkeyLabs</p></div>';
 N.$('#socBtn').onclick=function(){var s=N.$('#socials'),on=!s.classList.contains('on');s.classList.toggle('on',on);this.setAttribute('aria-expanded',on)};
}
/* ---------- routing ---------- */
N.room=function(){return (location.hash.replace(/^#\/?/,'').split(/[/?]/)[0])||'start'};
N.go=function(id,q){location.hash='#/'+id+(q?'/'+q:'')};
N.renderers={};N.rendered={};N.needsData={ashtadhyayi:1,sound:1};
N.loadData=function(){if(N._ld||window.NEXUS_DATA.ashta.length||window.NEXUS_STANDALONE)return;N._ld=1;var ds=document.createElement('script');ds.src='js/data-ashta.js';document.body.appendChild(ds)};
N.dataReady=function(cb){N.loadData();if(window.NEXUS_DATA.ashta.length)cb();else document.addEventListener('nexus:data',function f(){document.removeEventListener('nexus:data',f);cb()})};
function route(){var id=N.room();if(!N.rooms.some(function(r){return r.id===id}))id='start';
 N.$$('.room').forEach(function(s){s.classList.toggle('on',s.id==='room-'+id)});
 N.$$('[data-room]').forEach(function(a){if(a.getAttribute('data-room')===id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 if(!N.rendered[id]&&N.renderers[id]){N.rendered[id]=1;var el=N.$('#room-'+id);if(N.needsData[id]&&!window.NEXUS_DATA.ashta.length){el.innerHTML='<p class="mute" role="status">Loading the sūtra data…</p>';document.body.classList.add('ld');N.dataReady(function(){document.body.classList.remove('ld');N.renderers[id](el);N.counters&&N.counters();document.dispatchEvent(new CustomEvent('nexus:rendered',{detail:id}))})}else N.renderers[id](el)}
 var r=N.rooms.filter(function(x){return x.id===id})[0];document.title=r.label+' · Sūtra Nexus';
 P.visited[id]=1;save();if(Object.keys(P.visited).length>=5)N.award('explorer');
 var a=N.$('.bn-nav a[aria-current=page]');if(a&&a.scrollIntoView&&!document.querySelector('.bn-nav:hover'))try{a.parentNode.scrollLeft=a.offsetLeft-20}catch(e){}
 scrollTo(0,0);document.dispatchEvent(new CustomEvent('nexus:room',{detail:id}));
 var m=N.$('#room-'+id+' h1');if(m&&N.userNav){m.setAttribute('tabindex','-1');m.focus({preventScroll:true})}N.userNav=true;}
N.init=function(){build();var m=N.$('#main');N.rooms.forEach(function(r){var s=document.createElement('section');s.className='room';s.id='room-'+r.id;s.setAttribute('aria-label',r.label);m.appendChild(s)});
 addEventListener('hashchange',route);route();document.body.classList.remove('boot');
 /* counters */
 document.addEventListener('nexus:room',function(){setTimeout(counters,50)});counters();
 var fh=N.$('#site');function bumpBot(){var b=N.$('#guidebot-root');if(!b)return;var r=fh.getBoundingClientRect(),over=Math.max(0,innerHeight-r.top);b.style.setProperty('--gb-lift',over+'px')}
 addEventListener('scroll',bumpBot,{passive:true});addEventListener('resize',bumpBot);setInterval(bumpBot,600);
 setTimeout(N.loadData,2400);
 setTimeout(function(){var bs=document.createElement('script');bs.src='guidebot/kb.js';bs.onload=function(){var g=document.createElement('script');g.src='guidebot/guidebot.js';document.body.appendChild(g)};if(!window.NEXUS_STANDALONE)document.body.appendChild(bs)},1800);
};
function counters(){N.$$('[data-count]').forEach(function(e){if(e._done||!e.offsetParent)return;e._done=1;var to=+e.getAttribute('data-count'),t0=null,off=root.getAttribute('data-motion')==='off';if(off){e.textContent=to.toLocaleString('en-US');return}
 function step(ts){if(!t0)t0=ts;var k=Math.min(1,(ts-t0)/900);e.textContent=Math.round(to*(1-Math.pow(1-k,3))).toLocaleString('en-US');if(k<1)requestAnimationFrame(step)}requestAnimationFrame(step)})}
N.counters=counters;
})();
