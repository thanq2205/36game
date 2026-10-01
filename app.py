import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chọc chó", page_icon="🐕", layout="wide")
st.markdown("<h3 style='text-align:center'>🐕 CHỌC CHÓ 🐕</h3>", unsafe_allow_html=True)

GAME_HTML = r"""
<style>
  html,body{margin:0;background:#8fd0ff;overflow:hidden;font-family:'Courier New',monospace}
  #wrap{position:relative;width:100%;height:660px;overflow:hidden}
  canvas{display:block;width:100%;height:100%;filter:saturate(1.4) contrast(1.12)}
  #hud{position:absolute;top:10px;left:12px;background:#e8c99a;color:#3d2712;font-weight:bold;padding:6px 12px;font-size:15px;
       border:4px solid #5b3a1e;box-shadow:0 4px 0 #2e1d0e}
  #msg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(60,35,15,.45)}
  #card{background:#e8c99a;border:6px solid #5b3a1e;box-shadow:0 0 0 4px #2e1d0e,10px 10px 0 rgba(0,0,0,.45);
        padding:22px 26px;width:310px;text-align:center;color:#3d2712}
  #card h1{font-size:22px;letter-spacing:1px;text-transform:uppercase;color:#7a2e0e;text-shadow:3px 3px 0 #f5deb3;margin:0 0 12px}
  .btn{display:block;width:100%;margin:14px 0;font-family:inherit;font-size:17px;font-weight:bold;padding:11px;border:4px solid #2e1d0e;
       background:#8d6e3f;color:#fff8e1;cursor:pointer;text-transform:uppercase;box-shadow:0 5px 0 #2e1d0e}
  .btn:hover{background:#a07f4a} .btn:active{transform:translateY(4px);box-shadow:0 1px 0 #2e1d0e}
  .btn.g{background:#5c8a34} .btn.g:hover{background:#6fa03f}
  #nm{width:85%;font-family:inherit;font-size:17px;font-weight:bold;padding:8px;border:4px solid #2e1d0e;background:#fff3d6;text-align:center;margin:6px 0}
  #guide{text-align:left;font-size:14px;line-height:1.75;font-weight:bold}
  #best{color:#7a2e0e;font-weight:bold;margin:6px 0} #res{font-size:16px;font-weight:bold;line-height:1.6}
  #msg.over{align-items:flex-end;background:transparent;padding-bottom:16px}
  #msg.over #card{width:600px;max-width:94%;padding:12px 18px}
  #msg.over #card h1{display:none} #msg.over #res{font-size:17px}
  #msg.over .btn{display:inline-block;width:auto;margin:8px 6px;padding:9px 16px;font-size:15px}
  #pad{position:absolute;bottom:10px;width:100%;display:flex;justify-content:center;gap:10px}
  #pad button{font-size:20px;padding:8px 18px;border:3px solid #2e1d0e;background:rgba(232,201,154,.85);font-family:inherit}
  #mute{position:absolute;top:10px;right:10px;border:3px solid #2e1d0e;padding:6px 10px;background:#e8c99a;font-size:16px}
  #blood{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .3s;background:radial-gradient(transparent 30%,rgba(190,0,0,.85))}
  #card h1{font-size:34px;margin-bottom:4px} #sub{font-size:14px;font-weight:bold;margin:0 0 12px;color:#5b3a1e}
  #msg.over #sub{display:none}
  #cap{position:absolute;left:50%;bottom:34px;transform:translateX(-50%);display:none;background:#e8c99a;border:4px solid #2e1d0e;color:#3d2712;
       font-weight:bold;font-size:20px;padding:8px 18px;box-shadow:0 5px 0 #2e1d0e;white-space:nowrap}
  #skip{position:absolute;right:12px;bottom:8px;display:none;color:#fff;font-size:13px;font-weight:bold;text-shadow:1px 1px 0 #000}
  #mn{display:none} #msg.over #mn{display:inline-block} #msg.over #bg, #msg.over #br2{display:none}
  #wrap{touch-action:none}
  #joy{position:absolute;left:18px;bottom:24px;width:130px;height:130px;border-radius:50%;background:rgba(232,201,154,.35);border:4px solid rgba(46,29,14,.7);display:none;touch-action:none}
  #knob{position:absolute;left:35px;top:35px;width:60px;height:60px;border-radius:50%;background:#8d6e3f;border:4px solid #2e1d0e}
</style>
<div id="wrap">
  <div id="hud"><span id="n">?</span> &nbsp;|&nbsp; <span id="s">0</span></div>
  <div id="blood"></div>
  <div id="joy"><div id="knob"></div></div>
  <div id="cap"></div><div id="skip">Space / chạm: bỏ qua</div>
  <button id="mute">🔊</button>
  <div id="msg"><div id="card">
    <div id="vMain"><h1>CHỌC CHÓ</h1><div id="sub">Chọc chó xong thì... chạy đi! 🐕💨</div><div id="res"></div><div id="best"></div>
      <button class="btn g" id="go">▶ Chơi</button>
      <button class="btn" id="bg">Hướng dẫn</button>
      <button class="btn" id="br2">Đổi tên</button>
      <button class="btn" id="mn">Về menu</button></div>
    <div id="vGuide" style="display:none"><h1>Hướng dẫn</h1><div id="guide">
      ← → : đổi làn<br>↑ / Space : nhảy<br>↓ / S : cúi, trượt<br>
      Xe tải, xe rơm, máy cày: nhảy lên nóc chạy<br>Trâu, đá, khúc gỗ, hàng rào, xe máy, mương: nhảy qua<br>Cổng tre, cành cây thấp: cúi xuống<br>Vịt, xe cút kít, gạch, chum: nhảy qua<br>Cây, tường rơm cao: không nhảy được, đổi làn<br>Space: bỏ qua đoạn mở đầu · M: tắt tiếng<br>
      <span style="color:#b71c1c">Đụng 1 lần là chó cắn!</span></div>
      <button class="btn" id="bk1">◀ Quay lại</button></div>
    <div id="vName" style="display:none"><h1>Nhập tên</h1>
      <input id="nm" maxlength="16" placeholder="Username"><button class="btn g" id="ok">Lưu</button></div>
  </div></div>
  <div id="pad"><button id="bl">◀</button><button id="bj">▲</button><button id="bd">▼</button><button id="brt">▶</button></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const $=id=>document.getElementById(id);
let NAME='', best=0;
try{NAME=localStorage.getItem('runner_name')||''}catch(e){}
let overMode=false;
function view(v){['vMain','vGuide','vName'].forEach(i=>$(i).style.display=(i===v?'block':'none')); $('msg').classList.toggle('over',overMode&&v==='vMain');}
function setName(n){NAME=n; $('n').textContent=n||'?'; best=0; try{localStorage.setItem('runner_name',n);best=+localStorage.getItem('best_'+n)||0}catch(e){}
  $('best').textContent='🏆 Điểm cao: '+best; $('res').innerHTML=n?'Chào <b>'+n+'</b>!':'';}
$('mn').onclick=()=>{reset(); alive=false; overMode=false; showoff=false; dying=0; $('res').innerHTML=NAME?'Chào <b>'+NAME+'</b>!':''; $('go').textContent='▶ Chơi'; view('vMain');};
$('bg').onclick=()=>view('vGuide'); $('bk1').onclick=()=>view('vMain');
$('br2').onclick=()=>{$('nm').value=NAME;view('vName');$('nm').focus();};
$('ok').onclick=()=>{const v=$('nm').value.trim(); if(!v){$('nm').focus();return;} setName(v); view('vMain');};
setName(NAME); if(!NAME)view('vName');
const wrap=$('wrap'), W=()=>wrap.clientWidth, H=()=>wrap.clientHeight;

/* ================= ÂM THANH ================= */
let AC=null, muted=false, musicT=null;
const ac=()=>{if(!AC)AC=new (window.AudioContext||window.webkitAudioContext)();return AC};
function nz(d,vol,f,q,att,type){
  if(muted||!AC)return;
  const n=Math.floor(AC.sampleRate*d), b=AC.createBuffer(1,n,AC.sampleRate), a=b.getChannelData(0);
  for(let i=0;i<n;i++)a[i]=Math.random()*2-1;
  const s=AC.createBufferSource(); s.buffer=b;
  const fl=AC.createBiquadFilter(); fl.type=type||'bandpass'; fl.frequency.value=f; fl.Q.value=q||1;
  const g=AC.createGain(), T=AC.currentTime;
  g.gain.setValueAtTime(.0001,T); g.gain.linearRampToValueAtTime(vol,T+(att||.02)); g.gain.exponentialRampToValueAtTime(.0001,T+d);
  s.connect(fl); fl.connect(g); g.connect(AC.destination); s.start();
}
function tn(f1,f2,d,type,vol,fc){
  if(muted||!AC)return;
  const o=AC.createOscillator(), fl=AC.createBiquadFilter(), g=AC.createGain(), T=AC.currentTime;
  o.type=type; o.frequency.setValueAtTime(f1,T); o.frequency.exponentialRampToValueAtTime(Math.max(f2,1),T+d);
  fl.type='bandpass'; fl.frequency.value=fc||2000; fl.Q.value=1.5;
  g.gain.setValueAtTime(vol,T); g.gain.exponentialRampToValueAtTime(.0001,T+d);
  o.connect(fl); fl.connect(g); g.connect(AC.destination); o.start(); o.stop(T+d);
}
function bark1(v){tn(380,200,.16,'sawtooth',.3*v,900); tn(760,400,.12,'square',.06*v,1800); nz(.1,.3*v,1400,1.5,.004); jaw=.6;}
const sfx={
  jump:()=>{nz(.16,.22,900,1,.02); tn(200,320,.12,'sine',.08,600)},
  land:()=>nz(.12,.45,300,.7,.004,'lowpass'),
  bark:()=>{bark1(1); setTimeout(()=>bark1(.9),210); setTimeout(()=>bark1(.8),420)},
  growl:()=>{ if(muted||!AC)return; const T=AC.currentTime,o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),
      g=AC.createGain(),f=AC.createBiquadFilter(); o.type='sawtooth'; o.frequency.value=78; l.frequency.value=26; lg.gain.value=.12;
      f.type='lowpass'; f.frequency.value=380; g.gain.setValueAtTime(.16,T); g.gain.linearRampToValueAtTime(.001,T+.9);
      l.connect(lg); lg.connect(g.gain); o.connect(f); f.connect(g); g.connect(AC.destination); o.start();l.start();o.stop(T+.9);l.stop(T+.9); },
  pant:()=>{[0,.13,.26,.39].forEach(t=>setTimeout(()=>nz(.1,.13,3200,2,.012),t*1000))},
  chomp:()=>{nz(.09,.32,650,2,.004); tn(190,90,.09,'square',.09,500); setTimeout(()=>{nz(.09,.28,700,2,.004);tn(170,80,.09,'square',.08,500)},130)},
  breath:()=>{nz(.34,.16,1700,.8,.2); setTimeout(()=>nz(.4,.19,1200,.7,.06),330)},
  step:()=>{nz(.06,.38+Math.random()*.12,260+Math.random()*200,.8,.004,'lowpass'); nz(.04,.12,2600,1,.002)},     // đất, sỏi
  stepTop:()=>{tn(170,110,.07,'triangle',.2,420); nz(.05,.15,900,1,.003)},                                       // nóc xe
  swoosh:()=>nz(.25,.2,1800,1,.08),
  horn:()=>{const h=d=>{tn(330,330,d,'sawtooth',.1,900);tn(415,415,d,'sawtooth',.09,1100)}; h(.4); setTimeout(()=>h(.3),520)},
  moo:()=>tn(140,95,1,'sawtooth',.16,320),
  creak:()=>tn(520,330,.5,'sawtooth',.05,800),
  engine:()=>{for(let i=0;i<8;i++)setTimeout(()=>tn(70,55,.08,'square',.13,220),i*95)},
  quack:()=>{[0,150,300].forEach(d=>setTimeout(()=>tn(650,430,.11,'square',.08,1200),d))},
  snore:()=>{nz(.9,.08,180,1,.4,'lowpass'); tn(75,60,.6,'sawtooth',.03,150)},
  poke:()=>{tn(320,180,.07,'triangle',.18,800); nz(.06,.2,1500,1,.003)},
  yelp:()=>tn(800,480,.3,'sawtooth',.12,1400),
  moto:()=>{tn(110,240,.5,'sawtooth',.08,600); setTimeout(()=>tn(240,120,.4,'sawtooth',.07,600),450)},
  crash:()=>{nz(.4,.6,700,.5,.01,'lowpass'); tn(140,35,.4,'sawtooth',.25,300)},
  splash:()=>nz(.6,.4,3500,.6,.05),
  scream:()=>{ if(muted||!AC)return; const T=AC.currentTime,o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),
      g=AC.createGain(),f=AC.createBiquadFilter(); o.type='sawtooth'; o.frequency.setValueAtTime(600,T); o.frequency.linearRampToValueAtTime(900,T+.3);
      l.frequency.value=8; lg.gain.value=50; f.type='bandpass'; f.frequency.value=1400; f.Q.value=.8;
      g.gain.setValueAtTime(.18,T); g.gain.exponentialRampToValueAtTime(.001,T+1);
      l.connect(lg); lg.connect(o.frequency); o.connect(f); f.connect(g); g.connect(AC.destination); o.start();l.start();o.stop(T+1);l.stop(T+1); },
  bite:()=>{nz(.2,.7,2200,1,.005); tn(220,60,.25,'square',.15,600); nz(.35,.4,600,1,.01,'lowpass')},
  over:()=>tn(400,80,1,'triangle',.2,1000)
};
/* âm thanh thiên nhiên: gió qua ruộng, ve sầu, chim hót, gà gáy, trâu rống */
function chirp(){ if(muted||!AC)return; const n=2+Math.floor(Math.random()*4), f0=2200+Math.random()*2200;
  for(let i=0;i<n;i++)setTimeout(()=>tn(f0*(1+Math.random()*.3),f0*(1.3+Math.random()*.5),.07,'sine',.03,f0),i*90); }
function rooster(){ [[520,760,.25,0],[700,900,.18,300],[900,650,.2,550],[780,420,.7,800]].forEach(a=>setTimeout(()=>tn(a[0],a[1],a[2],'sawtooth',.05,900),a[3])); }
let amb=[], ambT=null, ambWanted=false;
function ambience(on){
  amb.forEach(n=>{try{n.stop()}catch(e){}}); amb=[]; clearInterval(ambT);
  if(!on||muted||!AC)return;
  const b=AC.createBuffer(1,AC.sampleRate*4,AC.sampleRate), a=b.getChannelData(0); for(let i=0;i<a.length;i++)a[i]=Math.random()*2-1;
  const s=AC.createBufferSource(); s.buffer=b; s.loop=true;
  const f=AC.createBiquadFilter(); f.type='bandpass'; f.frequency.value=500; f.Q.value=.6;
  const g=AC.createGain(); g.gain.value=.05; const l=AC.createOscillator(), lg=AC.createGain(); l.frequency.value=.18; lg.gain.value=.03;
  l.connect(lg); lg.connect(g.gain); s.connect(f); f.connect(g); g.connect(AC.destination); s.start(); l.start(); amb.push(s,l);
  const c=AC.createOscillator(), cg=AC.createGain(), cl=AC.createOscillator(), clg=AC.createGain();
  c.type='sine'; c.frequency.value=4300; cg.gain.value=.004; cl.type='square'; cl.frequency.value=32; clg.gain.value=.004;
  cl.connect(clg); clg.connect(cg.gain); c.connect(cg); cg.connect(AC.destination); c.start(); cl.start(); amb.push(c,cl);
  ambT=setInterval(()=>{const r=Math.random(); if(r<.6)chirp(); else if(r<.66)rooster(); else if(r<.72)chirp();},2000);
}
$('mute').onclick=()=>{muted=!muted;$('mute').textContent=muted?'🔇':'🔊'; if(ambWanted)ambience(!muted);};

/* ================= CẢNH LÀNG QUÊ ================= */
function canvasTex(w,h,draw,rx,ry){
  const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h);
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; if(rx)t.repeat.set(rx,ry); return t;
}
const mcache={}, L=c=>mcache[c]||(mcache[c]=new THREE.MeshLambertMaterial({color:c,flatShading:true}));
const sky=canvasTex(2048,1024,(x,w,h)=>{
  const g=x.createLinearGradient(0,0,0,h);
  g.addColorStop(0,'#1a45c8'); g.addColorStop(.14,'#2f84ee'); g.addColorStop(.28,'#7cc8ff'); g.addColorStop(.38,'#ffe6bd'); g.addColorStop(.48,'#ffc98f'); g.addColorStop(1,'#ffb27a');
  x.fillStyle=g; x.fillRect(0,0,w,h);
  const sx=w*.72, sy=h*.2;
  let rg=x.createRadialGradient(sx,sy,0,sx,sy,w*.36);                       // quầng sáng mặt trời
  rg.addColorStop(0,'rgba(255,252,225,.95)'); rg.addColorStop(.1,'rgba(255,232,165,.6)'); rg.addColorStop(.4,'rgba(255,205,130,.2)'); rg.addColorStop(1,'rgba(255,205,130,0)');
  x.fillStyle=rg; x.fillRect(0,0,w,h);
  x.save(); x.translate(sx,sy);                                             // tia nắng
  for(let i=0;i<22;i++){const sp=w*(.006+Math.random()*.014); x.fillStyle='rgba(255,240,200,'+(.05+Math.random()*.06)+')';
    x.beginPath(); x.moveTo(0,0); x.lineTo(w*1.1,-sp); x.lineTo(w*1.1,sp); x.fill(); x.rotate(Math.PI*2/22+(Math.random()-.5)*.05);}
  x.restore();
  rg=x.createRadialGradient(sx,sy,0,sx,sy,h*.05); rg.addColorStop(0,'#fff'); rg.addColorStop(.7,'rgba(255,250,220,1)'); rg.addColorStop(1,'rgba(255,240,180,0)');
  x.fillStyle=rg; x.fillRect(sx-h*.06,sy-h*.06,h*.12,h*.12);
  const rb=['#ff5252','#ff9800','#ffeb3b','#66bb6a','#42a5f5','#5c6bc0','#ab47bc'];     // cầu vồng mờ
  rb.forEach((c,i)=>{x.strokeStyle=c; x.globalAlpha=.2; x.lineWidth=h*.012; x.beginPath(); x.arc(w*.27,h*.5,h*.34-i*h*.011,Math.PI*1.08,Math.PI*1.92); x.stroke();}); x.globalAlpha=1;
  const puff=(px,py,r,a)=>{                                                  // cụm mây: đáy hồng cam, đỉnh trắng
    let q=x.createRadialGradient(px,py+r*.4,0,px,py+r*.4,r); q.addColorStop(0,'rgba(255,165,125,'+a*.55+')'); q.addColorStop(1,'rgba(255,165,125,0)');
    x.fillStyle=q; x.fillRect(px-r,py-r*.6,r*2,r*2);
    q=x.createRadialGradient(px,py-r*.12,0,px,py-r*.12,r); q.addColorStop(0,'rgba(255,255,255,'+a+')'); q.addColorStop(.6,'rgba(255,250,244,'+a*.6+')'); q.addColorStop(1,'rgba(255,255,255,0)');
    x.fillStyle=q; x.fillRect(px-r,py-r,r*2,r*2);};
  for(let i=0;i<10;i++){const cx=Math.random()*w, cy=h*(.06+Math.random()*.26);                                  // mây xa nhỏ
    for(let k=0;k<12;k++)puff(cx+(k-6)*38+Math.random()*14, cy+Math.random()*16-8, 30+Math.random()*30, .8);}
  for(let i=0;i<7;i++){const cx=Math.random()*w, cy=h*(.16+Math.random()*.18);                                  // mây lớn gần
    for(let k=0;k<14;k++)puff(cx+(k-7)*60+Math.random()*24, cy+Math.random()*26-13-Math.sin(k/13*Math.PI)*34, 60+Math.random()*60, .92);}
  for(let i=0;i<12;i++){x.save(); x.translate(Math.random()*w,h*(.03+Math.random()*.2)); x.rotate(-.12+Math.random()*.1); x.scale(9,1);   // mây ti
    const q=x.createRadialGradient(0,0,0,0,0,26); q.addColorStop(0,'rgba(255,255,255,.3)'); q.addColorStop(1,'rgba(255,255,255,0)'); x.fillStyle=q; x.fillRect(-26,-26,52,52); x.restore();}
  const hz=x.createLinearGradient(0,h*.28,0,h*.5); hz.addColorStop(0,'rgba(255,230,190,0)'); hz.addColorStop(1,'rgba(255,225,185,.55)'); x.fillStyle=hz; x.fillRect(0,h*.28,w,h*.22);   // sương mờ chân trời
});
const scene=new THREE.Scene(); scene.background=sky; scene.fog=new THREE.Fog(0xdcebff,30,140);
const cam=new THREE.PerspectiveCamera(72,W()/H(),.1,220);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(W(),H()); wrap.prepend(renderer.domElement); renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
scene.add(new THREE.HemisphereLight(0xd6ebff,0x58a83a,.85));
const sunL=new THREE.DirectionalLight(0xffe2b0,1.3); sunL.position.set(8,14,4); scene.add(sunL); sunL.castShadow=true; sunL.shadow.mapSize.set(1024,1024);
const sc=sunL.shadow.camera; sc.left=-13; sc.right=13; sc.top=15; sc.bottom=-15; sc.near=1; sc.far=45;

// đường làng bằng đất
const roadTex=canvasTex(256,256,(x,w,h)=>{
  x.fillStyle='#b5753a'; x.fillRect(0,0,w,h);
  for(let i=0;i<6000;i++){const v=Math.random()<.5?'#a37a4c':'#c79b6a';x.fillStyle=v;x.fillRect(Math.random()*w,Math.random()*h,2+Math.random()*2,2);}
  for(let i=0;i<60;i++){x.fillStyle='#8d6a44';x.beginPath();x.arc(Math.random()*w,Math.random()*h,1+Math.random()*3,0,7);x.fill();}
  x.fillStyle='rgba(120,85,50,.35)'; for(const f of [.15,.22,.47,.53,.78,.85])x.fillRect(w*f-3,0,6,h);
  x.fillStyle='rgba(255,255,255,.35)'; x.fillRect(w*.375-2,0,4,h*.4); x.fillRect(w*.625-2,0,4,h*.4);
  x.fillStyle='#7cb342'; x.fillRect(0,0,9,h); x.fillRect(w-9,0,9,h);
},1,25);
const road=new THREE.Mesh(new THREE.PlaneGeometry(8,240),new THREE.MeshLambertMaterial({map:roadTex}));
road.rotation.x=-Math.PI/2; road.position.z=-110; scene.add(road);
// nền rừng: thảm cỏ xanh
const riceTex=canvasTex(128,128,(x,w,h)=>{
  x.fillStyle='#3f9e2a'; x.fillRect(0,0,w,h);
  for(let i=0;i<60;i++){x.fillStyle=Math.random()<.5?'#4cb534':'#2f8a20'; x.beginPath(); x.arc(Math.random()*w,Math.random()*h,6+Math.random()*14,0,7); x.fill();}
  for(let i=0;i<1400;i++){x.fillStyle=Math.random()<.5?'#7fd23a':'#2a7d1c'; x.fillRect(Math.random()*w,Math.random()*h,1,3+Math.random()*3);}
  for(let i=0;i<40;i++){x.fillStyle=['#ffeb3b','#ffffff','#f48fb1'][i%3]; x.fillRect(Math.random()*w,Math.random()*h,2,2);}
},36,30);
const field=new THREE.Mesh(new THREE.PlaneGeometry(300,240),new THREE.MeshLambertMaterial({map:riceTex}));
field.rotation.x=-Math.PI/2; field.position.set(0,-.05,-110); scene.add(field);
// núi xa + đồi xanh
const mts=new THREE.MeshLambertMaterial({color:0x8fb4d6,flatShading:true});
for(let i=0;i<9;i++){const m=new THREE.Mesh(new THREE.ConeGeometry(22+Math.random()*14,18+Math.random()*16,6),mts);
  m.position.set(-110+i*28,8,-128-Math.random()*10); scene.add(m);}
for(let i=0;i<10;i++){const m=new THREE.Mesh(new THREE.SphereGeometry(1,8,5),L(i%2?0x3f9a3a:0x4aa83f));
  m.scale.set(26+Math.random()*10,8+Math.random()*5,14); m.position.set(-125+i*28,0,-108-Math.random()*8); scene.add(m);}

const deco=[];
function addDeco(m,x,z){m.position.x=x; m.position.z=z; scene.add(m); deco.push(m);}
function cyl(rt,rb,h,c,x,y,z,seg){const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg||6),L(c));m.position.set(x,y,z);return m;}
function bx(w,h,d,c,x,y,z){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),L(c));m.position.set(x,y,z);return m;}
function palm(){const g=new THREE.Group(); const tr=cyl(.12,.22,4.6,0x8d6e63,0,2.3,0,6); tr.rotation.z=.1; g.add(tr);
  for(let i=0;i<7;i++){const l=new THREE.Mesh(new THREE.ConeGeometry(.28,2.6,4),L(0x2e7d32)); l.position.set(0,4.7,0);
    l.rotation.set(1.3,i*Math.PI*2/7,0); l.translateY(1.2); g.add(l);}
  for(let i=0;i<3;i++){const c=new THREE.Mesh(new THREE.SphereGeometry(.16,6,5),L(0x6d4c41));c.position.set(Math.cos(i*2)*.25,4.5,Math.sin(i*2)*.25);g.add(c);}return g;}
function house(){const g=new THREE.Group(); g.add(bx(3.2,2,3,0xfff1cf,0,1,0));
  const r=new THREE.Mesh(new THREE.ConeGeometry(2.8,1.6,4),L(Math.random()<.5?0xc0562d:0xd4b05a)); r.position.y=2.8; r.rotation.y=Math.PI/4; g.add(r);
  g.add(bx(.7,1.3,.1,0x6d4c41,0,.65,1.52)); g.add(bx(.6,.6,.1,0x81d4fa,-1,1.2,1.52)); g.add(bx(.6,.6,.1,0x81d4fa,1,1.2,1.52)); return g;}
function haystack(){const g=new THREE.Group(); g.add(cyl(.9,1,1.3,0xe0b84c,0,.65,0,8)); g.add(cyl(0,.9,1,0xd8a93c,0,1.8,0,8)); return g;}
function bamboo(){const g=new THREE.Group(); for(let i=0;i<5;i++){const h=4+Math.random()*3;
  const b=cyl(.07,.09,h,0x7cb342,(i-2)*.3,h/2,Math.random()*.4,6); b.rotation.z=(Math.random()-.5)*.15; g.add(b);
  const lf=new THREE.Mesh(new THREE.SphereGeometry(.5,5,4),L(0x9ccc65)); lf.position.set((i-2)*.3,h,0); lf.scale.y=.5; g.add(lf);} return g;}
function scarecrow(){const g=new THREE.Group(); g.add(cyl(.05,.05,2.2,0x8d6e63,0,1.1,0,5)); g.add(bx(1.4,.08,.08,0x8d6e63,0,1.7,0));
  g.add(bx(.5,.7,.25,0x1976d2,0,1.5,0)); const hd=new THREE.Mesh(new THREE.SphereGeometry(.22,6,5),L(0xffe0b2)); hd.position.set(0,2.05,0); g.add(hd);
  const h=new THREE.Mesh(new THREE.ConeGeometry(.5,.35,8),L(0xf5d76e)); h.position.y=2.3; g.add(h); return g;}
function tree(){const g=new THREE.Group(); g.add(cyl(.15,.24,1.8,0x6d4c41,0,.9,0,6)); const c=[0x388e3c,0x43a047,0x2e7d32];
  for(let i=0;i<3;i++){const b=new THREE.Mesh(new THREE.IcosahedronGeometry(1.1-i*.2,0),L(c[i]));b.position.set((i-1)*.3,2.3+i*.6,(i%2)*.3);g.add(b);} return g;}
function bush(){const g=new THREE.Group(); for(let i=0;i<3;i++){const b=new THREE.Mesh(new THREE.IcosahedronGeometry(.4+Math.random()*.25,0),L(i?0x558b2f:0x33691e));b.position.set((i-1)*.45,.35,Math.random()*.3);g.add(b);} return g;}
function banana(){const g=new THREE.Group(); g.add(cyl(.12,.16,2.2,0x9ccc65,0,1.1,0,6));
  const lm=new THREE.MeshLambertMaterial({color:0x66bb6a,side:THREE.DoubleSide,flatShading:true});
  for(let i=0;i<6;i++){const l=new THREE.Mesh(new THREE.PlaneGeometry(.5,2),lm); l.position.y=2.3; l.rotation.set(1.1,i*1.05,0); l.translateY(.9); g.add(l);} return g;}
function grass(){const g=new THREE.Group(); for(let i=0;i<7;i++){const c=new THREE.Mesh(new THREE.ConeGeometry(.06,.5+Math.random()*.4,4),L(i%2?0x7cb342:0x558b2f));
  c.position.set((Math.random()-.5)*.5,.3,(Math.random()-.5)*.5); c.rotation.set((Math.random()-.5)*.5,0,(Math.random()-.5)*.5); g.add(c);} return g;}
function flowers(){const g=bush(); const cs=[0xffeb3b,0xf48fb1,0xffffff,0xff7043];
  for(let i=0;i<8;i++){const f=new THREE.Mesh(new THREE.SphereGeometry(.07,4,3),L(cs[i%4]));f.position.set((Math.random()-.5)*1.2,.55+Math.random()*.2,(Math.random()-.5)*.5);g.add(f);} return g;}
function buffaloMesh(){const g=new THREE.Group();
  g.add(bx(1,.85,1.7,0x455a64,0,1.05,0)); g.add(bx(.9,.5,.4,0x37474f,0,1.1,-.9));
  for(const [x,z] of [[-.3,-.6],[.3,-.6],[-.3,.6],[.3,.6]])g.add(cyl(.11,.13,.75,0x37474f,x,.38,z,6));
  g.add(bx(.5,.5,.55,0x455a64,0,1.15,-1.2)); g.add(bx(.4,.25,.25,0x90a4ae,0,1.02,-1.5));
  for(const x of [-.4,.4]){const h=bx(.5,.08,.08,0xf5f5dc,x,1.5,-1.15);h.rotation.z=x>0?.5:-.5;g.add(h);g.add(bx(.08,.08,.08,0x111111,x*.4,1.28,-1.45));}
  g.add(bx(.08,.6,.08,0x37474f,0,1.0,.95)); return g;}
const farmers=[];
const GI=new THREE.IcosahedronGeometry(1,0), GC=new THREE.ConeGeometry(1,1,7), GT=new THREE.CylinderGeometry(1,1,1,6);
const pk=a=>a[Math.floor(Math.random()*a.length)];
const GREENS=[0x2e7d32,0x388e3c,0x43a047,0x558b2f,0x2f8f3a,0x1b7a2e,0x66bb6a,0x4caf50];
function blob(c,r,x,y,z){const m=new THREE.Mesh(GI,L(c)); m.scale.set(r,r*.9,r); m.position.set(x,y,z); m.rotation.y=Math.random()*6; return m;}
function trunk(c,r,h){const m=new THREE.Mesh(GT,L(c)); m.scale.set(r,h,r); m.position.y=h/2; return m;}
function oak(s,cols){s=s||1; cols=cols||GREENS; const g=new THREE.Group(), h=1.8*s; g.add(trunk(0x6d4c41,.22*s,h));
  g.add(blob(pk(cols),1.5*s,0,h+.9*s,0)); g.add(blob(pk(cols),1.1*s,.8*s,h+.5*s,.2*s)); g.add(blob(pk(cols),1.1*s,-.8*s,h+.6*s,-.2*s)); g.add(blob(pk(cols),.9*s,0,h+2*s,0)); return g;}
function pine(s){s=s||1; const g=new THREE.Group(), h=1.2*s, c=pk([0x1b5e20,0x2e7d32,0x256d2a]); g.add(trunk(0x5d4037,.18*s,h));
  for(let i=0;i<4;i++){const m=new THREE.Mesh(GC,L(c)); const r=(1.5-i*.3)*s; m.scale.set(r,1.5*s,r); m.position.y=h+.5*s+i*.95*s; g.add(m);} return g;}
function birch(s){s=s||1; const g=new THREE.Group(), h=3*s; g.add(trunk(0xeeeeee,.13*s,h)); const c=[0x7cb342,0x9ccc65,0x8bc34a];
  g.add(blob(pk(c),1.1*s,0,h+.5*s,0)); g.add(blob(pk(c),.8*s,.5*s,h,.2*s)); g.add(blob(pk(c),.8*s,-.5*s,h+.2*s,-.2*s)); return g;}
function blossom(s){return oak(s,[0xf8bbd0,0xf48fb1,0xfce4ec]);}
const near=[bush,bush,flowers,grass,grass,()=>oak(.6)];
const mid=[()=>oak(1),()=>oak(1.1),()=>pine(1),()=>birch(1),palm,banana,()=>blossom(1),()=>oak(1.2),()=>pine(1.2)];
const far=[()=>oak(1.7),()=>pine(1.8),()=>pine(1.5),()=>oak(1.5),bamboo,()=>birch(1.6),()=>oak(2)];
for(const sx of [-1,1]){
  for(let i=0;i<30;i++)addDeco(pk(near)(), sx*(5.1+Math.random()*2.2), -i*4-Math.random()*3);
  for(let i=0;i<32;i++)addDeco(pk(mid)(), sx*(7.6+Math.random()*6), -i*3.8-Math.random()*3);
  for(let i=0;i<36;i++)addDeco(pk(far)(), sx*(14+Math.random()*18), -i*3.4-Math.random()*3);
  for(let i=0;i<4;i++){const h=house(); h.rotation.y=sx>0?-Math.PI/2:Math.PI/2; addDeco(h,sx*(10+Math.random()*3),-i*30-(sx>0?14:0)-8);}
}
// cỏ + hoa 3D (instanced)
const tuftN=700, tuft=new THREE.InstancedMesh(new THREE.ConeGeometry(.1,.55,4),L(0x62c033),tuftN), tp=[], d0=new THREE.Object3D();
for(let i=0;i<tuftN;i++)tp.push({x:(Math.random()<.5?-1:1)*(4.7+Math.random()*16),z:-Math.random()*120,s:.7+Math.random()*.9});
tuft.frustumCulled=false; scene.add(tuft);
const flN=450, fl=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.09,0),new THREE.MeshLambertMaterial({flatShading:true}),flN), fp=[];
const FC=[0xffeb3b,0xf48fb1,0xffffff,0xff7043,0xce93d8].map(c=>new THREE.Color(c));
for(let i=0;i<flN;i++){fp.push({x:(Math.random()<.5?-1:1)*(4.7+Math.random()*10),z:-Math.random()*120}); fl.setColorAt(i,pk(FC));}
fl.instanceColor.needsUpdate=true; fl.frustumCulled=false; scene.add(fl);
function updTufts(mv){
  tp.forEach((q,i)=>{q.z+=mv*2; if(q.z>8)q.z-=120; d0.position.set(q.x,.25*q.s,q.z); d0.scale.set(q.s,q.s,q.s); d0.updateMatrix(); tuft.setMatrixAt(i,d0.matrix);}); tuft.instanceMatrix.needsUpdate=true;
  fp.forEach((q,i)=>{q.z+=mv*2; if(q.z>8)q.z-=120; d0.position.set(q.x,.15,q.z); d0.scale.set(1,1,1); d0.updateMatrix(); fl.setMatrixAt(i,d0.matrix);}); fl.instanceMatrix.needsUpdate=true;
}
// chim bay
const birds=[];
for(let i=0;i<8;i++){const g=new THREE.Group(), m=0x37474f; g.add(bx(.4,.12,.15,m,0,0,0)); g.add(bx(.1,.08,.08,0xffa000,.25,0,0));
  const wl=new THREE.Group(), wr=new THREE.Group(); wl.add(bx(.5,.03,.25,m,-.25,0,0)); wr.add(bx(.5,.03,.25,m,.25,0,0)); g.add(wl); g.add(wr);
  g.userData={wl,wr,ph:Math.random()*6,sp:.04+Math.random()*.05,dir:Math.random()<.5?-1:1}; g.scale.set(1.6*g.userData.dir,1.6,1.6);
  g.position.set(-45+Math.random()*90,7+Math.random()*9,-25-Math.random()*70); scene.add(g); birds.push(g);}
const clouds=[];
for(let i=0;i<7;i++){const g=new THREE.Group(),m=new THREE.MeshBasicMaterial({color:0xffffff,fog:false});
  for(let k=0;k<5;k++){const s=new THREE.Mesh(new THREE.SphereGeometry(3+Math.random()*2,8,6),m);s.position.set(k*3.5-7,Math.random()*1.5,Math.random()*2);s.scale.y=.6;g.add(s);}
  g.position.set(-60+Math.random()*120,22+Math.random()*10,-80-Math.random()*30); scene.add(g); clouds.push(g);}
function shadow(){return new THREE.Group();}

/* ================= NHÂN VẬT: cậu nhóc da đen, chỉ mặc quần, tóc mái chéo ================= */
const skin=L(0x2e1c10), player=new THREE.Group(), lim={};
function limbP(px,py,parts){const p=new THREE.Group(); p.position.set(px,py,0);
  parts.forEach(a=>{const m=new THREE.Mesh(a[0],a[1]); m.position.set(0,a[2],a[3]||0); p.add(m);}); player.add(p); return p;}
const BG=(w,h,d)=>new THREE.BoxGeometry(w,h,d);
player.add(bx(.78,.74,.5,0x2e1c10,0,1.12,0));                        // thân trần
player.add(bx(.06,.6,.02,0x24150b,0,1.12,.26));                      // đường sống lưng
player.add(bx(.8,.3,.52,0x1565c0,0,.78,0)); player.add(bx(.82,.06,.54,0x0d47a1,0,.94,0));   // quần đùi + cạp
const head=new THREE.Mesh(new THREE.SphereGeometry(.4,8,6),skin); head.position.y=1.85; player.add(head);
for(const x of [-.4,.4]){const e=new THREE.Mesh(new THREE.SphereGeometry(.1,5,4),skin);e.position.set(x,1.83,0);player.add(e);}
const ns=new THREE.Mesh(new THREE.ConeGeometry(.08,.14,4),skin); ns.rotation.x=-1.5; ns.position.set(0,1.8,-.4); player.add(ns);
for(const x of [-.14,.14]){player.add(bx(.11,.08,.04,0xffffff,x,1.9,-.37)); player.add(bx(.05,.06,.045,0,x,1.9,-.38));}
player.add(bx(.26,.05,.04,0xffffff,0,1.68,-.38));
const hairM=L(0x0a0a0a);                                              // tóc đen, mái xéo
const cap=new THREE.Mesh(new THREE.SphereGeometry(.44,8,6,0,Math.PI*2,0,Math.PI*.5),hairM); cap.position.set(0,1.87,.03); cap.rotation.x=.55; player.add(cap);
const fr=bx(.62,.14,.2,0x0a0a0a,.06,2.13,-.3); fr.rotation.z=-.38; player.add(fr);
const fr2=bx(.36,.12,.16,0x0a0a0a,.2,2.0,-.36); fr2.rotation.z=-.65; player.add(fr2);
player.add(bx(.7,.3,.12,0x0a0a0a,0,1.98,.36));
function armP(x){return limbP(x,1.42,[[BG(.22,.42,.22),skin,-.21],[BG(.2,.38,.2),skin,-.58],[new THREE.IcosahedronGeometry(.12,0),skin,-.8]]);}
function legP(x){return limbP(x,.78,[[BG(.4,.44,.4),L(0x1565c0),-.22],[BG(.22,.3,.22),skin,-.58],[BG(.26,.08,.4),skin,-.75,-.05]]);}   // chân đất
lim.armL=armP(-.55); lim.armR=armP(.55); lim.legL=legP(-.2); lim.legR=legP(.2);
scene.add(player);

/* ================= CHÓ LOW-POLY ================= */
const dog=new THREE.Group(), dm=L(0xa8672d), dk=L(0x5a3a1a), dl=[];
dog.add(bx(.62,.6,1.0,0xa8672d,0,.75,.05)); dog.add(bx(.66,.66,.5,0xa8672d,0,.78,-.4)); // thân + ngực
dog.add(bx(.5,.3,.3,0xf3e0bd,0,.55,-.45));                                            // ngực trắng
dog.add(bx(.3,.35,.35,0xa8672d,0,1.0,-.75));                                          // cổ
const dhead=new THREE.Group(); dhead.position.set(0,1.1,-.95); dog.add(dhead);
dhead.add(bx(.44,.4,.45,0xa8672d,0,0,0));
dhead.add(bx(.26,.17,.34,0x5a3a1a,0,-.06,-.36));                                      // mõm trên
dhead.add(bx(.08,.07,.06,0x000000,0,.02,-.55));                                       // mũi
for(const x of [-.19,.19]){const e=new THREE.Mesh(new THREE.BoxGeometry(.1,.3,.16),dk);e.position.set(x,.15,.1);e.rotation.z=x>0?-.35:.35;dhead.add(e);
  dhead.add(bx(.07,.07,.03,0xff1744,x*.6,.08,-.23));}
const jawG=new THREE.Group(); jawG.position.set(0,-.13,-.12); dhead.add(jawG);
jawG.add(bx(.22,.08,.32,0x5a3a1a,0,-.03,-.2)); jawG.add(bx(.12,.04,.2,0xff8a80,0,0,-.2));   // hàm dưới + lưỡi
for(const x of [-.08,.08])jawG.add(bx(.03,.05,.03,0xffffff,x,.03,-.34));
for(const x of [-.08,.08])dhead.add(bx(.03,.05,.03,0xffffff,x,-.15,-.5));                    // răng nanh
dog.add(bx(.36,.1,.36,0xd32f2f,0,.98,-.7));                                            // vòng cổ
const tag=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,.02,6),L(0xffd600)); tag.rotation.x=1.57; tag.position.set(0,.85,-.9); dog.add(tag);
const tail=new THREE.Mesh(new THREE.BoxGeometry(.11,.11,.55),dm); tail.position.set(0,1.0,.7); tail.rotation.x=.7; dog.add(tail);
for(const [x,z] of [[-.2,-.5],[.2,-.5],[-.2,.5],[.2,.5]]){
  const p=new THREE.Group();p.position.set(x,.55,z);const l=new THREE.Mesh(new THREE.BoxGeometry(.14,.5,.14),dm);l.position.y=-.25;p.add(l);
  p.add(bx(.17,.08,.22,0xf3e0bd,0,-.5,-.03)); dog.add(p);dl.push(p);}
function boneMesh(){const g=new THREE.Group(),m=L(0xfff8e1);
  const c=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.6,8),m); c.rotation.z=Math.PI/2; g.add(c);
  for(const x of [-.32,.32])for(const z of [-.07,.07]){const s=new THREE.Mesh(new THREE.SphereGeometry(.12,6,5),m);s.position.set(x,0,z);g.add(s);} return g;}
const mouthBone=boneMesh(); mouthBone.position.set(0,-.12,-.5); mouthBone.rotation.y=Math.PI/2; mouthBone.visible=false; dhead.add(mouthBone);
dog.add(shadow()); scene.add(dog);

/* máu (hạt low-poly kiểu hoạt hình) + xương bay */
const drops=[]; for(let i=0;i<50;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(.09,.09,.09),new THREE.MeshBasicMaterial({color:i%3?0xc62828:0x8e0000}));
  m.visible=false; scene.add(m); drops.push({m,vx:0,vy:0,vz:0});}
const pool=new THREE.Mesh(new THREE.CircleGeometry(1,14),new THREE.MeshBasicMaterial({color:0x9b0000})); pool.rotation.x=-Math.PI/2; pool.position.y=.05; pool.visible=false; scene.add(pool);
const boneFly=boneMesh(); boneFly.visible=false; boneFly.scale.set(1.3,1.3,1.3); scene.add(boneFly);
let bfv=0;

/* ================= LOGIC ================= */
const LANES=[-2,0,2], SPD0=.16, SPDMAX=.40, DY=110;
let lane=1,y=0,vy=0,floorY=0,speed=SPD0,score=0,alive=false,items=[],timer=0,gap=4,shake=0,t=0,jaw=0,
    duckT=0,dying=0,dyk=0,stepS=0,breathT=0,pantT=0,barkT=200,growlT=150,poolS=0,wasAir=false,showoff=false,chewT=0,
    cx=0,cy=3.6,cz=6.5,lx=0,ly=1.2,lz=-6;
function cast(g){g.traverse(o=>{if(o.isMesh)o.castShadow=true;});}
road.receiveShadow=true; field.receiveShadow=true; cast(player); cast(dog);
mouthBone.scale.set(1.5,1.5,1.5);
/* đống xương người (hoạt hình) */
const pile=new THREE.Group(); pile.visible=false; scene.add(pile);
{const bm=0xf3ecd6; const sk=new THREE.Mesh(new THREE.SphereGeometry(.22,7,6),L(bm)); sk.position.set(.15,.22,0); pile.add(sk);
 pile.add(bx(.22,.1,.2,bm,.15,.08,-.1)); pile.add(bx(.06,.07,.03,0x111111,.08,.25,-.2)); pile.add(bx(.06,.07,.03,0x111111,.22,.25,-.2));
 for(let i=0;i<5;i++){const r=new THREE.Mesh(new THREE.TorusGeometry(.3-i*.02,.028,4,8,Math.PI),L(bm)); r.rotation.y=Math.PI/2; r.position.set(-.75+i*.13,.03,.1); pile.add(r);}
 const sp=cyl(.03,.03,.7,bm,-.45,.03,.1,5); sp.rotation.z=Math.PI/2; pile.add(sp);
 for(const [a,z] of [[.5,.55],[-.4,-.5]]){const b=boneMesh(); b.scale.set(1.3,1.3,1.3); b.rotation.y=a; b.position.set(0,.1,z); pile.add(b);}}
function wheel(r,x,y,z,w){const m=cyl(r,r,w||.2,0x212121,x,y,z,10);m.rotation.z=Math.PI/2;return m;}
const HT={fence:.7,buffalo:1.7,pit:.35,log:.65,rock:.95,moto:1.3,ducks:.5,cart:1.2,bricks:1.0,jars:1.0};
function mk(type,l){
  const g=new THREE.Group(); let hz=.6, top=0, solid=false;
  if(type==='fence'){for(const x of [-.8,0,.8])g.add(bx(.12,.9,.12,0x8d6e63,x,.45,0)); g.add(bx(1.8,.12,.08,0xa1785c,0,.35,0)); g.add(bx(1.8,.12,.08,0xa1785c,0,.68,0)); hz=.3;}
  else if(type==='buffalo'){g.add(buffaloMesh()); hz=1.1;}
  else if(type==='log'){const c=cyl(.3,.3,2,0x6d4c41,0,.32,0,8); c.rotation.z=Math.PI/2; g.add(c);
    for(const x of [-1.01,1.01]){const e=cyl(.27,.27,.03,0xd7b98a,x,.32,0,8); e.rotation.z=Math.PI/2; g.add(e);} hz=.35;}
  else if(type==='rock'){[[0,.45,0,.6],[.55,.3,.2,.4],[-.55,.28,-.1,.38]].forEach((a,i)=>{const r=new THREE.Mesh(new THREE.IcosahedronGeometry(a[3],0),L(i?0x8d949b:0x78808a));r.position.set(a[0],a[1],a[2]);g.add(r);}); hz=.7;}
  else if(type==='moto'){g.add(wheel(.36,0,.36,-.7,.14)); g.add(wheel(.36,0,.36,.7,.14)); g.add(bx(.3,.35,1.2,0xd32f2f,0,.75,0)); g.add(bx(.32,.12,.6,0x212121,0,1.0,.3));
    g.add(bx(.7,.06,.06,0x424242,0,1.25,-.55)); g.add(bx(.2,.2,.15,0xfff59d,0,1.0,-.7)); g.add(bx(.06,.6,.06,0x9e9e9e,0,.85,-.6)); hz=.95;}
  else if(type==='tractor'){g.add(bx(1.4,.8,2.2,0x2e7d32,0,1.2,0)); g.add(bx(1,.4,.9,0x388e3c,0,1.7,-.7)); g.add(bx(.5,.15,.4,0x212121,0,1.7,.55));
    g.add(wheel(.7,-.95,.7,.6,.35)); g.add(wheel(.7,.95,.7,.6,.35)); g.add(wheel(.4,-.8,.4,-.8,.25)); g.add(wheel(.4,.8,.4,-.8,.25));
    g.add(cyl(.05,.05,1,0x212121,.4,2.2,-.9,5)); g.add(bx(.3,.15,.06,0xfff59d,-.3,1.3,-1.12)); g.add(bx(.3,.15,.06,0xfff59d,.3,1.3,-1.12)); hz=1.5; top=1.7;}
  else if(type==='truck'){g.add(bx(1.7,.3,3.6,0x455a64,0,.6,0)); g.add(bx(1.7,1.2,2.3,0x8d6e63,0,1.3,.6));
    for(let i=0;i<4;i++)g.add(bx(.7,.4,.6,0xf5f0dc,i%2?.42:-.42,2.1,i<2?.1:1.1));
    g.add(bx(1.6,1.3,1.1,0x2e7d32,0,1.25,-1.4)); g.add(bx(1.4,.5,.06,0x81d4fa,0,1.6,-1.96));
    g.add(bx(.3,.15,.06,0xfff59d,-.5,.85,-1.82)); g.add(bx(.3,.15,.06,0xfff59d,.5,.85,-1.82));
    for(const z of [-1.4,.4,1.4])for(const x of [-.85,.85])g.add(wheel(.36,x,.36,z)); g.add(bx(1.72,.12,2.3,0xd32f2f,0,.85,.6)); hz=2.0; top=1.9;}
  else if(type==='haycart'){g.add(bx(1.6,.25,2.4,0x8d6e63,0,.6,0)); g.add(bx(1.5,1.2,2.2,0xe6c35c,0,1.3,0)); g.add(bx(1.3,.35,1.8,0xd9b04a,0,2.05,0));
    g.add(wheel(.45,-.85,.45,.3)); g.add(wheel(.45,.85,.45,.3)); g.add(bx(.1,.1,1.5,0x6d4c41,0,.55,-1.7)); hz=1.3; top=1.9;}
  else if(type==='pit'){const m=new THREE.Mesh(new THREE.PlaneGeometry(2.4,3),new THREE.MeshLambertMaterial({color:0x4fc3f7,emissive:0x0277bd}));m.rotation.x=-Math.PI/2;m.position.y=.03;g.add(m);
    g.add(bx(2.4,.1,.3,0x795548,0,.06,-1.6)); g.add(bx(2.4,.1,.3,0x795548,0,.06,1.6)); hz=1.5;}
  else if(type==='gate'){for(const x of [-1.1,1.1])g.add(cyl(.09,.11,1.9,0x9ccc65,x,.95,0,6));
    const beam=cyl(.09,.09,2.4,0x7cb342,0,1.85,0,6); beam.rotation.z=Math.PI/2; g.add(beam); g.add(bx(1.4,.35,.04,0xd32f2f,0,1.6,0)); hz=.4;}
  else if(type==='tree'){g.add(cyl(.32,.45,3.2,0x6d4c41,0,1.6,0,7)); const cs=[0x2e7d32,0x388e3c,0x43a047,0x66bb6a];
    [[0,4,0,1.5],[.6,4.8,.2,1.1],[-.6,4.7,-.2,1.1],[0,5.6,0,.9]].forEach((a,i)=>{const b=new THREE.Mesh(new THREE.IcosahedronGeometry(a[3],0),L(cs[i]));b.position.set(a[0],a[1],a[2]);g.add(b);});
    hz=.75; solid=true;}
  else if(type==='ducks'){for(let i=0;i<4;i++){const d=new THREE.Group(); d.add(bx(.28,.22,.4,0xffffff,0,.3,0)); d.add(bx(.18,.18,.18,0xffffff,0,.5,-.2)); d.add(bx(.1,.05,.1,0xff9800,0,.48,-.33));
    d.add(bx(.06,.2,.06,0xff9800,-.07,.1,0)); d.add(bx(.06,.2,.06,0xff9800,.07,.1,0)); d.position.set(-.9+i*.6,0,(i%2)*.4-.2); d.rotation.y=Math.random()*.6-.3; g.add(d);} hz=.6;}
  else if(type==='cart'){g.add(bx(.9,.35,1,0x607d8b,0,.65,0)); g.add(wheel(.25,0,.25,-.62,.12)); g.add(bx(.06,.06,.9,0x8d6e63,-.35,.7,.85)); g.add(bx(.06,.06,.9,0x8d6e63,.35,.7,.85));
    g.add(bx(.06,.45,.06,0x8d6e63,-.35,.25,1.2)); g.add(bx(.06,.45,.06,0x8d6e63,.35,.25,1.2)); g.add(bx(.55,.35,.55,0xe8d5a8,0,1.0,0)); hz=.8;}
  else if(type==='bricks'){for(const [x,yy] of [[-.4,.15],[.4,.15],[0,.45],[-.4,.75],[.4,.75]])g.add(bx(.75,.3,.9,0xc0562d,x,yy,0)); hz=.6;}
  else if(type==='jars'){for(const [x,z] of [[-.5,0],[.5,0],[0,.5]]){g.add(cyl(.38,.3,.9,0x8d5524,x,.45,z,8)); g.add(cyl(.25,.38,.12,0x6d3f1a,x,.96,z,8));} hz=.6;}
  else if(type==='branch'){for(const x of [-1.1,1.1])g.add(cyl(.05,.05,1.9,0x6d4c41,x,.95,0,5));
    const bm=cyl(.1,.1,2.4,0x795548,0,1.85,0,6); bm.rotation.z=Math.PI/2; g.add(bm);
    for(let i=0;i<5;i++){const lf=new THREE.Mesh(new THREE.IcosahedronGeometry(.28,0),L(i%2?0x388e3c:0x2e7d32)); lf.position.set(-.9+i*.45,1.65,0); g.add(lf);} hz=.4;}
  else if(type==='haywall'){for(let i=0;i<4;i++)g.add(bx(1.8,.7,1,i%2?0xe0b84c:0xd4a537,0,.35+i*.7,0)); g.add(bx(1.9,.12,1.1,0x8d6e63,0,2.86,0)); hz=.6; solid=true;}
  cast(g); g.position.set(LANES[l],0,-80); scene.add(g); items.push({m:g,type,hz,top,solid});
}
const OB=['fence','log','rock','moto','buffalo','truck','haycart','tractor','pit','gate','tree','tree','ducks','cart','bricks','jars','branch','haywall'];
const LOWS=['fence','log','rock','ducks','cart','bricks','jars','pit'];
function spawn(){
  const lv=Math.min(1,(speed-SPD0)/(SPDMAX-SPD0)), l=Math.floor(Math.random()*3), pk=a=>a[Math.floor(Math.random()*a.length)];
  if(Math.random()<.12+lv*.2){                       // đủ 3 làn có vật cản, chỉ 1 làn nhảy qua được
    const free=Math.floor(Math.random()*3);
    for(let i=0;i<3;i++)mk(i===free?pk(LOWS):pk(OB),i);
    return;
  }
  mk(pk(OB),l);
  if(Math.random()<.3+lv*.4)mk(pk(OB),(l+1+Math.floor(Math.random()*2))%3);
}
function reset(){
  items.forEach(o=>scene.remove(o.m)); items=[];
  lane=1;y=0;vy=0;floorY=0;speed=SPD0;score=0;timer=0;gap=4;shake=0;duckT=0;dying=0;alive=true;wasAir=false;showoff=false;overMode=false;
  $('msg').classList.remove('over');
  player.position.set(0,0,0);player.rotation.set(0,0,0);player.scale.y=1;player.visible=true;
  dog.position.set(0,0,4);dog.rotation.y=0;dhead.rotation.x=0;mouthBone.visible=false;pile.visible=false;
  drops.forEach(d=>d.m.visible=false); pool.visible=false; boneFly.visible=false; $('blood').style.opacity=0;
  cx=0;cy=3.6;cz=6.5;lx=0;ly=1.2;lz=-6;
}
function end(type){
  alive=false; dying=DY;
  if(type==='pit')sfx.splash(); else sfx.crash();
  sfx.scream(); sfx.growl(); sfx.bark();
}
function bloodBurst(){
  drops.forEach(d=>{d.m.position.set(player.position.x,player.position.y+.6+Math.random()*.8,.2); d.vx=(Math.random()-.5)*.14; d.vy=.06+Math.random()*.12; d.vz=(Math.random()-.3)*.14; d.m.visible=true;});
  pool.position.set(player.position.x,.05,.2); pool.visible=true; poolS=0; $('blood').style.opacity=.6;
}
function showOver(){
  if(score>best){best=Math.floor(score);try{localStorage.setItem('best_'+NAME,best)}catch(e){}}
  $('res').innerHTML='Chó cắn rồi! <b style="color:#b71c1c">'+NAME+' gà quá!</b> &nbsp;Điểm: '+Math.floor(score);
  $('best').textContent='Điểm cao: '+best; $('go').textContent='↻ Chơi lại'; overMode=true; view('vMain'); $('msg').style.display='flex'; sfx.over();
}
const left=()=>{if(alive&&lane>0)lane--}, right=()=>{if(alive&&lane<2)lane++};
const jump=()=>{if(alive&&y<=floorY+.01){vy=.34;sfx.jump();}};
const duck=()=>{if(!alive)return; if(y>floorY+.01)vy=-.4; else if(duckT===0){duckT=45;sfx.swoosh();}};
addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'){if(e.key==='Enter')$('ok').click();return;}
  if(introT>0){endIntro();return;}
  if(e.key==='m'||e.key==='M')$('mute').click();
  if(e.key==='ArrowLeft'||e.key==='a')left();
  if(e.key==='ArrowRight'||e.key==='d')right();
  if(['ArrowUp',' ','w'].includes(e.key)){e.preventDefault();jump();}
  if(e.key==='ArrowDown'||e.key==='s'){e.preventDefault();duck();}
});
$('bl').onclick=left; $('brt').onclick=right; $('bj').onclick=jump; $('bd').onclick=duck;
$('pad').style.display='none'; $('mute').style.display='none';
/* ---- điện thoại: joystick ảo (trái/phải đổi làn, lên nhảy, xuống cúi) ---- */
const IS_TOUCH=('ontouchstart' in window)||navigator.maxTouchPoints>0;
const joy=$('joy'), knob=$('knob'); let jid=null, jf={x:0,y:0}, jc={x:0,y:0};
function joyMove(t){
  const dx=t.clientX-jc.x, dy=t.clientY-jc.y, m=Math.min(1,Math.hypot(dx,dy)/45), a=Math.atan2(dy,dx);
  knob.style.transform='translate('+Math.cos(a)*m*40+'px,'+Math.sin(a)*m*40+'px)';
  if(dx>32){if(!jf.x){right();jf.x=1;}} else if(dx<-32){if(!jf.x){left();jf.x=1;}} else jf.x=0;
  if(dy<-32){if(!jf.y){jump();jf.y=1;}} else if(dy>32){if(!jf.y){duck();jf.y=1;}} else jf.y=0;
}
joy.addEventListener('touchstart',e=>{e.preventDefault();e.stopPropagation(); const r=joy.getBoundingClientRect(); jc={x:r.left+r.width/2,y:r.top+r.height/2}; jid=e.changedTouches[0].identifier; joyMove(e.changedTouches[0]);},{passive:false});
joy.addEventListener('touchmove',e=>{e.preventDefault();e.stopPropagation(); for(const t of e.changedTouches)if(t.identifier===jid)joyMove(t);},{passive:false});
const joyEnd=e=>{e.stopPropagation(); jid=null; jf={x:0,y:0}; knob.style.transform='translate(0,0)';};
joy.addEventListener('touchend',joyEnd); joy.addEventListener('touchcancel',joyEnd);   // màn hình chỉ có tên + điểm (M = tắt tiếng)
let tx,ty;
wrap.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;});
wrap.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx,dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)){if(dx>30)right();else if(dx<-30)left();} else if(dy<-30)jump(); else if(dy>30)duck();});
$('go').onclick=()=>{if(!NAME){view('vName');return;} ac(); if(AC.state==='suspended')AC.resume(); ambWanted=true; ambience(true);
  $('msg').style.display='none'; startIntro();};

/* ---------- ANIMATION MỞ ĐẦU: chọc chó -> chó dậy -> bị đuổi ---------- */
let introT=0, introMv=0;
const stick=cyl(.03,.03,1.1,0x8d6e63,0,-1.35,0,5); stick.visible=false; lim.armR.add(stick);
const CAP=[[45,'Chọc nó thử xem... 😏'],[105,'Ối! Nó dậy rồi!'],[135,'CHẠY ĐI!!!']];
function setCap(t){$('cap').textContent=t; $('cap').style.display=t?'block':'none'; $('skip').style.display=introT>0?'block':'none';}
function startIntro(){
  reset(); alive=false; introT=1; introMv=0; $('blood').style.opacity=0;
  player.position.set(-3.6,0,-.45); player.rotation.set(0,-Math.PI/2,0); player.scale.y=1;
  dog.position.set(.8,0,0); dog.rotation.y=Math.PI/2; dog.scale.set(1,.6,1);      // chó nằm ngủ
  stick.visible=true; mouthBone.visible=false; jaw=0;
  cx=3.2;cy=1.8;cz=4.2;lx=-.6;ly=1;lz=0;
  setCap('Con chó đang ngủ...'); sfx.snore();
}
function endIntro(){introT=0; stick.visible=false; dog.scale.set(1,1,1); jaw=0; setCap(''); reset(); window.focus();}
function introStep(){
  const k=introT++; CAP.forEach(c=>{if(k===c[0])setCap(c[1]);});
  if(k<45){                                   // rón rén lại gần, tay cầm gậy
    const cyc=k*.28; player.position.x=-3.6+k/45*2.1;
    lim.legL.rotation.x=Math.sin(cyc*1.5)*.6; lim.legR.rotation.x=-lim.legL.rotation.x; lim.armL.rotation.x=-lim.legL.rotation.x*.5; lim.armR.rotation.x=1.2;
    dog.scale.y=.6+Math.sin(k*.1)*.02; if(k%40===20)sfx.snore();
  } else if(k<105){                           // chọc 3 phát
    lim.legL.rotation.x=0; lim.legR.rotation.x=0; lim.armL.rotation.x=0;
    const ph=(k-45)%20; lim.armR.rotation.x=1.2+(ph<8?ph/8*.45:(ph<12?.45-(ph-8)/4*.45:0));
    if(ph===8){sfx.poke(); dog.position.x=.88;} else dog.position.x+=(.8-dog.position.x)*.3;
    if(k>85)dog.scale.y+=(1-dog.scale.y)*.15; if(k===90)sfx.growl();
    player.rotation.z=Math.sin(k*.5)*.05;
  } else if(k<135){                           // chó bật dậy sủa, nhóc giật mình
    if(k===105){sfx.bark(); sfx.yelp();} if(k===118)sfx.bark();
    dog.scale.y+=(1-dog.scale.y)*.3; dog.position.y=Math.abs(Math.sin((k-105)*.4))*.25; jaw=.6*Math.abs(Math.sin(k*.6));
    player.rotation.z=0; player.position.y=Math.max(0,Math.sin((k-105)/12*Math.PI)*.5); player.position.x+=(-1.8-player.position.x)*.15;
    lim.armR.rotation.x=-2.4; lim.armL.rotation.x=-2.4;
  } else if(k<200){                           // quay lưng bỏ chạy, chó đuổi theo
    if(k===135){sfx.scream(); sfx.bark(); stick.visible=false;}
    const u=Math.min(1,(k-135)/30), cc=k*.45;
    player.rotation.y+=(0-player.rotation.y)*.15; dog.rotation.y+=(0-dog.rotation.y)*.12;
    player.position.x+=(0-player.position.x)*.06; player.position.z+=(0-player.position.z)*.08; player.position.y=0;
    dog.position.x+=(0-dog.position.x)*.06; dog.position.z+=(3.6-dog.position.z)*.05; dog.position.y=Math.abs(Math.sin(k*.3))*.12;
    introMv=SPD0*u;
    lim.legL.rotation.x=Math.sin(cc)*.9; lim.legR.rotation.x=-Math.sin(cc)*.9; lim.armL.rotation.x=-Math.sin(cc)*.9; lim.armR.rotation.x=Math.sin(cc)*.9;
    dl.forEach((q,i)=>q.rotation.x=Math.sin(cc*1.3+(i%2?Math.PI:0))*.9);
    if(k%12===0)sfx.step(); jaw*=.9;
  } else {endIntro();}
}
wrap.addEventListener('click',()=>{if(introT>0)endIntro();});

function loop(){
  requestAnimationFrame(loop); t+=.016;
  if(IS_TOUCH){const sj=(alive||introT>0)?'block':'none'; if(joy.style.display!==sj)joy.style.display=sj;}
  const mv=introT>0?introMv:(alive?speed:((dying>0||showoff)?0:.09));
  if(introT>0){introStep();}
  else if(dying>0){
    const k=DY-dying; dying--; dyk=k; shake=(k>25&&k<60)?5:0;
    if(k<25){dog.position.z+=(.4-dog.position.z)*.2; dog.position.x+=(player.position.x-dog.position.x)*.2; dog.position.y=floorY+Math.sin(k/25*Math.PI)*.9; jaw=.7;}
    else if(k<62){dog.position.set(player.position.x,floorY+.1+Math.abs(Math.sin(k*.6))*.12,.4); dog.rotation.y=Math.sin(k*1.2)*.3; jaw=Math.sin(k*1.5)>0?.6:.05;
      player.rotation.x+=(-1.45-player.rotation.x)*.12; player.position.y=floorY+.18; player.scale.y=1;}
    else{dog.position.x+=(0-dog.position.x)*.06; dog.position.z+=(2.3-dog.position.z)*.06; dog.position.y+=(0-dog.position.y)*.1;
      dog.rotation.y+=(Math.PI-dog.rotation.y)*.08; dhead.rotation.x+=(.45-dhead.rotation.x)*.1; jaw=.15;}
    if(k===25){bloodBurst(); sfx.bite(); sfx.scream(); sfx.growl();}
    if(k===55){player.visible=false; pile.position.set(player.position.x,.05,.2); pile.visible=true; sfx.crash();}
    if(k===62){mouthBone.visible=true; sfx.bark();}
    if(k>30&&k%16===0)sfx.chomp();
    if(k>25&&poolS<1.6){poolS+=.03; pool.scale.set(poolS,poolS*1.3,1);}
    if(dying===0){showoff=true; showOver();}
  } else if(showoff){
    // chó ngậm xương người, khoe giữa màn hình
    dog.position.x*=.9; dog.position.z+=(2.3-dog.position.z)*.1; dog.position.y=Math.abs(Math.sin(t*5))*.22;
    dog.rotation.y=Math.PI+Math.sin(t*1.6)*.5; dhead.rotation.x=.45+Math.sin(t*5)*.08; jaw=.12+Math.abs(Math.sin(t*9))*.1;
    tail.rotation.z=Math.sin(t*22)*.6; if(++chewT%26===0)sfx.chomp();
  } else if(alive){
    speed=Math.min(SPDMAX,speed+.00004); score+=speed*.25; timer++;
    if(timer%Math.max(20,Math.floor(50-(speed-SPD0)*140))===0)spawn();
    player.position.x+=(LANES[lane]-player.position.x)*.2; player.rotation.z=(player.position.x-LANES[lane])*.18;
    let floor=0, dead=null;
    for(let i=items.length-1;i>=0;i--){
      const o=items[i]; o.m.position.z+=speed*2;
      if(!o.snd&&o.m.position.z>-42){o.snd=1; if(o.type==='truck')sfx.horn(); else if(o.type==='buffalo')sfx.moo(); else if(o.type==='haycart')sfx.creak();
        else if(o.type==='tractor')sfx.engine(); else if(o.type==='moto')sfx.moto(); else if(o.type==='ducks')sfx.quack(); else if(o.type==='cart')sfx.creak();}
      const dz=Math.abs(o.m.position.z-player.position.z), dx=Math.abs(o.m.position.x-player.position.x);
      if(dx<.9&&dz<o.hz+.35){
        if(o.top){ if(y>=o.top-.35)floor=Math.max(floor,o.top); else dead=o; }
        else if(o.solid)dead=o;                                        // cây: không nhảy/trượt qua được
        else{ const bad=(o.type==='gate'||o.type==='branch')?(y<2.0&&(duckT===0||y>.01)):y<HT[o.type]; if(bad)dead=o; }
      }
      if(o.m.position.z>12){scene.remove(o.m);items.splice(i,1);}
    }
    if(dead)end(dead.type);
    else{
      floorY=floor; vy-=.02; y+=vy; if(y<=floor){y=floor;vy=0;}
      const air=y>floorY+.02; if(wasAir&&!air)sfx.land(); wasAir=air;
    }
    player.position.y=y;
    if(duckT>0)duckT--;
    player.scale.y+=((duckT>0&&y<=floorY+.01?.5:1)-player.scale.y)*.4;
    const gT=3.5+Math.sin(t*1.5)*.35; gap+=(gT-gap)*.03;
    dog.position.z=gap; dog.position.x+=(player.position.x-dog.position.x)*.1; tail.rotation.z=Math.sin(t*18)*.5;
    breathT++; if(breathT>=Math.max(42,Math.floor(80-(speed-SPD0)*220))){breathT=0;sfx.breath();}
    pantT++; if(pantT>=60){pantT=0;sfx.pant();}
    if(--barkT<=0){barkT=200+Math.random()*220;sfx.bark();}
    if(--growlT<=0){growlT=260+Math.random()*200;sfx.growl();}
    $('s').textContent=Math.floor(score);
  }
  const cyc=t*(9+mv*12), air=alive&&y>floorY+.02;
  if(dying===0&&!showoff&&introT===0){
    lim.legL.rotation.x=air?.5:Math.sin(cyc)*.9; lim.legR.rotation.x=air?-.5:-Math.sin(cyc)*.9;
    lim.armL.rotation.x=air?-2.5:-Math.sin(cyc)*.9; lim.armR.rotation.x=air?-2.5:Math.sin(cyc)*.9;
    if(!alive)dog.position.set(0,Math.abs(Math.sin(cyc*1.3))*.1,3.6); else dog.position.y=Math.abs(Math.sin(cyc*1.3))*.12;
    if(alive){const sg=Math.sign(Math.sin(cyc)); if(sg!==stepS&&!air&&duckT===0){stepS=sg; if(floorY>0)sfx.stepTop(); else sfx.step();}}
    jaw*=.86;
  }
  if(dying===0&&!showoff&&introT===0||showoff||dyk>=62)dl.forEach((q,i)=>q.rotation.x=Math.sin(cyc*1.3+(i%2?Math.PI:0))*(showoff||dying>0?.35:.9));
  jawG.rotation.x=-jaw;
  drops.forEach(d=>{if(!d.m.visible)return; d.vy-=.006; d.m.position.x+=d.vx; d.m.position.y+=d.vy; d.m.position.z+=d.vz;
    if(d.m.position.y<.06){d.m.position.y=.06;d.vx=d.vy=d.vz=0;}});
  roadTex.offset.y+=mv*2/8; riceTex.offset.y+=mv*2/8;
  deco.forEach(d=>{d.position.z+=mv*2; if(d.position.z>8)d.position.z-=120;});
  updTufts(mv);
  farmers.forEach(f=>{const u=f.userData; u.body.rotation.x=.95+Math.sin(t*1.4+u.ph)*.3; u.arm.rotation.x=-.95+Math.sin(t*2.8+u.ph)*.5;});
  birds.forEach(b=>{const u=b.userData; b.position.x+=u.dir*u.sp*1.2; if(b.position.x>60)b.position.x=-60; if(b.position.x<-60)b.position.x=60;
    const f=Math.sin(t*14+u.ph)*.7; u.wl.rotation.z=f; u.wr.rotation.z=-f; b.position.y+=Math.sin(t*2+u.ph)*.005;});
  clouds.forEach(c=>{c.position.x+=.03; if(c.position.x>80)c.position.x=-80;});
  // camera: bình thường bám người chơi, khi chết zoom vào con chó
  const zoom=showoff||(dying>0&&dyk>=62), r=(showoff||dying>0)?.05:(introT>0?.08:.35), IN=introT>0&&introT<135;
  const tcx=IN?3.2:(zoom?0:player.position.x*.4), tcy=IN?1.8:(zoom?1.9:3.6+player.position.y*.35), tcz=IN?4.2:(zoom?5.6:6.5),
        tlx=IN?-.6:(zoom?0:player.position.x*.2), tly=IN?1:(zoom?.75:1.2+player.position.y*.3), tlz=IN?0:(zoom?2.3:-6);
  cx+=(tcx-cx)*r; cy+=(tcy-cy)*r; cz+=(tcz-cz)*r; lx+=(tlx-lx)*r; ly+=(tly-ly)*r; lz+=(tlz-lz)*r;
  const sh=shake>0?(shake--,(Math.random()-.5)*.3):0;
  cam.position.set(cx+sh,cy+sh,cz); cam.lookAt(lx,ly,lz);
  renderer.render(scene,cam);
}
loop();
addEventListener('resize',()=>{renderer.setSize(W(),H());cam.aspect=W()/H();cam.updateProjectionMatrix();});
</script>
"""

components.html(GAME_HTML, height=680, scrolling=False)
