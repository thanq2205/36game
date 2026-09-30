import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chạy trốn chó dữ", page_icon="🏃", layout="wide")
st.markdown("<h2 style='text-align:center'>🏃💨🐕 Chạy trốn chó dữ 3D</h2>", unsafe_allow_html=True)

name = st.text_input("Nhập username trước khi chơi", max_chars=16, placeholder="VD: Speedy123")

GAME_HTML = r"""
<style>
  html,body{margin:0;background:#8fd0ff;overflow:hidden;font-family:'Segoe UI',Arial,sans-serif}
  #wrap{position:relative;width:100%;height:660px;border-radius:14px;overflow:hidden}
  canvas{display:block;width:100%;height:100%}
  #hud{position:absolute;top:10px;left:12px;background:rgba(255,255,255,.85);color:#233;font-weight:600;
       padding:6px 14px;border-radius:20px;box-shadow:0 2px 8px rgba(0,0,0,.2);font-size:16px}
  #tip{position:absolute;top:52px;left:14px;font-weight:700;font-size:16px;color:#2e7d32;text-shadow:0 0 4px #fff}
  #msg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
       background:linear-gradient(160deg,rgba(120,200,255,.55),rgba(255,236,170,.55));backdrop-filter:blur(3px)}
  #card{background:rgba(255,255,255,.94);border-radius:24px;padding:26px 40px;text-align:center;color:#234;
        box-shadow:0 10px 40px rgba(0,60,120,.35);max-width:440px}
  #card h1{margin:4px 0 6px;font-size:30px;background:linear-gradient(90deg,#ff7043,#ffb300);-webkit-background-clip:text;color:transparent}
  #logo{font-size:44px}
  #t{font-size:20px;margin:8px 0}
  #best{color:#f57c00;font-weight:700;margin-bottom:10px}
  #go{font-size:22px;font-weight:700;padding:12px 38px;border:0;border-radius:40px;color:#fff;cursor:pointer;
      background:linear-gradient(90deg,#ff7043,#ffa000);box-shadow:0 5px 0 #c75b16;transition:transform .1s}
  #go:hover{transform:scale(1.06)} #go:active{transform:translateY(3px);box-shadow:0 2px 0 #c75b16}
  #how{margin-top:14px;font-size:14px;color:#456;line-height:1.7;text-align:left;background:#eef7ff;border-radius:12px;padding:10px 16px}
  button{cursor:pointer}
  #pad{position:absolute;bottom:10px;width:100%;display:flex;justify-content:center;gap:10px}
  #pad button{font-size:20px;padding:8px 18px;border:0;border-radius:12px;background:rgba(255,255,255,.7)}
  #mute{position:absolute;top:8px;right:10px;border:0;border-radius:20px;padding:6px 12px;background:rgba(255,255,255,.85);font-size:16px}
  #blood{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .4s;
         background:radial-gradient(transparent 35%,rgba(200,0,0,.85))}
</style>
<div id="wrap">
  <div id="hud">👤 <span id="n"></span> &nbsp;|&nbsp; 🏁 <span id="s">0</span> &nbsp;|&nbsp; 🪙 <span id="c">0</span> &nbsp;|&nbsp; ⭐ Cấp <span id="lv">1</span></div>
  <div id="tip"></div><div id="blood"></div>
  <button id="mute">🔊</button>
  <div id="msg"><div id="card">
    <div id="logo">🏃💨🐕</div><h1>CHẠY TRỐN CHÓ DỮ</h1>
    <div id="t"></div><div id="best"></div>
    <button id="go">▶ CHƠI NGAY</button>
    <div id="how">⬅ ➡ &nbsp;đổi làn &nbsp;|&nbsp; ⬆ / Space: nhảy &nbsp;|&nbsp; ⬇ / S: cúi<br>
      🚧 hàng rào, hố nước: nhảy · 🚗 ô tô: né hoặc nhảy cao · 🛢 ống: cúi<br>
      🦴 nhặt xương: chó dừng lại gặm · ⚠ <b>đụng 1 lần là chó cắn!</b></div>
  </div></div>
  <div id="pad"><button id="bl">◀</button><button id="bj">▲</button><button id="bd">▼</button><button id="br">▶</button></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const NAME=__NAME__, $=id=>document.getElementById(id);
$('n').textContent=NAME;
$('t').innerHTML='Chào <b>'+NAME+'</b>! Chó đang đuổi, chạy đi!';
let best=0; try{best=+localStorage.getItem('best_'+NAME)||0}catch(e){}
$('best').textContent='🏆 Điểm cao: '+best;
const wrap=$('wrap'), W=()=>wrap.clientWidth, H=()=>wrap.clientHeight;

/* ================= ÂM THANH ================= */
let AC=null, muted=false, musicT=null;
const ac=()=>{if(!AC)AC=new (window.AudioContext||window.webkitAudioContext)();return AC};
function nz(d,vol,f,q,att,type){            // nhiễu lọc có đường bao (thở, bước chân, sủa...)
  if(muted||!AC)return;
  const n=Math.floor(AC.sampleRate*d), b=AC.createBuffer(1,n,AC.sampleRate), a=b.getChannelData(0);
  for(let i=0;i<n;i++)a[i]=Math.random()*2-1;
  const s=AC.createBufferSource(); s.buffer=b;
  const fl=AC.createBiquadFilter(); fl.type=type||'bandpass'; fl.frequency.value=f; fl.Q.value=q||1;
  const g=AC.createGain(), T=AC.currentTime;
  g.gain.setValueAtTime(.0001,T); g.gain.linearRampToValueAtTime(vol,T+(att||.02)); g.gain.exponentialRampToValueAtTime(.0001,T+d);
  s.connect(fl); fl.connect(g); g.connect(AC.destination); s.start();
}
function tn(f1,f2,d,type,vol,fc){            // tone qua bộ lọc formant
  if(muted||!AC)return;
  const o=AC.createOscillator(), fl=AC.createBiquadFilter(), g=AC.createGain(), T=AC.currentTime;
  o.type=type; o.frequency.setValueAtTime(f1,T); o.frequency.exponentialRampToValueAtTime(Math.max(f2,1),T+d);
  fl.type='bandpass'; fl.frequency.value=fc||2000; fl.Q.value=1.5;
  g.gain.setValueAtTime(vol,T); g.gain.exponentialRampToValueAtTime(.0001,T+d);
  o.connect(fl); fl.connect(g); g.connect(AC.destination); o.start(); o.stop(T+d);
}
function bark1(v){ tn(380,200,.16,'sawtooth',.3*v,900); tn(760,400,.12,'square',.06*v,1800); nz(.1,.3*v,1400,1.5,.004); }
const sfx={
  coin:()=>{tn(988,988,.08,'square',.06,3000); setTimeout(()=>tn(1319,1319,.16,'square',.06,3000),70)},
  ting:()=>{tn(1200,1800,.25,'sine',.15,4000)},
  jump:()=>{tn(250,600,.18,'sine',.12,900); nz(.14,.16,1200,1,.02)},
  bark:()=>{bark1(1); setTimeout(()=>bark1(.9),210); setTimeout(()=>bark1(.8),420)},
  bark1:()=>bark1(.6),
  growl:()=>{ if(muted||!AC)return; const T=AC.currentTime,o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),
      g=AC.createGain(),f=AC.createBiquadFilter(); o.type='sawtooth'; o.frequency.value=78; l.frequency.value=26; lg.gain.value=.12;
      f.type='lowpass'; f.frequency.value=380; g.gain.setValueAtTime(.16,T); g.gain.linearRampToValueAtTime(.001,T+.9);
      l.connect(lg); lg.connect(g.gain); o.connect(f); f.connect(g); g.connect(AC.destination); o.start();l.start();o.stop(T+.9);l.stop(T+.9); },
  pant:()=>{[0,.13,.26,.39].forEach(t=>setTimeout(()=>nz(.1,.13,3200,2,.012),t*1000))},
  chomp:()=>{nz(.09,.32,650,2,.004); tn(190,90,.09,'square',.09,500); setTimeout(()=>{nz(.09,.28,700,2,.004);tn(170,80,.09,'square',.08,500)},130)},
  breath:()=>{nz(.34,.16,1700,.8,.2); setTimeout(()=>nz(.4,.19,1200,.7,.06),330)},    // hít vào, thở ra
  gasp:()=>nz(.25,.25,1500,.8,.05),
  step:()=>nz(.07,.3+Math.random()*.1,350+Math.random()*250,1,.005),
  swoosh:()=>nz(.25,.2,1800,1,.08),
  crash:()=>{nz(.4,.6,700,.5,.01,'lowpass'); tn(140,35,.4,'sawtooth',.25,300)},
  splash:()=>nz(.6,.4,3500,.6,.05),
  scream:()=>{ if(muted||!AC)return; const T=AC.currentTime,o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),
      g=AC.createGain(),f=AC.createBiquadFilter(); o.type='sawtooth'; o.frequency.setValueAtTime(600,T); o.frequency.linearRampToValueAtTime(900,T+.3);
      l.frequency.value=8; lg.gain.value=50; f.type='bandpass'; f.frequency.value=1400; f.Q.value=.8;
      g.gain.setValueAtTime(.18,T); g.gain.exponentialRampToValueAtTime(.001,T+1);
      l.connect(lg); lg.connect(o.frequency); o.connect(f); f.connect(g); g.connect(AC.destination); o.start();l.start();o.stop(T+1);l.stop(T+1); },
  bite:()=>{nz(.2,.7,2200,1,.005); tn(220,60,.25,'square',.15,600)},
  over:()=>{tn(400,80,1,'triangle',.2,1000)}
};
const notes=[262,294,330,392,440,392,330,294]; let step=0;
function music(on){clearInterval(musicT); if(on)musicT=setInterval(()=>{tn(notes[step%8],notes[step%8],.2,'triangle',.05,1500); if(step%2==0)tn(65,60,.15,'sine',.08,300); step++;},260);}
$('mute').onclick=()=>{muted=!muted;$('mute').textContent=muted?'🔇':'🔊'};

/* ================= CẢNH BAN NGÀY ================= */
function canvasTex(w,h,draw,rx,ry){
  const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h);
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; if(rx)t.repeat.set(rx,ry); return t;
}
const sky=canvasTex(1024,512,(x,w,h)=>{
  const g=x.createLinearGradient(0,0,0,h); g.addColorStop(0,'#3d8fe0'); g.addColorStop(.6,'#8fd0ff'); g.addColorStop(1,'#e6f6ff');
  x.fillStyle=g; x.fillRect(0,0,w,h);
  const rg=x.createRadialGradient(w*.78,h*.22,0,w*.78,h*.22,120);
  rg.addColorStop(0,'rgba(255,255,235,1)'); rg.addColorStop(.25,'rgba(255,240,170,.9)'); rg.addColorStop(1,'rgba(255,240,170,0)');
  x.fillStyle=rg; x.fillRect(0,0,w,h);
  for(let i=0;i<12;i++){const cx=Math.random()*w,cy=50+Math.random()*h*.45;
    for(let k=0;k<7;k++){const px=cx+(k-3)*26+Math.random()*10,py=cy+Math.random()*16-8,r=24+Math.random()*22;
      const rr=x.createRadialGradient(px,py,0,px,py,r); rr.addColorStop(0,'rgba(255,255,255,.95)'); rr.addColorStop(1,'rgba(255,255,255,0)');
      x.fillStyle=rr; x.fillRect(px-r,py-r,r*2,r*2);}}
});
const scene=new THREE.Scene(); scene.background=sky; scene.fog=new THREE.Fog(0xcfeaff,28,95);
const cam=new THREE.PerspectiveCamera(72,W()/H(),.1,120);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(W(),H()); wrap.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x88aa77,1.05));
const sun=new THREE.DirectionalLight(0xfff2cc,.9); sun.position.set(8,14,4); scene.add(sun);

const roadTex=canvasTex(256,256,(x,w,h)=>{
  x.fillStyle='#45464a'; x.fillRect(0,0,w,h);
  for(let i=0;i<5000;i++){const v=55+Math.random()*35;x.fillStyle='rgb('+v+','+v+','+(v+4)+')';x.fillRect(Math.random()*w,Math.random()*h,2,2);}
  x.fillStyle='#fff'; x.fillRect(w*.375-3,0,6,h*.5); x.fillRect(w*.625-3,0,6,h*.5);
  x.fillStyle='#ffc107'; x.fillRect(4,0,6,h); x.fillRect(w-10,0,6,h);
},1,25);
const road=new THREE.Mesh(new THREE.PlaneGeometry(8,200),new THREE.MeshLambertMaterial({map:roadTex}));
road.rotation.x=-Math.PI/2; road.position.z=-90; scene.add(road);
const swTex=canvasTex(64,64,(x,w,h)=>{x.fillStyle='#cfcfcf';x.fillRect(0,0,w,h);x.strokeStyle='#a5a5a5';x.lineWidth=3;x.strokeRect(0,0,w,h);},1,60);
for(const sx of [-1,1]){const sw=new THREE.Mesh(new THREE.PlaneGeometry(1.6,200),new THREE.MeshLambertMaterial({map:swTex}));
  sw.rotation.x=-Math.PI/2; sw.position.set(sx*4.8,.03,-90); scene.add(sw);}
const gTex=canvasTex(64,64,(x,w,h)=>{x.fillStyle='#5fae4a';x.fillRect(0,0,w,h);
  for(let i=0;i<500;i++){x.fillStyle=Math.random()<.5?'#6fc058':'#4e9a3d';x.fillRect(Math.random()*w,Math.random()*h,2,3);}},40,40);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(240,240),new THREE.MeshLambertMaterial({map:gTex}));
ground.rotation.x=-Math.PI/2; ground.position.set(0,-.02,-80); scene.add(ground);

const deco=[];                                  // mọi thứ ven đường, chạy lùi rồi quay vòng
function addDeco(m,x,z){m.position.x=x; m.position.z=z; scene.add(m); deco.push(m);}
const bTex=canvasTex(128,256,(x,w,h)=>{x.fillStyle='#f2f2f2';x.fillRect(0,0,w,h);
  for(let r=0;r<10;r++)for(let c=0;c<4;c++){x.fillStyle='#8fc9f0';x.fillRect(10+c*29,10+r*24,18,14);x.fillStyle='#fff';x.fillRect(10+c*29,10+r*24,18,3);}});
const tints=[0xffcdd2,0xfff59d,0xb2dfdb,0xd1c4e9,0xffe0b2,0xc5e1a5];
for(let i=0;i<20;i++)for(const sx of [-1,1]){
  const s=.7+Math.random()*1,b=new THREE.Mesh(new THREE.BoxGeometry(4,10,4),new THREE.MeshLambertMaterial({map:bTex,color:tints[(i+(sx>0?2:0))%6]}));
  b.scale.y=s; b.position.y=5*s; addDeco(b,sx*(8.6+Math.random()*1.2),-i*6);
}
function tree(){const g=new THREE.Group();
  const tr=new THREE.Mesh(new THREE.CylinderGeometry(.14,.2,1.5,8),new THREE.MeshLambertMaterial({color:0x795548})); tr.position.y=.75; g.add(tr);
  const f1=new THREE.Mesh(new THREE.SphereGeometry(.95,10,8),new THREE.MeshLambertMaterial({color:0x43a047})); f1.position.y=2.2; g.add(f1);
  const f2=new THREE.Mesh(new THREE.SphereGeometry(.6,10,8),new THREE.MeshLambertMaterial({color:0x66bb6a})); f2.position.set(.3,2.8,0); g.add(f2); return g;}
function lamp(){const g=new THREE.Group(),mt=new THREE.MeshLambertMaterial({color:0x455a64});
  const p=new THREE.Mesh(new THREE.CylinderGeometry(.06,.08,3.2,8),mt); p.position.y=1.6; g.add(p);
  const h=new THREE.Mesh(new THREE.SphereGeometry(.2,10,8),new THREE.MeshBasicMaterial({color:0xfff59d})); h.position.y=3.3; g.add(h); return g;}
for(let i=0;i<10;i++)for(const sx of [-1,1]){addDeco(tree(),sx*5.3,-i*12-(sx>0?4:0));}
for(let i=0;i<8;i++)for(const sx of [-1,1])addDeco(lamp(),sx*4.15,-i*15-(sx>0?7:0));
const clouds=[];
for(let i=0;i<7;i++){const g=new THREE.Group(),m=new THREE.MeshBasicMaterial({color:0xffffff,fog:false});
  for(let k=0;k<5;k++){const s=new THREE.Mesh(new THREE.SphereGeometry(3+Math.random()*2,10,8),m);s.position.set(k*3.5-7,Math.random()*1.5,Math.random()*2);s.scale.y=.6;g.add(s);}
  g.position.set(-50+Math.random()*100,20+Math.random()*10,-70-Math.random()*30); scene.add(g); clouds.push(g);}
function shadow(){const s=new THREE.Mesh(new THREE.CircleGeometry(.6,16),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.28}));
  s.rotation.x=-Math.PI/2; s.position.y=.04; s.scale.y=1.6; return s;}

/* ================= NHÂN VẬT ================= */
const skin=new THREE.MeshLambertMaterial({color:0x3a2216}), M=c=>new THREE.MeshLambertMaterial({color:c});
const player=new THREE.Group(), lim={};
function limb(w,h,d,mat,x,y){const p=new THREE.Group();p.position.set(x,y,0);
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.y=-h/2;p.add(m);player.add(p);return p;}
const torso=new THREE.Mesh(new THREE.BoxGeometry(.8,.85,.45),M(0xd32f2f)); torso.position.y=1.15; player.add(torso);
const head=new THREE.Mesh(new THREE.SphereGeometry(.34,16,16),skin); head.position.y=1.85; player.add(head);
for(let i=0;i<14;i++){const h=new THREE.Mesh(new THREE.SphereGeometry(.13,8,8),M(0x0a0a0a));
  const a=Math.random()*6.28,e=Math.random()*1.1; h.position.set(Math.cos(a)*.27*Math.cos(e),1.95+Math.sin(e)*.28,Math.sin(a)*.27*Math.cos(e)); player.add(h);}
const shades=new THREE.Mesh(new THREE.BoxGeometry(.5,.1,.05),M(0)); shades.position.set(0,1.88,-.32); player.add(shades);
lim.armL=limb(.22,.7,.22,skin,-.52,1.5); lim.armR=limb(.22,.7,.22,skin,.52,1.5);
lim.legL=limb(.28,.75,.28,M(0x1a237e),-.2,.75); lim.legR=limb(.28,.75,.28,M(0x1a237e),.2,.75);
for(const x of [-.2,.2]){const s=new THREE.Mesh(new THREE.BoxGeometry(.3,.12,.4),M(0xffffff));s.position.set(x,.06,-.05);player.add(s);}
player.add(shadow()); scene.add(player);

/* ================= CHÓ ================= */
const dog=new THREE.Group(), dm=M(0x8d5a2b), dl=[];
const dbody=new THREE.Mesh(new THREE.BoxGeometry(.6,.55,1.2),dm); dbody.position.y=.7; dog.add(dbody);
const dhead=new THREE.Group(); dhead.position.set(0,.95,-.75); dog.add(dhead);
const hd=new THREE.Mesh(new THREE.BoxGeometry(.45,.42,.5),dm); dhead.add(hd);
const snout=new THREE.Mesh(new THREE.BoxGeometry(.25,.2,.3),M(0x3e2a15)); snout.position.set(0,-.07,-.35); dhead.add(snout);
const nose=new THREE.Mesh(new THREE.BoxGeometry(.1,.08,.05),M(0)); nose.position.set(0,0,-.52); dhead.add(nose);
for(const x of [-.17,.17]){const e=new THREE.Mesh(new THREE.BoxGeometry(.12,.28,.1),M(0x3e2a15));e.position.set(x,.3,.05);dhead.add(e);
  const eye=new THREE.Mesh(new THREE.BoxGeometry(.07,.07,.03),M(0xff1744));eye.position.set(x,.08,-.26);dhead.add(eye);}
const teeth=new THREE.Mesh(new THREE.BoxGeometry(.2,.05,.03),M(0xffffff)); teeth.position.set(0,-.18,-.5); dhead.add(teeth);
function boneMesh(){const g=new THREE.Group(),m=M(0xfff8e1);
  const c=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.6,10),m); c.rotation.z=Math.PI/2; g.add(c);
  for(const x of [-.32,.32])for(const z of [-.07,.07]){const s=new THREE.Mesh(new THREE.SphereGeometry(.12,8,8),m);s.position.set(x,0,z);g.add(s);} return g;}
const mouthBone=boneMesh(); mouthBone.position.set(0,-.2,-.5); mouthBone.rotation.y=Math.PI/2; mouthBone.visible=false; dhead.add(mouthBone);
const tail=new THREE.Mesh(new THREE.BoxGeometry(.1,.1,.5),dm); tail.position.set(0,.95,.75); tail.rotation.x=.6; dog.add(tail);
for(const [x,z] of [[-.2,-.4],[.2,-.4],[-.2,.4],[.2,.4]]){
  const p=new THREE.Group();p.position.set(x,.45,z);const l=new THREE.Mesh(new THREE.BoxGeometry(.13,.45,.13),dm);l.position.y=-.22;p.add(l);dog.add(p);dl.push(p);}
dog.add(shadow()); scene.add(dog);

/* ================= LOGIC ================= */
const LANES=[-2,0,2], SPD0=.15, SPDMAX=.36;
let lane=1,y=0,vy=0,speed=SPD0,score=0,coins=0,alive=false,items=[],timer=0,gap=4,shake=0,t=0,
    duckT=0,dying=0,stepS=0,breathT=0,pantT=0,barkT=200,growlT=150,busy=0,started=false;
const wood=canvasTex(64,64,(x,w,h)=>{x.fillStyle='#a1785c';x.fillRect(0,0,w,h);x.fillStyle='#5d4037';
  for(let i=0;i<64;i+=16)x.fillRect(i,0,3,h);x.fillStyle='#4e342e';x.fillRect(0,14,w,5);x.fillRect(0,40,w,5);});
const coinM=new THREE.MeshLambertMaterial({color:0xffd600,emissive:0x8a6d00});
const carCols=[0xe53935,0x1e88e5,0xfdd835,0x43a047,0xf5f5f5,0xff7043];
function box(w,h,d,c,x,y,z){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),M(c));m.position.set(x,y,z);return m;}
function mk(type,l,zo){
  const g=new THREE.Group(); let hz=.6;
  if(type==='fence'){const m=new THREE.Mesh(new THREE.BoxGeometry(1.7,.75,.25),new THREE.MeshLambertMaterial({map:wood}));m.position.y=.4;g.add(m);hz=.3;}
  else if(type==='car'){g.add(box(1.6,.7,3.2,carCols[Math.floor(Math.random()*6)],0,.6,0)); g.add(box(1.3,.55,1.5,0x90caf9,0,1.2,.2));
    for(const [x,z] of [[-.8,-1],[.8,-1],[-.8,1],[.8,1]]){const w=new THREE.Mesh(new THREE.CylinderGeometry(.32,.32,.2,12),M(0x222222));w.rotation.z=Math.PI/2;w.position.set(x,.32,z);g.add(w);}
    g.add(box(.3,.15,.05,0xfff59d,-.5,.65,-1.62)); g.add(box(.3,.15,.05,0xfff59d,.5,.65,-1.62)); hz=1.6;}
  else if(type==='pit'){const m=new THREE.Mesh(new THREE.PlaneGeometry(2.2,3),new THREE.MeshLambertMaterial({color:0x29b6f6,emissive:0x0277bd}));m.rotation.x=-Math.PI/2;m.position.y=.03;g.add(m);hz=1.5;}
  else if(type==='pipe'){const c=new THREE.Mesh(new THREE.CylinderGeometry(.35,.35,2.2,16),M(0x90a4ae));c.rotation.z=Math.PI/2;c.position.y=1.7;g.add(c);
    g.add(box(.2,1.7,.3,0x546e7a,-1.05,.85,0)); g.add(box(.2,1.7,.3,0x546e7a,1.05,.85,0)); hz=.4;}
  else if(type==='bone'){const b=boneMesh();b.position.y=1.2;b.scale.set(1.5,1.5,1.5);g.add(b);}
  else{const m=new THREE.Mesh(new THREE.CylinderGeometry(.4,.4,.1,20),coinM);m.rotation.x=Math.PI/2;m.position.y=1.1;g.add(m);}
  g.position.set(LANES[l],0,-70-(zo||0)); scene.add(g); items.push({m:g,type,hz});
}
function spawn(){
  const lv=Math.min(1,(speed-SPD0)/(SPDMAX-SPD0)), r=Math.random(), l=Math.floor(Math.random()*3);
  if(r<.3){for(let i=0;i<3;i++)mk('coin',l,i*2.5);return;}
  if(r<.4&&busy===0){mk('bone',l);return;}
  const type=['fence','car','pit','pipe'][Math.floor(Math.random()*4)]; mk(type,l);
  if(Math.random()<.08+lv*.3)mk(['fence','car','pit','pipe'][Math.floor(Math.random()*4)],(l+1+Math.floor(Math.random()*2))%3);
}
function reset(){
  items.forEach(o=>scene.remove(o.m)); items=[];
  lane=1;y=0;vy=0;speed=SPD0;score=0;coins=0;timer=0;gap=4;shake=0;duckT=0;dying=0;busy=0;alive=true;started=true;
  player.position.set(0,0,0);player.rotation.x=0;player.scale.y=1;dog.position.set(0,0,4);mouthBone.visible=false;
  $('blood').style.opacity=0;$('tip').textContent='';
}
function end(type){
  alive=false; dying=100; music(false); $('tip').textContent='';
  if(type==='pit')sfx.splash(); else sfx.crash();
  sfx.scream(); sfx.growl(); sfx.bark(); setTimeout(()=>{sfx.bite();$('blood').style.opacity=.85},400); setTimeout(sfx.scream,600);
}
function showOver(){
  if(score>best){best=Math.floor(score);try{localStorage.setItem('best_'+NAME,best)}catch(e){}}
  $('t').innerHTML='🐕 Chó cắn rồi!<br><b style="color:#e65100;font-size:26px">'+NAME+' gà quá! 🐔</b><br><small>Điểm: '+Math.floor(score)+' | Xu: '+coins+'</small>';
  $('best').textContent='🏆 Điểm cao: '+best; $('go').textContent='↻ CHƠI LẠI'; $('msg').style.display='flex'; sfx.over();
}
const left=()=>{if(alive&&lane>0)lane--}, right=()=>{if(alive&&lane<2)lane++};
const jump=()=>{if(alive&&y===0){vy=.34;sfx.jump();}};
const duck=()=>{if(!alive)return; if(y>0)vy=-.4; else if(duckT===0){duckT=45;sfx.swoosh();}};
addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='a')left();
  if(e.key==='ArrowRight'||e.key==='d')right();
  if(['ArrowUp',' ','w'].includes(e.key)){e.preventDefault();jump();}
  if(e.key==='ArrowDown'||e.key==='s'){e.preventDefault();duck();}
});
$('bl').onclick=left; $('br').onclick=right; $('bj').onclick=jump; $('bd').onclick=duck;
let tx,ty;
wrap.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;});
wrap.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx,dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)){if(dx>30)right();else if(dx<-30)left();} else if(dy<-30)jump(); else if(dy>30)duck();});
$('go').onclick=()=>{ac(); if(AC.state==='suspended')AC.resume(); $('msg').style.display='none'; reset(); music(true); window.focus();};

function loop(){
  requestAnimationFrame(loop); t+=.016;
  const mv=alive?speed:(dying>0?0:.09);            // menu: cảnh vẫn chạy nhẹ phía sau
  if(dying>0){
    dying--; shake=6;
    dog.position.z+=(.2-dog.position.z)*.15; dog.position.x+=(player.position.x-dog.position.x)*.2;
    dog.position.y=.4+Math.abs(Math.sin(dying*.5))*.35; dhead.rotation.x=Math.sin(dying*.8)*.3;
    player.rotation.x+=(-1.4-player.rotation.x)*.1; player.position.y=.15; player.scale.y=1;
    if(dying===0)showOver();
  } else if(alive){
    speed=Math.min(SPDMAX,speed+.00003); score+=speed*.25; timer++;
    if(timer%Math.max(24,Math.floor(62-(speed-SPD0)*150))===0)spawn();
    player.position.x+=(LANES[lane]-player.position.x)*.2;
    vy-=.02; y=Math.max(0,y+vy); if(y===0)vy=0; player.position.y=y;
    if(duckT>0)duckT--;
    player.scale.y+=((duckT>0&&y===0?.5:1)-player.scale.y)*.4;
    // chó
    if(busy>0){busy--; if(busy%18===0)sfx.chomp(); if(busy===0){mouthBone.visible=false;$('tip').textContent='';}}
    const gT=busy>0?7.5:3.5+Math.sin(t*1.5)*.35; gap+=(gT-gap)*.03;
    dog.position.z=gap; dog.position.x+=(player.position.x-dog.position.x)*.1;
    dhead.rotation.x=busy>0?Math.sin(t*28)*.28:0; tail.rotation.z=Math.sin(t*(busy>0?30:18))*.5;
    // âm thanh sống động: người thở, chó thở hổn hển/sủa/gầm gừ
    breathT++; if(breathT>=Math.max(42,Math.floor(80-(speed-SPD0)*220))){breathT=0;sfx.breath();}
    if(busy===0){pantT++; if(pantT>=60){pantT=0;sfx.pant();}
      if(--barkT<=0){barkT=200+Math.random()*220;sfx.bark();}
      if(--growlT<=0){growlT=260+Math.random()*200;sfx.growl();}}
    // xử lý va chạm
    for(let i=items.length-1;i>=0;i--){
      const o=items[i]; o.m.position.z+=speed*2;
      if(o.type==='coin'||o.type==='bone')o.m.rotation.y+=.1;
      const dz=Math.abs(o.m.position.z-player.position.z),dx=Math.abs(o.m.position.x-player.position.x);
      if(dz<o.hz+.4&&dx<.9){
        if(o.type==='coin'){coins++;score+=2;sfx.coin();scene.remove(o.m);items.splice(i,1);continue;}
        if(o.type==='bone'){busy=320;mouthBone.visible=true;score+=10;sfx.ting();sfx.bark();setTimeout(sfx.growl,400);
          $('tip').textContent='🦴 Chó đang gặm xương, chạy đi!';scene.remove(o.m);items.splice(i,1);continue;}
        const bad=o.type==='fence'?y<.7:o.type==='car'?y<1.6:o.type==='pit'?y<.35:(duckT===0||y>0);
        if(bad){end(o.type);break;}
      }
      if(o.m.position.z>10){scene.remove(o.m);items.splice(i,1);}
    }
    $('s').textContent=Math.floor(score); $('c').textContent=coins; $('lv').textContent=Math.floor((speed-SPD0)/.03)+1;
  }
  // hoạt ảnh chạy
  const cyc=t*(9+mv*12), air=y>0&&alive;
  if(dying===0){
    lim.legL.rotation.x=air?.5:Math.sin(cyc)*.9; lim.legR.rotation.x=air?-.5:-Math.sin(cyc)*.9;
    lim.armL.rotation.x=air?-2.5:-Math.sin(cyc)*.9; lim.armR.rotation.x=air?-2.5:Math.sin(cyc)*.9;
    dl.forEach((q,i)=>q.rotation.x=Math.sin(cyc*1.3+(i%2?Math.PI:0))*(busy>0?.4:.9));
    if(!alive){dog.position.set(0,Math.abs(Math.sin(cyc*1.3))*.1,3.6);}
    else dog.position.y=Math.abs(Math.sin(cyc*1.3))*.12;
    if(alive){const sg=Math.sign(Math.sin(cyc)); if(sg!==stepS&&y===0&&duckT===0){stepS=sg;sfx.step();}}
  }
  roadTex.offset.y+=mv*2/8; swTex.offset.y+=mv*2/1.6/1;
  deco.forEach(d=>{d.position.z+=mv*2; if(d.position.z>8)d.position.z-=120;});
  clouds.forEach(c=>{c.position.x+=.03; if(c.position.x>70)c.position.x=-70;});
  const sh=shake>0?(shake--,(Math.random()-.5)*.3):0;
  cam.position.set(sh,3.6+sh,6.5); cam.lookAt(0,1.2,-6);
  renderer.render(scene,cam);
}
loop();
addEventListener('resize',()=>{renderer.setSize(W(),H());cam.aspect=W()/H();cam.updateProjectionMatrix();});
</script>
"""

if name.strip():
    components.html(GAME_HTML.replace("__NAME__", json.dumps(name.strip())), height=680, scrolling=False)
else:
    st.info("👆 Nhập username rồi game sẽ hiện ra.")
