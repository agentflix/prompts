// Gera o deck HTML (1 arquivo, fonte e foto embutidas)
const fs=require('fs'),path=require('path');
const PROFILE=JSON.parse(fs.readFileSync(process.env.PROFILE_JSON||path.join(__dirname,'..','assets','profile.default.json'),'utf8'));
const PROF=PROFILE.short;let DISC='';
const PHOTO=process.env.PHOTO||path.join(process.cwd(),'foto.jpg');
if(!fs.existsSync(PHOTO)){console.error('Foto nao encontrada: '+PHOTO+' (use PHOTO=/caminho/foto.jpg ou coloque foto.jpg na pasta atual; veja crop_photo.sh)');process.exit(1)}
const photo='data:image/jpeg;base64,'+fs.readFileSync(PHOTO).toString('base64');
const font='data:font/woff2;base64,'+fs.readFileSync(path.join(__dirname,'..','assets','lexend-latin.woff2')).toString('base64');
const ACC={0:'#6B1E2E',4:'#6B1E2E',5:'#1F5F6B',6:'#5B6A1F'};

// ------------------------------------------------------------ conteúdo
const D=require(path.resolve(process.argv[3]));const S=D.S;DISC=D.DISC;

// ------------------------------------------------------------ ícones (traço, 24x24)
const IC={
 landmark:'<path d="M3 21h18M5 21V10M9 21V10M15 21V10M19 21V10M2 10l10-6 10 6z"/>',
 link:'<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
 sword:'<path d="M14.5 17.5 3 6V3h3l11.5 11.5M13 19l6-6M16 16l4 4M19 21l2-2"/>',
 swords:'<path d="M5 19 19 5M14 5h5v5M19 19 5 5M10 5H5v5"/>',
 book:'<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2zM22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
 sprout:'<path d="M12 22V10M12 10C12 6 9 4 5 4c0 4 2 6 7 6zM12 13c0-3 2-5 6-5 0 3-2 5-6 5z"/>',
 pen:'<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
 hammer:'<path d="M14 6l4 4M9 11l7-7 4 4-7 7zM8 12l-5 5 4 4 5-5"/>',
 users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 castle:'<path d="M3 21V7h3v3h3V7h3v3h3V7h3v14zM10 21v-4a2 2 0 0 1 4 0v4"/>',
 home:'<path d="M3 11l9-8 9 8M5 10v11h14V10M10 21v-6h4v6"/>',
 coins:'<circle cx="12" cy="12" r="9"/><path d="M12 7v10M9 9.5h4.2a1.8 1.8 0 0 1 0 3.6H9.8a1.8 1.8 0 0 0 0 3.6H15"/>',
 map:'<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14"/>',
 cross:'<path d="M12 2v20M5 8h14"/>',
 crown:'<path d="M3 19h18M4 19 3 8l5 4 4-7 4 7 5-4-1 11z"/>',
 pause:'<path d="M8 5v14M16 5v14" stroke-width="3"/>',
 mountain:'<path d="M3 20 9 8l4 7 3-5 5 10z"/>',
 wave:'<path d="M2 12c2-3 4-3 6 0s4 3 6 0 4-3 6 0M2 18c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/>',
 layers:'<path d="M12 3 2 8l10 5 10-5zM2 13l10 5 10-5"/>',
 drop:'<path d="M12 3s7 7 7 12a7 7 0 0 1-14 0c0-5 7-12 7-12z"/>',
 rain:'<path d="M7 15a4 4 0 0 1 0-8 5 5 0 0 1 9.6 1A3.5 3.5 0 0 1 17 15M8 19v2M12 18v3M16 19v2"/>',
 factory:'<path d="M2 21V10l6 4V10l6 4V6h4v15zM2 21h20"/>',
 city:'<path d="M3 21V8h7v13M10 21V3h8v18M6 12h1M6 16h1M13 7h2M13 11h2M13 15h2"/>',
 phone:'<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
 ship:'<path d="M3 17h18l-2 4H5zM5 17V9l7-3 7 3v8M12 6v11"/>',
 globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 wind:'<path d="M3 8h11a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h8"/>',
 bulb:'<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1V18h6v-1.2c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2z"/>'};
const ico=(n,sz=36)=>`<svg viewBox="0 0 24 24" width="${sz}" height="${sz}" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${IC[n]}</svg>`;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const rv=d=>`class="rv" style="--d:${d}"`;

// ------------------------------------------------------------ slides
function body(s,n){
const tag=s.tag?`<div class="tag">${esc(s.tag)}</div>`:'';
const key=s.key?`<div class="key rv" style="--d:5"><span class="kic">${ico('bulb',30)}</span><div><b>Ideia-chave</b>${esc(s.key)}</div></div>`:'';
switch(s.k){
case'cover':return{cls:'cover-s',html:`<div class="cover"><div class="ct"><div class="kick rv" style="--d:0">${esc(s.who)}</div><h1 class="rv${s.title.length>18?' sm':''}" style="--d:1">${esc(s.title)}</h1><div class="sub rv" style="--d:2">${esc(s.sub)}</div><div class="bar rv" style="--d:3"></div>${s.meta.map((m,i)=>`<p class="rv" style="--d:${4+i}">${esc(m)}</p>`).join('')}</div><div class="ph rv pop" style="--d:2"><img src="${photo}" alt="Retrato da professora"></div></div>`};
case'timeline':{const pos=y=>((y-s.from)/(s.to-s.from)*100).toFixed(1);
 return{html:`<div class="hd"><h2>${esc(s.title)}</h2></div><div class="bd"><div class="tl"><div class="tl-line"></div>${s.pts.map((p,i)=>`<div class="tl-n ${i%2?'dn':'up'}" style="left:${pos(+p[0])}%;--d:${i+2}"><div class="tl-t"><b>${esc(p[0])}</b><span>${esc(p[1])}</span></div><i></i></div>`).join('')}</div><div class="note rv" style="--d:8">${esc(s.sub)}</div></div>`}}
case'agenda':return{html:`<div class="hd"><h2>${esc(s.title)}</h2></div><div class="bd"><div class="grid g3">${s.items.map((x,j)=>`<div class="card ag rv" style="--d:${j};--acc:${ACC[4+j]}"><div class="ic">${ico(x[3],40)}</div><div class="chip">${esc(x[0])}</div><h3>${esc(x[1])}</h3><p>${esc(x[2])}</p></div>`).join('')}</div><div class="note rv" style="--d:4">${esc(s.note)}</div></div>`};
case'question':return{html:`<span class="qmark" aria-hidden="true">?</span><div class="hd">${tag}<h2 class="lt">${esc(s.title)}</h2></div><div class="bd">${s.qs.map((q,i)=>`<div class="q rv" style="--d:${i+1}">${esc(q)}</div>`).join('')}${s.sub?`<div class="qsub rv" style="--d:4">${esc(s.sub)}</div>`:''}</div>`};
case'cards':{const g=s.cards.length>3?'g2':'g3';
 return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="grid ${g}">${s.cards.map((c,j)=>`<div class="card rv" style="--d:${j}"><div class="ch"><div class="ic">${ico(c[2])}</div><h3>${esc(c[0])}</h3>${c[3]?`<span class="bign">${esc(c[3])}</span>`:''}</div><p>${esc(c[1])}</p></div>`).join('')}</div>${key}</div>`}}
case'swords':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="duel"><div class="side rv" style="--d:0"><div class="ic xl">${ico(s.left[3],54)}</div><small>${esc(s.left[0])}</small><h3>${esc(s.left[1])}</h3><p>${esc(s.left[2])}</p></div><div class="vs rv pop" style="--d:2"><div class="vsc">${ico('swords',44)}</div><span>${esc(s.mid)}</span></div><div class="side alt rv" style="--d:1"><div class="ic xl">${ico(s.right[3],54)}</div><small>${esc(s.right[0])}</small><h3>${esc(s.right[1])}</h3><p>${esc(s.right[2])}</p></div></div><div class="key rv" style="--d:4"><span class="kic">${ico('bulb',30)}</span><div><b>Para a Igreja</b>${esc(s.key.replace(/^Para a Igreja, /,'').replace(/^./,c=>c.toUpperCase()))}</div></div></div>`};
case'hub':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="hubw"><div class="hubc rv pop" style="--d:0"><div class="ic xl">${ico('landmark',52)}</div><b>${esc(s.hub)}</b></div><svg class="hubl" viewBox="0 0 1000 70" preserveAspectRatio="none" aria-hidden="true"><path class="ln" style="--d:2" d="M500 0V30M500 30H166V70M500 30V70M500 30H834V70"/></svg><div class="grid g3 hubn">${s.nodes.map((c,j)=>`<div class="card rv" style="--d:${j+2}"><div class="ch"><div class="ic">${ico(c[2])}</div><h3>${esc(c[0])}</h3></div><p>${esc(c[1])}</p></div>`).join('')}</div></div></div>`};
case'three':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="grid g3">${s.cols.map((c,j)=>`<div class="card tall rv" style="--d:${j}"><div class="ch"><div class="ic xl" style="margin:0">${ico(c[3],48)}</div>${c[4]?`<span class="big3">${esc(c[4])}</span>`:''}</div><div class="chip">${esc(c[0])}</div><h3>${esc(c[1])}</h3><p>${esc(c[2])}</p></div>`).join('')}</div><div class="note rv" style="--d:4">${esc(s.note)}</div></div>`};
case'versus':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="duel vsr"><div class="side rv" style="--d:0"><div class="ic xl">${ico(s.l[1],50)}</div><h3>${esc(s.l[0])}</h3><ul>${s.l[2].map(t=>`<li>${esc(t)}</li>`).join('')}</ul></div><div class="vsc sm rv pop" style="--d:2">×</div><div class="side alt rv" style="--d:1"><div class="ic xl">${ico(s.r[1],50)}</div><h3>${esc(s.r[0])}</h3><ul>${s.r[2].map(t=>`<li>${esc(t)}</li>`).join('')}</ul></div></div><div class="grid g2 strip">${s.foot.map((f,j)=>`<div class="pill rv" style="--d:${3+j}"><b>${esc(f[0])}</b>${esc(f[1])}</div>`).join('')}</div></div>`};
case'steps':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="steps">${s.steps.map((t,j)=>`<div class="step rv" style="--d:${j}"><span>${j+1}</span><p>${esc(t)}</p></div>`).join('')}</div><div class="note rv" style="--d:4">${esc(s.foot)}</div></div>`};
case'reading':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><blockquote class="rv" style="--d:0">${esc(s.quote)}<cite>${esc(s.cite)}</cite></blockquote><div class="ask rv" style="--d:2">${esc(s.ask)}</div><div class="note rv" style="--d:3">${esc(s.foot)}</div></div>`};
case'pyramid':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="pyr">${s.tiers.map((t,j)=>`<div class="tier t${j} rv" style="--d:${3-j}"><b>${esc(t)}</b></div><p class="tn n${j} rv" style="--d:${4-j}">${esc(s.notes[j])}</p>`).join('')}<div class="fl fd rv" style="--d:5"><span>${esc(s.down)}</span></div><div class="fl fu rv" style="--d:6"><span>${esc(s.up)}</span></div></div></div>`};
case'flow':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="flow">${s.steps.map((c,j)=>`<div class="fs rv" style="--d:${j}"><div class="fn">${j+1}</div><h3>${esc(c[0])}</h3><p>${esc(c[1])}</p></div>${j<s.steps.length-1?`<div class="fa rv" style="--d:${j}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></div>`:''}`).join('')}</div>${s.note?`<div class="note rv" style="--d:5">${esc(s.note)}</div>`:''}</div>`};
case'bars':return{html:`<div class="hd">${tag}<h2>${esc(s.title)}</h2></div><div class="bd"><div class="bars">${s.bars.map((b,j)=>`<div class="brow rv" style="--d:${j}"><div class="bl">${esc(b.label)}</div><div class="bt"><div class="bf" style="width:${b.pct}%;background:${b.c}"><span>${b.pct}%</span></div></div><div class="bn">${esc(b.txt)}</div></div>`).join('')}</div>${s.note?`<div class="note rv" style="--d:4">${esc(s.note)}</div>`:''}</div>`};
case'pause':return{html:`<div class="hd"><div class="tag">Ponto de parada · 50 min</div><div class="ph-row"><div class="pz rv pop" style="--d:0">${ico('pause',44)}</div><h2 class="lt">${esc(s.title)}</h2></div></div><div class="bd"><div class="grid g2 pg"><div class="pnl rv" style="--d:1"><b>O que ficou</b><ul>${s.kept.map(t=>`<li>${esc(t)}</li>`).join('')}</ul></div><div class="pnl alt rv" style="--d:2"><b>Na próxima aula</b><h3>${esc(s.next)}</h3><div class="ret"><small>Comece por</small>${esc(s.ask)}</div></div></div></div>`};
case'about':return{html:`<div class="about"><div class="ph sm rv pop" style="--d:0"><img src="${photo}" alt="Retrato da professora"></div><div><div class="kick dark rv" style="--d:1">${esc(s.title)}</div><h2 class="rv" style="--d:1">${esc(s.name)}</h2><div class="role rv" style="--d:2">${esc(s.role)}</div><ul class="facts">${s.facts.map((f,i)=>`<li class="rv" style="--d:${3+i}">${esc(f)}</li>`).join('')}</ul><a class="btn rv" style="--d:7" href="${s.lattes}" target="_blank" rel="noopener">Currículo Lattes</a></div></div>`};
case'close':return{html:`<div class="hd"><h2>${esc(s.title)}</h2></div><div class="bd"><div class="pts">${s.points.map((p,j)=>`<div class="pt rv" style="--d:${j}"><span>${j+1}</span><p>${esc(p)}</p></div>`).join('')}</div><div class="note rv" style="--d:4">${esc(s.next)}</div></div>`};}
}
const TOT={};S.forEach(x=>{TOT[x.au]=(TOT[x.au]||0)+x.min});const START=[];{const acc={};S.forEach((x,k)=>{START[k]=acc[x.au]||0;acc[x.au]=START[k]+x.min})}
function slide(s,i){const n=i+1,b=body(s,n),dark=(s.k==='cover'||s.k==='question'||s.k==='pause')?' dark':'';
 const segs=s.k==='cover'?'':`<nav class="segs" aria-label="Ir para o slide">${S.map((x,k)=>`<button type="button" class="seg" data-go="${k}" style="--c:${ACC[x.a]}" aria-label="Slide ${k+1}"></button>`).join('')}</nav>`;
 return `<section class="slide${dark}" id="s${n}" role="group" aria-roledescription="slide" aria-label="Slide ${n} de ${S.length}" data-title="${esc(s.title)}" style="--acc:${ACC[s.a]}"><div class="in">${b.html}</div>${s.k!=='cover'?`<div class="pill-t" aria-label="Aula ${s.au} de 3">${s.k==='pause'?`Planejado: ${TOT[s.au]} de 50 min`:`Aula ${s.au} de 3 · ${s.min} min · min ${START[i]}–${START[i]+s.min}`}</div>`:''}${s.k!=='cover'?`<footer><span>${PROF} · ${DISC}</span>${segs}<span>${n} / ${S.length}</span></footer>`:''}</section>`;}

// ------------------------------------------------------------ CSS
const css=`@font-face{font-family:'Lexend';src:url(${font}) format('woff2');font-weight:100 900;font-style:normal;font-display:swap}
:root{--burg:#6B1E2E;--burgD:#4A1220;--gold:#C79A3B;--goldT:#8A5F0A;--parch:#F7F1E5;--ink:#241C2B;--mut:#5A5063;--ease:cubic-bezier(.2,.7,.2,1);--f:'Lexend','Segoe UI',system-ui,sans-serif}
*{box-sizing:border-box;margin:0}html,body{height:100%;background:#1c1418;font-family:var(--f);-webkit-font-smoothing:antialiased}
body{display:flex;align-items:center;justify-content:center;overflow:hidden}
#stage{width:1280px;height:720px;position:relative;transform-origin:center;flex:none}
.slide{position:absolute;inset:0;overflow:hidden;color:var(--ink);visibility:hidden;opacity:0;transform:translateX(28px);transition:opacity .3s var(--ease),transform .3s var(--ease),visibility 0s .3s;
 background-color:var(--parch);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44'%3E%3Cpath d='M22 8l4 4-4 4-4-4z' fill='%23C79A3B' fill-opacity='.10'/%3E%3C/svg%3E")}
.slide.on{visibility:visible;opacity:1;transform:none;transition:opacity .3s var(--ease),transform .3s var(--ease),visibility 0s}.slide.prev{transform:translateX(-28px)}
.slide::before{content:'';position:absolute;left:0;top:0;bottom:0;width:18px;background:var(--acc)}
.slide::after{content:'';position:absolute;right:-150px;bottom:-150px;width:400px;height:400px;border-radius:50%;border:2px solid rgba(199,154,59,.4);box-shadow:0 0 0 30px rgba(199,154,59,.07),0 0 0 60px rgba(199,154,59,.04);pointer-events:none}
.slide.dark{background:radial-gradient(circle at 80% 20%,#8a2a3f,var(--burg) 55%,var(--burgD));color:var(--parch)}.slide.dark::before{background:var(--gold)}
.in{position:absolute;inset:0;padding:52px 90px 88px 100px;z-index:1;display:flex;flex-direction:column}
.hd{flex:none}.bd{flex:1;display:flex;flex-direction:column;justify-content:center;gap:22px;min-height:0}
h1{font-weight:700;font-size:92px;line-height:1.02;color:var(--parch);letter-spacing:-.02em}
h2{font-weight:700;font-size:54px;line-height:1.1;color:var(--burg);margin-bottom:14px;letter-spacing:-.015em;text-wrap:balance}.lt{color:var(--parch)}
.tag{font-size:20px;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);font-weight:600;margin-bottom:10px}.dark .tag{color:#F0CB72}
footer{position:absolute;left:100px;right:90px;bottom:24px;display:flex;align-items:center;justify-content:space-between;gap:20px;font-size:19px;color:var(--mut);z-index:2}.dark footer{color:#e8d9cc}
.segs{display:flex;gap:4px;align-items:center}.seg{all:unset;box-sizing:border-box;cursor:pointer;width:20px;height:16px;display:flex;align-items:center}
.seg::before{content:'';width:100%;height:6px;border-radius:3px;background:var(--c);opacity:.28;transition:opacity .2s,height .2s}.seg:hover::before{opacity:.6}.seg.cur::before{opacity:1;height:10px}.dark .seg::before{background:#F0CB72}
.seg:focus-visible,a:focus-visible,.nav:focus-visible{outline:3px solid var(--gold);outline-offset:3px;border-radius:4px}
.grid{display:grid;gap:22px}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}
.card{position:relative;background:#fff;border-radius:20px;padding:24px 26px;box-shadow:0 6px 22px rgba(74,18,32,.12);border-top:6px solid var(--acc)}
.card h3{font-weight:600;font-size:31px;color:var(--acc);line-height:1.15;text-wrap:balance}.card p{font-size:26px;line-height:1.38;font-weight:400}
.ch{display:flex;align-items:center;gap:16px;margin-bottom:14px}
.ic{flex:none;width:58px;height:58px;border-radius:16px;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center}.ic.xl{width:84px;height:84px;border-radius:22px;margin-bottom:12px}
.chip{display:inline-block;background:var(--acc);color:#fff;border-radius:99px;padding:5px 18px;font-size:20px;font-weight:600;margin:4px 0 10px}
.card.tall,.card.ag{padding:28px}.card.ag .ic{margin-bottom:14px;width:70px;height:70px}.card.ag h3{font-size:31px;margin-bottom:8px}
.bign{margin-left:auto;white-space:nowrap;font-weight:700;font-size:40px;line-height:1;color:var(--goldT);letter-spacing:-.02em}.g2{gap:18px}.g2 .card{padding:16px 24px}.g2 .card p{font-size:24px;line-height:1.3}.g2 .ch{margin-bottom:8px}.g2 .ic{width:54px;height:54px}
.key{display:flex;align-items:center;gap:20px;padding:14px 24px;border-radius:16px;background:rgba(255,255,255,.75);border:2px solid var(--acc);font-size:26px;line-height:1.3}
.key b{display:block;font-size:17px;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin-bottom:2px;font-weight:600}.kic{flex:none;width:52px;height:52px;border-radius:50%;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center}
.note{font-size:25px;color:var(--mut);border-left:5px solid var(--gold);padding-left:18px;line-height:1.35}
.kick{font-size:21px;letter-spacing:.16em;text-transform:uppercase;color:#F0CB72;margin-bottom:20px;font-weight:500}.kick.dark{color:var(--goldT);font-weight:600}
.cover{display:flex;height:100%;align-items:center;justify-content:space-between;gap:30px}.cover .ct{max-width:720px}.sub{font-weight:500;font-size:36px;color:#F0CB72;margin-top:14px}
.bar{width:120px;height:5px;background:var(--gold);margin:30px 0 24px}.cover p{font-size:25px;line-height:1.6;color:#f4eadf}
.ph{width:380px;height:380px;border-radius:50%;overflow:hidden;border:8px solid var(--gold);box-shadow:0 18px 50px rgba(0,0,0,.4);flex:none}.ph img{width:100%;height:100%;object-fit:cover;display:block}.ph.sm{width:320px;height:320px}
.qmark{position:absolute;right:70px;bottom:-60px;font:700 520px var(--f);color:#F0CB72;opacity:.07;line-height:1;pointer-events:none}
.q{background:rgba(255,255,255,.10);border:2px solid rgba(240,203,114,.6);border-radius:20px;padding:28px 34px;font-size:36px;line-height:1.3;font-weight:500;max-width:1010px}
.steps{display:grid;grid-template-columns:1fr 1fr;gap:24px}.step{display:flex;gap:18px;align-items:center;background:#fff;border-radius:20px;padding:30px 26px;box-shadow:0 6px 22px rgba(74,18,32,.12);border-top:6px solid var(--acc)}
.step span,.pt span{flex:none;width:58px;height:58px;border-radius:50%;background:var(--acc);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:28px}.step p,.pt p{font-size:28px;line-height:1.3}
blockquote{background:#fff;border-left:8px solid var(--acc);border-radius:16px;padding:28px 34px;font-size:32px;line-height:1.4;font-weight:400;box-shadow:0 6px 22px rgba(74,18,32,.12)}cite{display:block;font-size:20px;color:var(--mut);margin-top:12px;font-style:normal}
.ask{background:var(--acc);color:#fff;border-radius:16px;padding:22px 30px;font-size:29px;font-weight:500;line-height:1.3}
.pts{display:grid;gap:18px}.pt{display:flex;gap:22px;align-items:center;background:#fff;border-radius:20px;padding:26px 28px;box-shadow:0 6px 22px rgba(74,18,32,.12);border-left:8px solid var(--acc)}
/* linha do tempo */
.tl{position:relative;height:360px;margin:0 80px}.tl-line{position:absolute;left:0;right:0;top:50%;height:8px;margin-top:-4px;background:linear-gradient(90deg,var(--burg),var(--gold));border-radius:4px;transform-origin:left}
.tl-n{position:absolute;top:50%;width:0}.tl-n i{position:absolute;left:-14px;top:-14px;width:28px;height:28px;border-radius:50%;background:#fff;border:7px solid var(--burg);box-shadow:0 2px 8px rgba(0,0,0,.2)}
.tl-t{position:absolute;left:-140px;width:280px;text-align:center}.tl-t b{display:block;font-size:56px;font-weight:700;color:var(--burg);line-height:1}.tl-t span{display:block;font-size:25px;line-height:1.25;margin-top:6px}
.tl-n.up .tl-t{bottom:36px}.tl-n.dn .tl-t{top:36px}.tl-n:last-child .tl-t{left:-215px;text-align:right}.tl-n:nth-of-type(2) .tl-t{left:-40px;text-align:left;width:300px}
/* duelo / versus */
.duel{display:grid;grid-template-columns:1fr auto 1fr;gap:20px;align-items:stretch}.side{background:#fff;border-radius:22px;padding:24px 26px;box-shadow:0 6px 22px rgba(74,18,32,.12);border-top:6px solid var(--acc);text-align:center}
.side.alt{border-top-color:var(--gold)}.side.alt .ic{background:var(--gold);color:#241C2B}.side small{display:block;font-size:19px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);font-weight:600}.side h3{font-weight:700;font-size:36px;color:var(--acc);margin:4px 0}.side p{font-size:26px}
.side .ic{margin:0 auto 10px}.vsr .side{text-align:left}.vsr .side .ic{margin:0 0 10px}.vsr .side h3{font-size:34px}.side ul{list-style:none;padding:0}.side li{font-size:25px;line-height:1.3;padding-left:24px;position:relative;margin-top:8px}.side li::before{content:'';position:absolute;left:0;top:11px;width:11px;height:11px;border-radius:50%;background:var(--gold)}
.vs{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;width:200px;text-align:center;font-size:21px;font-weight:600;color:var(--burg);line-height:1.2}.vsc{width:84px;height:84px;border-radius:50%;background:var(--burg);color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 8px rgba(199,154,59,.35)}.vsc.sm{width:70px;height:70px;font-size:40px;font-weight:700;align-self:center}
.strip{gap:18px}.pill{background:rgba(255,255,255,.8);border:2px solid var(--acc);border-radius:16px;padding:14px 22px;font-size:24px;line-height:1.3}.pill b{display:block;font-size:17px;letter-spacing:.1em;text-transform:uppercase;color:var(--acc);font-weight:600}
/* hub */
.hubw{display:flex;flex-direction:column;align-items:center}.hubc{display:flex;align-items:center;gap:18px;background:var(--burg);color:#fff;border-radius:99px;padding:10px 40px 10px 12px;box-shadow:0 0 0 8px rgba(199,154,59,.35)}.hubc .ic{margin:0;background:#fff;color:var(--burg);width:76px;height:76px}.hubc b{font-size:36px;font-weight:700}
.hubl{width:100%;height:50px}.hubl path{fill:none;stroke:var(--gold);stroke-width:5;vector-effect:non-scaling-stroke;stroke-linecap:round}.hubn{width:100%}
/* piramide */
.pyr{position:relative;height:400px}.tier{position:absolute;left:0;width:520px;height:92px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:30px}
.t0{top:0;background:#4A1220;clip-path:polygon(36% 0,64% 0,73% 100%,27% 100%)}.t1{top:102px;background:#6B1E2E;clip-path:polygon(27% 0,73% 0,82% 100%,18% 100%)}.t2{top:204px;background:#8f3a4b;clip-path:polygon(18% 0,82% 0,91% 100%,9% 100%)}.t3{top:306px;background:#C79A3B;color:#241C2B;clip-path:polygon(9% 0,91% 0,100% 100%,0% 100%)}
.tn{position:absolute;left:580px;width:440px;height:92px;display:flex;align-items:center;font-size:24px;line-height:1.28}.n0{top:0}.n1{top:102px}.n2{top:204px}.n3{top:306px}
.fl{position:absolute;top:0;width:62px;height:398px;display:flex;align-items:center;justify-content:center}.fd{left:1032px}.fu{left:1100px}
.fl::before{content:'';position:absolute;left:50%;margin-left:-3px;top:8px;bottom:8px;width:6px;border-radius:3px;background:var(--acc)}
.fd::after,.fu::after{content:'';position:absolute;left:50%;margin-left:-14px;border:14px solid transparent}.fd::after{bottom:-4px;border-top:20px solid var(--acc);border-bottom:0}.fu::after{top:-4px;border-bottom:20px solid var(--gold);border-top:0}.fu::before{background:var(--gold)}
.fl span{position:relative;writing-mode:vertical-rl;background:var(--parch);padding:10px 0;font-size:20px;font-weight:600;color:var(--ink);letter-spacing:.02em}.fu span{transform:rotate(180deg)}
.ph-row{display:flex;align-items:center;gap:20px}.ph-row h2{margin:0}.pz{flex:none;width:76px;height:76px;border-radius:50%;background:#F0CB72;color:#4A1220;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 8px rgba(240,203,114,.25)}
.pg{align-items:stretch}.pnl{background:rgba(255,255,255,.10);border:2px solid rgba(240,203,114,.55);border-radius:20px;padding:26px 28px;color:var(--parch)}.pnl b{display:block;font-size:19px;letter-spacing:.12em;text-transform:uppercase;color:#F0CB72;font-weight:600;margin-bottom:12px}.pnl ul{list-style:none;padding:0}.pnl li{font-size:26px;line-height:1.3;padding-left:28px;position:relative;margin-bottom:12px}.pnl li::before{content:'';position:absolute;left:0;top:10px;width:12px;height:12px;border-radius:50%;background:#F0CB72}.pnl h3{font-size:31px;font-weight:600;line-height:1.2;margin-bottom:14px}.ret{background:rgba(0,0,0,.22);border-radius:14px;padding:16px 20px;font-size:25px;line-height:1.3}.ret small{display:block;font-size:17px;letter-spacing:.12em;text-transform:uppercase;color:#F0CB72;font-weight:600;margin-bottom:4px}
.pill-t{position:absolute;top:50px;right:90px;z-index:3;border:2px solid var(--acc);border-radius:99px;padding:6px 18px;font-size:17px;font-weight:600;color:var(--acc);background:rgba(255,255,255,.7);white-space:nowrap}.dark .pill-t{border-color:#F0CB72;color:#F0CB72;background:rgba(0,0,0,.18)}
.cover h1.sm{font-size:68px}.qsub{font-size:24px;opacity:.85;max-width:1010px;line-height:1.35}.big3{margin-left:auto;font-weight:700;font-size:60px;line-height:1;color:var(--goldT);letter-spacing:-.02em}
.flow{display:flex;align-items:stretch;gap:6px;margin-top:10px}.fs{flex:1;position:relative;background:#fff;border-radius:20px;padding:36px 20px 24px;min-height:300px;box-shadow:0 6px 22px rgba(74,18,32,.12);border-top:6px solid var(--acc)}.fn{position:absolute;top:-18px;left:18px;width:38px;height:38px;border-radius:50%;background:var(--acc);color:#fff;font-weight:700;font-size:20px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 4px var(--parch)}
.fs h3{font-size:30px;color:var(--acc);font-weight:600;line-height:1.15;margin-bottom:10px}.fs p{font-size:25px;line-height:1.3}.fa{flex:none;width:34px;display:flex;align-items:center;justify-content:center;color:var(--acc)}.fa svg{width:30px;height:30px}
.bars{display:grid;gap:10px}.bl{font-size:28px;font-weight:600;margin-bottom:6px;color:var(--ink)}.bt{background:rgba(0,0,0,.07);border-radius:14px;height:64px;overflow:hidden}.bf{height:100%;border-radius:14px;display:flex;align-items:center;justify-content:flex-end;padding-right:20px;color:#fff;font-weight:700;font-size:34px;transform-origin:left}.bn{font-size:24px;color:var(--mut);margin-top:6px}
@keyframes growx{from{transform:scaleX(0)}to{transform:none}}.slide.on .bf{animation:growx 1s var(--ease) .4s both}
/* sobre */
.about{display:flex;gap:56px;align-items:center;height:100%}.about h2{margin:6px 0 4px;font-size:50px}.role{font-weight:500;font-size:28px;color:var(--goldT);margin-bottom:16px}
.facts{list-style:none;padding:0}.facts li{font-size:24px;line-height:1.35;padding-left:28px;position:relative;margin-bottom:10px}.facts li::before{content:'';position:absolute;left:0;top:11px;width:12px;height:12px;border-radius:50%;background:var(--gold)}
.btn{display:inline-block;margin-top:12px;background:var(--burg);color:#fff;padding:13px 30px;border-radius:99px;text-decoration:none;font-size:22px;font-weight:600;cursor:pointer;transition:background .2s}.btn:hover{background:var(--burgD)}
.nav{position:absolute;bottom:58px;width:48px;height:48px;border-radius:50%;border:2px solid rgba(107,30,46,.35);background:rgba(255,255,255,.85);color:var(--burg);cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .2s;z-index:6}#prev{right:150px}#next{right:90px}#stage:hover .nav,.nav:focus-visible{opacity:.95}.nav svg{width:24px;height:24px}
#bar{position:fixed;left:0;top:0;height:5px;background:var(--gold);width:0;z-index:5;transition:width .25s}#hint{position:fixed;bottom:8px;right:14px;color:#a89aa0;font-size:13px;z-index:5}.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
/* movimento */
@keyframes rise{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}@keyframes pop{from{opacity:0;transform:scale(.8)}to{opacity:1;transform:none}}@keyframes draw{from{transform:scaleX(0)}to{transform:scaleX(1)}}@keyframes pulse{0%,100%{box-shadow:0 0 0 8px rgba(199,154,59,.35)}50%{box-shadow:0 0 0 18px rgba(199,154,59,.12)}}
.rv{opacity:0}.slide.on .rv{animation:rise .65s var(--ease) both;animation-delay:calc(var(--d,0)*130ms + 180ms)}.slide.on .rv.pop{animation-name:pop}
.slide.on .tl-line{animation:draw 1.3s var(--ease) both;animation-delay:.1s}.slide.on .hubc,.slide.on .vsc:not(.sm){animation:pop .65s var(--ease) both,pulse 2.8s ease-in-out 1.2s 3}
.slide.on .hubl path{stroke-dasharray:1200;stroke-dashoffset:1200;animation:dash 1s var(--ease) .5s forwards}@keyframes dash{to{stroke-dashoffset:0}}
.slide.on .fl.rv{animation-name:rise}
@media (prefers-reduced-motion:reduce){.slide.on .bf{animation:none!important}.slide,.slide.on{transition:none!important;transform:none!important}#bar{transition:none}.rv{opacity:1!important}.slide.on .rv,.slide.on .tl-line,.slide.on .hubc,.slide.on .vsc,.slide.on .hubl path{animation:none!important}.slide.on .hubl path{stroke-dasharray:none;stroke-dashoffset:0}}
@media print{.bf{animation:none!important}@page{size:1280px 720px;margin:0}html,body{height:auto;overflow:visible;background:none;display:block}#stage{transform:none!important;width:1280px;height:auto!important;overflow:hidden;display:block}.slide{visibility:visible!important;opacity:1!important;transform:none!important;position:relative;height:720px;-webkit-print-color-adjust:exact;print-color-adjust:exact}.slide+.slide{page-break-before:always}.rv{opacity:1!important;animation:none!important}.hubl path{animation:none!important;stroke-dasharray:none!important;stroke-dashoffset:0!important}#bar,#hint,.nav,#live,.slide::after{display:none}}`;

// ------------------------------------------------------------ JS
const js=`const sl=[...document.querySelectorAll('.slide')],st=document.getElementById('stage'),bar=document.getElementById('bar'),live=document.getElementById('live');let i=-1;
const segsAll=sl.map(s=>[...s.querySelectorAll('.seg')]);
function show(n){n=Math.max(0,Math.min(sl.length-1,n));if(n===i)return;
 sl.forEach((s,k)=>{s.classList.toggle('on',k===n);s.classList.toggle('prev',k<n);s.setAttribute('aria-hidden',k===n?'false':'true');segsAll[k].forEach((b,j)=>b.classList.toggle('cur',j===n))});
 i=n;bar.style.width=((i+1)/sl.length*100)+'%';live.textContent='Slide '+(i+1)+' de '+sl.length+': '+sl[i].dataset.title;try{history.replaceState(null,'','#'+(i+1))}catch(e){}}
function fit(){const s=Math.min(innerWidth/1280,innerHeight/720);st.style.transform='scale('+s+')'}
addEventListener('resize',fit);fit();
addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('a'))return;if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();show(i+1)}else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();show(i-1)}else if(e.key==='Home')show(0);else if(e.key==='End')show(sl.length-1);else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}});
document.getElementById('prev').onclick=e=>{e.stopPropagation();show(i-1)};document.getElementById('next').onclick=e=>{e.stopPropagation();show(i+1)};
st.addEventListener('click',e=>{const g=e.target.closest('[data-go]');if(g){show(+g.dataset.go);return}if(e.target.closest('a,button'))return;const r=st.getBoundingClientRect();show(e.clientX-r.left<r.width/3?i-1:i+1)});
show((parseInt(location.hash.slice(1))||1)-1);`;
const arrow=d=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
const out=`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${D.title}</title><style>${css}</style></head><body><div id="bar"></div><main id="stage" role="region" aria-roledescription="apresentação" aria-label="${D.aria}">${S.map(slide).join('')}<button type="button" class="nav" id="prev" aria-label="Slide anterior">${arrow('M15 18l-6-6 6-6')}</button><button type="button" class="nav" id="next" aria-label="Próximo slide">${arrow('M9 6l6 6-6 6')}</button></main><div id="live" class="sr" aria-live="polite"></div><div id="hint">← → navegar · F tela cheia</div><script>${js}</script></body></html>`;
fs.writeFileSync(process.argv[2],out);console.log('ok',S.length,'slides',(out.length/1024).toFixed(0)+' KB');
