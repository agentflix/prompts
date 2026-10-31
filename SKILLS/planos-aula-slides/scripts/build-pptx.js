// PowerPoint editável a partir do mesmo conteúdo do HTML (lê S e IC de build.js)
const fs=require('fs'),path=require('path');const pptxgen=require('pptxgenjs');const sharp=require('sharp');
const src=fs.readFileSync(path.join(__dirname,'build-deck.js'),'utf8');
const D=require(path.resolve(process.argv[3]));const S=D.S;
const IC=new Function(src.match(/const IC=\{[\s\S]*?\};\nconst ico/)[0].replace(/\nconst ico$/,'')+';return IC;')();
const PROFILE=JSON.parse(fs.readFileSync(process.env.PROFILE_JSON||path.join(__dirname,'..','assets','profile.default.json'),'utf8'));
const PROF=PROFILE.short,DISC=D.DISC;
const C={burg:'6B1E2E',burgD:'4A1220',gold:'C79A3B',goldT:'8A5F0A',parch:'F7F1E5',ink:'241C2B',mut:'5A5063',white:'FFFFFF',line:'E4D8C3',goldL:'F0CB72'};
const ACC={0:'6B1E2E',4:'6B1E2E',5:'1F5F6B',6:'5B6A1F'};
const FONT='Lexend';
const K=13.333/1280;               // px do HTML -> polegadas
const I=px=>px*K, PT=px=>Math.round(px*0.75*10)/10;
const lines=(t,size,w,f=0.6)=>Math.max(1,Math.ceil(String(t).length*size*f/w));
const PHOTO=process.env.PHOTO||path.join(process.cwd(),'foto.jpg');
if(!fs.existsSync(PHOTO)){console.error('Foto nao encontrada: '+PHOTO);process.exit(1)}
const photoB=fs.readFileSync(PHOTO);

const iconCache={};
async function icon(name,color='FFFFFF'){const k=name+color;if(iconCache[k])return iconCache[k];
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="256" height="256" fill="none" stroke="#${color}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${IC[name]}</svg>`;
 const png=await sharp(Buffer.from(svg)).png().toBuffer();return iconCache[k]='data:image/png;base64,'+png.toString('base64');}

const p=new pptxgen();p.layout='LAYOUT_WIDE';p.title=D.title;p.author=PROFILE.name;
const ONLY=process.env.ONLY?+process.env.ONLY:0;

function T(sl,text,x,y,w,h,o={}){sl.addText(text,{x:I(x),y:I(y),w:I(w),h:I(h),fontFace:FONT,fontSize:PT(o.size||26),color:o.color||C.ink,bold:!!o.bold,italic:!!o.italic,align:o.align||'left',valign:o.valign||'top',margin:0,fit:'none',wrap:true,charSpacing:o.cs,lineSpacingMultiple:o.ls||1.12,paraSpaceAfter:0,hyperlink:o.link,vert:o.vert});}
function R(sl,x,y,w,h,o={}){sl.addShape(o.round?'roundRect':'rect',{x:I(x),y:I(y),w:I(w),h:I(h),rectRadius:o.round?I(o.round):undefined,fill:o.fill?{color:o.fill,transparency:o.tr||0}:{type:'none'},line:o.line?{color:o.line,width:o.lw||1}:{type:'none'},shadow:o.shadow?{type:'outer',color:'4A1220',opacity:.14,blur:8,offset:3,angle:90}:undefined});}
async function IB(sl,name,x,y,sz,bg,fg='FFFFFF',r=16){R(sl,x,y,sz,sz,{fill:bg,round:r});const s=sz*0.58;sl.addImage({data:await icon(name,fg),x:I(x+(sz-s)/2),y:I(y+(sz-s)/2),w:I(s),h:I(s)});}

let sNo=0;
const TOT={};S.forEach(x=>{TOT[x.au]=(TOT[x.au]||0)+x.min});const START=[];{const ac={};S.forEach((x,k)=>{START[k]=ac[x.au]||0;ac[x.au]=START[k]+x.min})}
async function build(s,i){
 const n=i+1;if(ONLY&&n!==ONLY)return;const sl=p.addSlide();const dark=(s.k==='cover'||s.k==='question'||s.k==='pause');const acc=ACC[s.a];
 sl.background={color:dark?C.burg:C.parch};
 R(sl,0,0,18,720,{fill:dark?C.gold:acc});
 // cabeçalho
 let y0=52;
 if(s.k!=='cover'&&s.k!=='about'){
   if(s.tag||s.k==="pause"){T(sl,(s.k==="pause"?"Ponto de parada · 50 min":s.tag).toUpperCase(),100,y0,800,28,{size:20,bold:true,color:dark?C.goldL:acc,cs:2});y0+=30;}
   const hs=n===2||s.k==='close'?54:48;const hl=lines(s.title,hs,1090,0.58);
   if(s.k==='pause'){sl.addShape('ellipse',{x:I(100),y:I(y0),w:I(76),h:I(76),fill:{color:C.goldL},line:{type:'none'}});sl.addImage({data:await icon('pause','4A1220'),x:I(100+16),y:I(y0+16),w:I(44),h:I(44)});T(sl,s.title,196,y0,994,76,{size:54,bold:true,color:C.parch,valign:'middle'});y0+=76+14;}
   else{T(sl,s.title,100,y0,1090,hl*hs*1.15,{size:hs,bold:true,color:dark?C.parch:C.burg});y0+=hl*hs*1.15+14;}
 }
 if(s.k!=='cover'){const txt=s.k==='pause'?`Planejado: ${TOT[s.au]} de 50 min`:`Aula ${s.au} de 3 · ${s.min} min · min ${START[i]}–${START[i]+s.min}`;const pw=Math.round(txt.length*10.4+40);R(sl,1190-pw,48,pw,36,{fill:dark?'000000':'FFFFFF',tr:dark?82:30,line:dark?C.goldL:acc,lw:1.5,round:18});T(sl,txt,1190-pw,48,pw,36,{size:17,bold:true,color:dark?C.goldL:acc,align:'center',valign:'middle'});}
 const top=y0,bot=632;
 const center=(h)=>top+Math.max(0,(bot-top-h)/2);
 // rodapé
 if(s.k!=='cover'){T(sl,`${PROF} · ${DISC}`,100,676,420,24,{size:19,color:dark?'E8D9CC':C.mut});T(sl,`${n} / ${S.length}`,1050,676,140,24,{size:19,color:dark?'E8D9CC':C.mut,align:'right'});
   const sw=20,gap=4,tot=S.length*sw+(S.length-1)*gap,x0=640-tot/2;S.forEach((q,k)=>R(sl,x0+k*(sw+gap),684,sw,k===i?10:6,{fill:k===i?(dark?C.goldL:ACC[q.a]):(dark?C.goldL:ACC[q.a]),tr:k===i?0:72,round:3}));}
 const keyBox=async(text,label,yy)=>{R(sl,100,yy,1090,76,{fill:'FFFFFF',tr:20,line:acc,lw:1.5,round:16});await IB(sl,'bulb',124,yy+12,52,acc,'FFFFFF',26);T(sl,label.toUpperCase(),196,yy+10,900,20,{size:17,bold:true,color:acc,cs:1.5});T(sl,text,196,yy+32,970,38,{size:26,color:C.ink});};
 const card=async(x,y,w,h,o)=>{R(sl,x,y,w,h,{fill:'FFFFFF',round:20,shadow:1,line:C.line,lw:.5});R(sl,x+16,y,w-32,6,{fill:o.acc||acc});};
 switch(s.k){
 case'cover':{
  const ts=s.title.length>16?64:80,tl=lines(s.title,ts,700,0.58),th=tl*ts*1.28,sl2=lines(s.sub,36,720,0.56)*44,mh=130;const tot=40+th+10+sl2+22+mh,y0=Math.max(80,(720-tot)/2);
  T(sl,s.who.toUpperCase(),100,y0,700,30,{size:21,color:C.goldL,cs:3});
  T(sl,s.title,100,y0+40,720,th,{size:ts,bold:true,color:C.parch});
  T(sl,s.sub,100,y0+40+th+10,720,sl2,{size:36,color:C.goldL});
  R(sl,100,y0+40+th+10+sl2+14,120,5,{fill:C.gold});
  T(sl,s.meta.join('\n'),100,y0+40+th+10+sl2+38,720,130,{size:25,color:'F4EADF',ls:1.35});
  sl.addImage({data:'data:image/jpeg;base64,'+photoB.toString('base64'),x:I(810),y:I(170),w:I(380),h:I(380),rounding:true});
  sl.addShape('ellipse',{x:I(810),y:I(170),w:I(380),h:I(380),fill:{type:'none'},line:{color:C.gold,width:6}});
  break;}
 case'timeline':{
  const ly=top+175,x0=180,wd=930,pos=v=>x0+(v-s.from)/(s.to-s.from)*wd;
  R(sl,x0,ly-4,wd/2,8,{fill:C.burg});R(sl,x0+wd/2,ly-4,wd/2,8,{fill:C.gold});
  s.pts.forEach((q,k)=>{const x=pos(+q[0]),up=k%2===0;const first=k===0,last=k===s.pts.length-1;
   const bx=first?x-40:last?x-215:x-140,bw=first?300:280,al=first?'left':last?'right':'center';const bh=124;
   const by=up?ly-36-bh:ly+36;
   T(sl,q[0],bx,by+(up?0:0),bw,60,{size:56,bold:true,color:C.burg,align:al});T(sl,q[1],bx,by+64,bw,64,{size:25,align:al});
   sl.addShape('ellipse',{x:I(x-14),y:I(ly-14),w:I(28),h:I(28),fill:{color:'FFFFFF'},line:{color:C.burg,width:5}});});
  R(sl,100,ly+215,5,34,{fill:C.gold});T(sl,s.sub,122,ly+217,1000,34,{size:25,color:C.mut});
  break;}
 case'agenda':{
  const w=(1090-44)/3,h=305,y=center(h+80);
  for(let j=0;j<3;j++){const x=100+j*(w+22),it=s.items[j],a=ACC[4+j];await card(x,y,w,h,{acc:a});await IB(sl,it[3],x+26,y+26,70,a);
   T(sl,it[0],x+26,y+112,120,32,{size:20,bold:true,color:'FFFFFF',align:'center'});R(sl,x+26,y+112,100,32,{fill:a,round:16});T(sl,it[0],x+26,y+118,100,26,{size:20,bold:true,color:'FFFFFF',align:'center'});
   T(sl,it[1],x+26,y+156,w-52,80,{size:31,bold:true,color:a});T(sl,it[2],x+26,y+h-62,w-52,56,{size:26});}
  R(sl,100,y+h+26,5,60,{fill:C.gold});T(sl,s.note,122,y+h+26,1060,60,{size:25,color:C.mut});
  break;}
 case'question':{
  const hs=s.qs.map(q=>20+lines(q,36,942,0.56)*47+20);const tot=hs.reduce((a,b)=>a+b,0)+(s.qs.length-1)*22+(s.sub?lines(s.sub,24,1010,0.55)*32+16:0);let y=center(tot);
  s.qs.forEach((q,k)=>{R(sl,100,y,1010,hs[k]+20,{fill:'FFFFFF',tr:88,line:C.goldL,lw:1.5,round:20});T(sl,q,134,y+20,942,hs[k],{size:36,color:C.parch,bold:false,valign:'middle'});y+=hs[k]+42;});
  if(s.sub){T(sl,s.sub,100,y-8,1010,lines(s.sub,24,1010,0.55)*32,{size:24,color:'E8D9CC'});}
  break;}
 case'cards':{
  const g2=s.cards.length>3;const n3=s.cards.length;
  if(!g2){const w=(1090-44)/3,pl=c=>lines(c[1],26,w-52,0.56);const th=Math.max(...s.cards.map(c=>lines(c[0],31,w-52-74,0.58)*36));const mh=Math.max(...s.cards.map(pl));
   const h=24+Math.max(58,th)+14+mh*36+24;const tot=h+22+76;let y=center(tot);
   for(let j=0;j<3;j++){const x=100+j*(w+22),c=s.cards[j];await card(x,y,w,h,{});await IB(sl,c[2],x+26,y+24,58,acc);T(sl,c[0],x+100,y+24,w-126,58,{size:31,bold:true,color:acc,valign:'middle'});T(sl,c[1],x+26,y+24+Math.max(58,th)+14,w-52,mh*36,{size:26});}
   await keyBox(s.key,'Ideia-chave',y+h+22);
  }else{const w=(1090-18)/2,h=Math.max(...s.cards.map(c=>16+54+8+lines(c[1],24,w-48,0.55)*31+16));const tot=2*h+18+18+76;let y=center(tot);
   for(let j=0;j<4;j++){const x=100+(j%2)*(w+18),yy=y+Math.floor(j/2)*(h+18),c=s.cards[j];await card(x,yy,w,h,{});await IB(sl,c[2],x+24,yy+16,54,acc);T(sl,c[0],x+92,yy+16,w-92-(c[3]?190:24),54,{size:31,bold:true,color:acc,valign:'middle'});if(c[3])T(sl,c[3],x+w-24-180,yy+16,180,54,{size:36,bold:true,color:C.goldT,align:'right',valign:'middle'});T(sl,c[1],x+24,yy+16+54+8,w-48,h-16-54-8-12,{size:24});}
   await keyBox(s.key,'Ideia-chave',y+2*h+18+18);}
  break;}
 case'swords':{
  const sw=425,h=250,tot=h+22+76;let y=center(tot);
  const side=async(x,o,alt)=>{R(sl,x,y,sw,h,{fill:'FFFFFF',round:22,shadow:1,line:C.line,lw:.5});R(sl,x+16,y,sw-32,6,{fill:alt?C.gold:acc});await IB(sl,o[3],x+sw/2-42,y+22,84,alt?C.gold:acc,alt?C.ink:'FFFFFF',22);
   T(sl,o[0].toUpperCase(),x,y+116,sw,24,{size:19,bold:true,color:C.mut,align:'center',cs:1.5});T(sl,o[1],x,y+142,sw,48,{size:36,bold:true,color:alt?C.ink:acc,align:'center'});T(sl,o[2],x,y+196,sw,36,{size:26,align:'center'});};
  await side(100,s.left,false);await side(100+sw+240,s.right,true);
  const mx=100+sw+120;sl.addShape('ellipse',{x:I(mx-50),y:I(y+h/2-80),w:I(100),h:I(100),fill:{color:C.gold,transparency:60},line:{type:'none'}});sl.addShape('ellipse',{x:I(mx-42),y:I(y+h/2-72),w:I(84),h:I(84),fill:{color:C.burg},line:{type:'none'}});sl.addImage({data:await icon('swords','FFFFFF'),x:I(mx-26),y:I(y+h/2-56),w:I(52),h:I(52)});
  T(sl,s.mid,mx-100,y+h/2+22,200,60,{size:21,bold:true,color:C.burg,align:'center'});
  await keyBox('O poder espiritual era superior ao dos reis.','Para a Igreja',y+h+22);
  break;}
 case'hub':{
  const w=(1090-44)/3,ch=Math.max(...s.nodes.map(c=>24+58+14+lines(c[1],26,w-52,0.56)*36+24));const tot=96+50+ch;let y=center(tot);
  const hw=420;R(sl,645-hw/2-8,y-8,hw+16,112,{fill:C.gold,tr:60,round:56});R(sl,645-hw/2,y,hw,96,{fill:C.burg,round:48});await IB(sl,'landmark',645-hw/2+10,y+10,76,'FFFFFF',C.burg,38);T(sl,s.hub,645-hw/2+100,y,hw-120,96,{size:36,bold:true,color:'FFFFFF',valign:'middle'});
  const cy=y+96,bar=cy+30,top2=y+96+50;const cx=[100+w/2,645,100+2*(w+22)+w/2];
  const ln=(x1,y1,x2,y2)=>sl.addShape('line',{x:I(Math.min(x1,x2)),y:I(Math.min(y1,y2)),w:I(Math.abs(x2-x1)),h:I(Math.abs(y2-y1)),line:{color:C.gold,width:3.5}});
  ln(645,cy,645,bar);ln(cx[0],bar,cx[2],bar);cx.forEach(x=>ln(x,bar,x,top2));
  for(let j=0;j<3;j++){const x=100+j*(w+22),c=s.nodes[j];await card(x,top2,w,ch,{});await IB(sl,c[2],x+26,top2+24,58,acc);T(sl,c[0],x+100,top2+24,w-126,58,{size:31,bold:true,color:acc,valign:'middle'});T(sl,c[1],x+26,top2+24+58+14,w-52,ch-24-58-14-14,{size:26});}
  break;}
 case'three':{
  const w=(1090-44)/3;const tl=Math.max(...s.cols.map(c=>lines(c[1],31,w-52,0.6))),bl=Math.max(...s.cols.map(c=>lines(c[2],26,w-52,0.56)));const h=168+tl*38+6+bl*34+26,tot=h+22+40;let y=center(tot);
  for(let j=0;j<3;j++){const x=100+j*(w+22),c=s.cols[j];await card(x,y,w,h,{});await IB(sl,c[3],x+26,y+26,84,acc,'FFFFFF',22);if(c[4])T(sl,c[4],x+w-26-170,y+30,170,76,{size:60,bold:true,color:C.goldT,align:'right',valign:'middle'});R(sl,x+26,y+124,Math.min(190,c[0].length*14+40),34,{fill:acc,round:17});T(sl,c[0],x+26,y+130,Math.min(190,c[0].length*14+40),28,{size:20,bold:true,color:'FFFFFF',align:'center'});
   T(sl,c[1],x+26,y+168,w-52,tl*38,{size:31,bold:true,color:acc});T(sl,c[2],x+26,y+168+tl*38+6,w-52,bl*34,{size:26});}
  R(sl,100,y+h+22,5,36,{fill:C.gold});T(sl,s.note,122,y+h+22,1060,36,{size:25,color:C.mut});
  break;}
 case'versus':{
  const sw=(1090-70-20*2)/2;const bl=o=>o[2].reduce((a,t)=>a+lines(t,25,sw-52-24,0.56)*32+6,0);const h=166+Math.max(bl(s.l),bl(s.r))+22,tot=h+20+88;let y=center(tot);
  const side=async(x,o,alt)=>{R(sl,x,y,sw,h,{fill:'FFFFFF',round:22,shadow:1,line:C.line,lw:.5});R(sl,x+16,y,sw-32,6,{fill:alt?C.gold:acc});await IB(sl,o[1],x+26,y+22,84,alt?C.gold:acc,alt?C.ink:'FFFFFF',22);T(sl,o[0],x+26,y+118,sw-52,44,{size:34,bold:true,color:alt?C.ink:acc});
   let yy=y+166;o[2].forEach(t=>{sl.addShape('ellipse',{x:I(x+26),y:I(yy+8),w:I(11),h:I(11),fill:{color:C.gold},line:{type:'none'}});const l=lines(t,25,sw-52-24,0.56);T(sl,t,x+50,yy,sw-76,l*32,{size:25});yy+=l*32+6;});};
  await side(100,s.l,false);await side(100+sw+20+70+20,s.r,true);
  const mx=100+sw+20+35;sl.addShape('ellipse',{x:I(mx-35),y:I(y+h/2-35),w:I(70),h:I(70),fill:{color:C.burg},line:{type:'none'}});T(sl,'×',mx-35,y+h/2-35,70,70,{size:40,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
  const pw=(1090-18)/2;s.foot.forEach((f,j)=>{const x=100+j*(pw+18),yy=y+h+20;R(sl,x,yy,pw,68,{fill:'FFFFFF',tr:20,line:acc,lw:1.5,round:16});T(sl,f[0].toUpperCase(),x+22,yy+8,pw-40,20,{size:17,bold:true,color:acc,cs:1.5});T(sl,f[1],x+22,yy+30,pw-40,34,{size:24});});
  break;}
 case'steps':{
  const w=(1090-24)/2,h=106,tot=2*h+24+44;let y=center(tot);
  for(let j=0;j<4;j++){const x=100+(j%2)*(w+24),yy=y+Math.floor(j/2)*(h+24);await card(x,yy,w,h,{});sl.addShape('ellipse',{x:I(x+26),y:I(yy+h/2-29),w:I(58),h:I(58),fill:{color:acc},line:{type:'none'}});T(sl,String(j+1),x+26,yy+h/2-29,58,58,{size:28,bold:true,color:'FFFFFF',align:'center',valign:'middle'});T(sl,s.steps[j],x+102,yy,w-126,h,{size:28,valign:'middle'});}
  R(sl,100,y+2*h+24+20,5,36,{fill:C.gold});T(sl,s.foot,122,y+2*h+24+20,1000,36,{size:25,color:C.mut});
  break;}
 case'reading':{
  const ql=lines(s.quote,32,1090-34*2-8,0.52),qh=28+ql*45+14+28+28,ah=22+lines(s.ask,29,1030,0.56)*38+22;const tot=qh+22+ah+22+36;let y=center(tot);
  R(sl,100,y,1090,qh,{fill:'FFFFFF',round:16,shadow:1,line:C.line,lw:.5});R(sl,100,y,8,qh,{fill:acc});
  T(sl,s.quote,142,y+28,1010,ql*45,{size:32});T(sl,s.cite,142,y+28+ql*45+10,1010,26,{size:20,color:C.mut});
  R(sl,100,y+qh+22,1090,ah,{fill:acc,round:16});T(sl,s.ask,130,y+qh+22,1030,ah,{size:29,color:'FFFFFF',valign:'middle',bold:false});
  R(sl,100,y+qh+22+ah+22,5,36,{fill:C.gold});T(sl,s.foot,122,y+qh+22+ah+22,1000,36,{size:25,color:C.mut});
  break;}
 case'pyramid':{
  const y=center(398),cols=['4A1220','6B1E2E','8F3A4B',C.gold];const L=[0.36,0.27,0.18,0.09,0],bw=520,th=92;
  s.tiers.forEach((t,j)=>{const ty=y+j*102;const pt=(fx,fy)=>({x:fx*I(bw),y:fy*I(th)});
   sl.addShape(p.ShapeType.custGeom,{x:I(100),y:I(ty),w:I(bw),h:I(th),fill:{color:cols[j]},line:{color:cols[j],width:.5},points:[{...pt(L[j],0),moveTo:true},pt(1-L[j],0),pt(1-L[j+1],1),pt(L[j+1],1),{close:true}]});
   T(sl,t,100,ty,bw,th,{size:30,bold:true,color:j===3?C.ink:'FFFFFF',align:'center',valign:'middle'});T(sl,s.notes[j],680,ty,330,th,{size:22,valign:'middle'});});
  // setas (rótulos na horizontal, acima das setas)
  const ax1=1050,ax2=1160;
  T(sl,s.down,ax1-52,y-6,104,48,{size:17,bold:true,color:acc,align:'center'});T(sl,s.up,ax2-52,y-6,104,48,{size:17,bold:true,color:C.goldT,align:'center'});
  sl.addShape('line',{x:I(ax1),y:I(y+52),w:0,h:I(336),line:{color:acc,width:4.5,endArrowType:'triangle'}});
  sl.addShape('line',{x:I(ax2),y:I(y+52),w:0,h:I(336),line:{color:C.gold,width:4.5,beginArrowType:'triangle'}});
  break;}
 case'flow':{
  const n=s.steps.length,gap=34,w=(1090-(n-1)*gap)/n;const dh=Math.max(...s.steps.map(c=>lines(c[1],25,w-40,0.56)*33)),th2=Math.max(...s.steps.map(c=>lines(c[0],30,w-40,0.58)*36));
  const h=Math.max(250,36+th2+10+dh+26),tot=h+(s.note?24+36:0);let y=center(tot);
  for(let j=0;j<n;j++){const x=100+j*(w+gap),c=s.steps[j];await card(x,y,w,h,{});
   sl.addShape('ellipse',{x:I(x+18),y:I(y-18),w:I(38),h:I(38),fill:{color:acc},line:{color:C.parch,width:3}});T(sl,String(j+1),x+18,y-18,38,38,{size:20,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
   T(sl,c[0],x+20,y+30,w-40,th2,{size:30,bold:true,color:acc});T(sl,c[1],x+20,y+30+th2+10,w-40,dh,{size:25});
   if(j<n-1){const ax=x+w+gap/2-12;sl.addShape(p.ShapeType.custGeom,{x:I(ax),y:I(y+h/2-14),w:I(24),h:I(28),fill:{color:acc},line:{type:'none'},points:[{x:0,y:0,moveTo:true},{x:I(24),y:I(14)},{x:0,y:I(28)},{close:true}]});}}
  if(s.note){R(sl,100,y+h+24,5,36,{fill:C.gold});T(sl,s.note,122,y+h+24,1060,36,{size:25,color:C.mut});}
  break;}
 case'bars':{
  const rh=34+6+64+6+lines(s.bars[0].txt,24,1090,0.55)*30+16,tot=s.bars.length*rh+(s.note?20+60:0);let y=center(tot);
  s.bars.forEach(b=>{T(sl,b.label,100,y,1090,36,{size:28,bold:true});R(sl,100,y+40,1090,64,{fill:'E6DFD3',round:14});R(sl,100,y+40,1090*b.pct/100,64,{fill:b.c.replace('#',''),round:14});T(sl,b.pct+'%',100,y+40,1090*b.pct/100-20,64,{size:34,bold:true,color:'FFFFFF',align:'right',valign:'middle'});T(sl,b.txt,100,y+110,1090,30,{size:24,color:C.mut});y+=rh;});
  if(s.note){R(sl,100,y+10,5,50,{fill:C.gold});T(sl,s.note,122,y+10,1060,50,{size:25,color:C.mut});}
  break;}
 case'pause':{
  const w=536,kh=s.kept.reduce((a,t)=>a+lines(t,26,w-56-28,0.56)*34+12,0);const h=Math.max(260,52+kh+24);const y=center(h);
  R(sl,100,y,w,h,{fill:'FFFFFF',tr:88,line:C.goldL,lw:1.5,round:20});T(sl,'O QUE FICOU',128,y+22,w-56,22,{size:19,bold:true,color:C.goldL,cs:1.5});
  let yy=y+58;s.kept.forEach(t=>{const l=lines(t,26,w-56-28,0.56);sl.addShape('ellipse',{x:I(128),y:I(yy+10),w:I(12),h:I(12),fill:{color:C.goldL},line:{type:'none'}});T(sl,t,156,yy,w-56-28,l*34,{size:26,color:C.parch});yy+=l*34+12;});
  const x2=100+w+18;R(sl,x2,y,w,h,{fill:'FFFFFF',tr:88,line:C.goldL,lw:1.5,round:20});T(sl,'NA PRÓXIMA AULA',x2+28,y+22,w-56,22,{size:19,bold:true,color:C.goldL,cs:1.5});
  T(sl,s.next,x2+28,y+54,w-56,lines(s.next,31,w-56,0.58)*38,{size:31,bold:true,color:C.parch});
  const nl=lines(s.next,31,w-56,0.58)*38,rl=lines(s.ask,25,w-56-40,0.56)*32;const by=y+54+nl+14;R(sl,x2+28,by,w-56,28+22+rl+16,{fill:'000000',tr:78,round:14});
  T(sl,'COMECE POR',x2+48,by+12,w-96,20,{size:17,bold:true,color:C.goldL,cs:1.5});T(sl,s.ask,x2+48,by+36,w-96,rl,{size:25,color:C.parch});
  break;}
 case'about':{
  sl.addImage({data:'data:image/jpeg;base64,'+photoB.toString('base64'),x:I(100),y:I(200),w:I(320),h:I(320),rounding:true});sl.addShape('ellipse',{x:I(100),y:I(200),w:I(320),h:I(320),fill:{type:'none'},line:{color:C.gold,width:6}});
  const x=476;T(sl,s.title.toUpperCase(),x,98,700,26,{size:21,bold:true,color:C.goldT,cs:2});T(sl,s.name,x,132,720,62,{size:50,bold:true,color:C.burg});T(sl,s.role,x,200,720,40,{size:28,color:C.goldT});
  let yy=258;s.facts.forEach(f=>{const l=lines(f,24,680,0.56);sl.addShape('ellipse',{x:I(x),y:I(yy+10),w:I(12),h:I(12),fill:{color:C.gold},line:{type:'none'}});T(sl,f,x+28,yy,690,l*32,{size:24});yy+=l*32+12;});
  R(sl,x,yy+10,300,52,{fill:C.burg,round:26});T(sl,'Currículo Lattes',x,yy+10,300,52,{size:22,bold:true,color:'FFFFFF',align:'center',valign:'middle',link:{url:s.lattes}});
  break;}
 case'close':{
  const hs=s.points.map(t=>26+lines(t,28,950,0.56)*36+26);const tot=hs.reduce((a,b)=>a+b,0)+2*18+22+36;let y=center(tot);
  s.points.forEach((t,j)=>{R(sl,100,y,1090,hs[j],{fill:'FFFFFF',round:20,shadow:1,line:C.line,lw:.5});R(sl,100,y,8,hs[j],{fill:C.burg});sl.addShape('ellipse',{x:I(130),y:I(y+hs[j]/2-29),w:I(58),h:I(58),fill:{color:C.burg},line:{type:'none'}});T(sl,String(j+1),130,y+hs[j]/2-29,58,58,{size:28,bold:true,color:'FFFFFF',align:'center',valign:'middle'});T(sl,t,212,y,950,hs[j],{size:28,valign:'middle'});y+=hs[j]+18;});
  R(sl,100,y+4,5,36,{fill:C.gold});T(sl,s.next,122,y+4,1000,36,{size:25,color:C.mut});
  break;}
 }
}
(async()=>{for(let i=0;i<S.length;i++)await build(S[i],i);await p.writeFile({fileName:process.argv[2]});console.log('ok',process.argv[2]);})();
