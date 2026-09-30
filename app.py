import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chạy trốn chó dữ", page_icon="🏃", layout="wide")
st.markdown("<h3 style='text-align:center'>🌾🏃💨🐕 Chạy trốn chó dữ: làng quê</h3>", unsafe_allow_html=True)

GAME_HTML = r"""
<style>
  html,body{margin:0;background:#8fd0ff;overflow:hidden;font-family:'Segoe UI',Arial,sans-serif}
  #wrap{position:relative;width:100%;height:660px;border-radius:14px;overflow:hidden}
  canvas{display:block;width:100%;height:100%}
  #hud{position:absolute;top:10px;left:12px;background:rgba(255,255,255,.88);color:#233;font-weight:600;
       padding:6px 14px;border-radius:20px;box-shadow:0 2px 8px rgba(0,0,0,.2);font-size:16px}
  #msg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(40,90,40,.35)}
  #card{background:#fff;border-radius:20px;padding:26px 34px;text-align:center;color:#234;width:340px;
        box-shadow:0 10px 36px rgba(0,50,0,.4)}
  #card h1{margin:0 0 10px;font-size:28px;color:#2e7d32}
  .btn{display:block;width:100%;margin:10px 0;font-size:19px;font-weight:700;padding:12px;border:0;border-radius:30px;
       cursor:pointer;color:#fff;background:#43a047;box-shadow:0 4px 0 #2e7d32}
  .btn.alt{background:#1e88e5;box-shadow:0 4px 0 #1565c0} .btn.or{background:#fb8c00;box-shadow:0 4px 0 #c56a00}
  .btn:active{transform:translateY(3px);box-shadow:none}
  #nm{width:88%;font-size:18px;padding:10px;border:2px solid #a5d6a7;border-radius:10px;text-align:center;margin:8px 0}
  #guide{text-align:left;font-size:15px;line-height:1.7}
  #best{color:#e65100;font-weight:700}
  #pad{position:absolute;bottom:10px;width:100%;display:flex;justify-content:center;gap:10px}
  #pad button{font-size:20px;padding:8px 18px;border:0;border-radius:12px;background:rgba(255,255,255,.7)}
  #mute{position:absolute;top:8px;right:10px;border:0;border-radius:20px;padding:6px 12px;background:rgba(255,255,255,.88);font-size:16px}
  #blood{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .3s;
         background:radial-gradient(transparent 30%,rgba(190,0,0,.85))}
</style>
<div id="wrap">
  <div id="hud">👤 <span id="n">?</span> &nbsp;|&nbsp; 🏁 <span id="s">0</span> &nbsp;|&nbsp; 🪙 <span id="c">0</span> &nbsp;|&nbsp; ⭐ Cấp <span id="lv">1</span></div>
  <div id="blood"></div>
  <button id="mute">🔊</button>
  <div id="msg"><div id="card">
    <div id="vMain"><h1>🌾 CHẠY TRỐN CHÓ DỮ</h1><div id="res"></div><div id="best"></div>
      <button class="btn" id="go">▶ CHƠI</button>
      <button class="btn alt" id="bg">📖 HƯỚNG DẪN</button>
      <button class="btn or" id="br2">✏️ ĐỔI TÊN</button></div>
    <div id="vGuide" style="display:none"><h1>📖 Hướng dẫn</h1><div id="guide">
      ⬅ ➡ : đổi làn<br>⬆ / Space : nhảy<br>⬇ / S : cúi, trượt<br>
      🚧 Hàng rào, 💧 mương nước: nhảy<br>🐃 Trâu, 🌾 xe rơm: né hoặc nhảy cao<br>🚚 Xe tải: phải né sang làn khác<br>
      🎋 Cổng tre: phải cúi<br>🪙 Nhặt xu lấy điểm<br><b>⚠ Đụng 1 lần là chó cắn!</b></div>
      <button class="btn" id="bk1">◀ Quay lại</button></div>
    <div id="vName" style="display:none"><h1>✏️ Nhập tên</h1>
      <input id="nm" maxlength="16" placeholder="Username của bạn"><button class="btn" id="ok">✔ Lưu</button></div>
  </div></div>
  <div id="pad"><button id="bl">◀</button><button id="bj">▲</button><button id="bd">▼</button><button id="brt">▶</button></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const $=id=>document.getElementById(id);
let NAME='', best=0;
try{NAME=localStorage.getItem('runner_name')||''}catch(e){}
function view(v){['vMain','vGuide','vName'].forEach(i=>$(i).style.display=(i===v?'block':'none'));}
function setName(n){NAME=n; $('n').textContent=n||'?'; best=0; try{localStorage.setItem('runner_name',n);best=+localStorage.getItem('best_'+n)||0}catch(e){}
  $('best').textContent='🏆 Điểm cao: '+best; $('res').innerHTML=n?'Chào <b>'+n+'</b>!':'';}
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
  coin:()=>{tn(988,988,.08,'square',.06,3000); setTimeout(()=>tn(1319,1319,.16,'square',.06,3000),70)},
  jump:()=>{tn(250,600,.18,'sine',.12,900); nz(.14,.16,1200,1,.02)},
  bark:()=>{bark1(1); setTimeout(()=>bark1(.9),210); setTimeout(()=>bark1(.8),420)},
  growl:()=>{ if(muted||!AC)return; const T=AC.currentTime,o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),
      g=AC.createGain(),f=AC.createBiquadFilter(); o.type='sawtooth'; o.frequency.value=78; l.frequency.value=26; lg.gain.value=.12;
      f.type='lowpass'; f.frequency.value=380; g.gain.setValueAtTime(.16,T); g.gain.linearRampToValueAtTime(.001,T+.9);
      l.connect(lg); lg.connect(g.gain); o.connect(f); f.connect(g); g.connect(AC.destination); o.start();l.start();o.stop(T+.9);l.stop(T+.9); },
  pant:()=>{[0,.13,.26,.39].forEach(t=>setTimeout(()=>nz(.1,.13,3200,2,.012),t*1000))},
  chomp:()=>{nz(.09,.32,650,2,.004); tn(190,90,.09,'square',.09,500); setTimeout(()=>{nz(.09,.28,700,2,.004);tn(170,80,.09,'square',.08,500)},130)},
  breath:()=>{nz(.34,.16,1700,.8,.2); setTimeout(()=>nz(.4,.19,1200,.7,.06),330)},
  step:()=>nz(.07,.3+Math.random()*.1,300+Math.random()*250,1,.005),
  swoosh:()=>nz(.25,.2,1800,1,.08),
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
const notes=[262,294,330,392,330,294,262,220]; let stp=0;
function music(on){clearInterval(musicT); if(on)musicT=setInterval(()=>{tn(notes[stp%8],notes[stp%8],.2,'triangle',.04,1500); if(stp%2==0)tn(65,60,.15,'sine',.07,300); stp++;},280);}
$('mute').onclick=()=>{muted=!muted;$('mute').textContent=muted?'🔇':'🔊'};

/* ================= CẢNH LÀNG QUÊ ================= */
function canvasTex(w,h,draw,rx,ry){
  const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h);
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; if(rx)t.repeat.set(rx,ry); return t;
}
const L=c=>new THREE.MeshLambertMaterial({color:c,flatShading:true});
const sky=canvasTex(1024,512,(x,w,h)=>{
  const g=x.createLinearGradient(0,0,0,h); g.addColorStop(0,'#3d8fe0'); g.addColorStop(.6,'#8fd0ff'); g.addColorStop(1,'#eaf7ff');
  x.fillStyle=g; x.fillRect(0,0,w,h);
  const rg=x.createRadialGradient(w*.78,h*.22,0,w*.78,h*.22,120);
  rg.addColorStop(0,'rgba(255,255,235,1)'); rg.addColorStop(.25,'rgba(255,240,170,.9)'); rg.addColorStop(1,'rgba(255,240,170,0)');
  x.fillStyle=rg; x.fillRect(0,0,w,h);
  for(let i=0;i<12;i++){const cx=Math.random()*w,cy=50+Math.random()*h*.4;
    for(let k=0;k<7;k++){const px=cx+(k-3)*26+Math.random()*10,py=cy+Math.random()*16-8,r=24+Math.random()*22;
      const rr=x.createRadialGradient(px,py,0,px,py,r); rr.addColorStop(0,'rgba(255,255,255,.95)'); rr.addColorStop(1,'rgba(255,255,255,0)');
      x.fillStyle=rr; x.fillRect(px-r,py-r,r*2,r*2);}}
});
const scene=new THREE.Scene(); scene.background=sky; scene.fog=new THREE.Fog(0xdcefff,30,140);
const cam=new THREE.PerspectiveCamera(72,W()/H(),.1,220);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(W(),H()); wrap.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x9ccc65,1.05));
const sunL=new THREE.DirectionalLight(0xfff2cc,.9); sunL.position.set(8,14,4); scene.add(sunL);

// đường làng bằng đất
const roadTex=canvasTex(256,256,(x,w,h)=>{
  x.fillStyle='#b58b5a'; x.fillRect(0,0,w,h);
  for(let i=0;i<6000;i++){const v=Math.random()<.5?'#a37a4c':'#c79b6a';x.fillStyle=v;x.fillRect(Math.random()*w,Math.random()*h,2+Math.random()*2,2);}
  for(let i=0;i<60;i++){x.fillStyle='#8d6a44';x.beginPath();x.arc(Math.random()*w,Math.random()*h,1+Math.random()*3,0,7);x.fill();}
  x.fillStyle='rgba(120,85,50,.35)'; for(const f of [.15,.22,.47,.53,.78,.85])x.fillRect(w*f-3,0,6,h);
  x.fillStyle='rgba(255,255,255,.35)'; x.fillRect(w*.375-2,0,4,h*.4); x.fillRect(w*.625-2,0,4,h*.4);
  x.fillStyle='#7cb342'; x.fillRect(0,0,9,h); x.fillRect(w-9,0,9,h);
},1,25);
const road=new THREE.Mesh(new THREE.PlaneGeometry(8,240),new THREE.MeshLambertMaterial({map:roadTex}));
road.rotation.x=-Math.PI/2; road.position.z=-110; scene.add(road);
// ruộng lúa
const riceTex=canvasTex(128,128,(x,w,h)=>{
  x.fillStyle='#7cc043'; x.fillRect(0,0,w,h);
  for(let c=0;c<16;c++){x.fillStyle=c%2?'#8fd14f':'#5fa832';x.fillRect(c*8,0,5,h);}
  for(let i=0;i<900;i++){x.fillStyle=Math.random()<.5?'#c8e26a':'#3f8a24';x.fillRect(Math.random()*w,Math.random()*h,1,4);}
  x.fillStyle='#8ecdea'; x.fillRect(8,84,50,22); x.fillStyle='#b9e3f5'; x.fillRect(12,88,18,4);
  x.fillStyle='#c9b37a'; x.fillRect(0,124,w,4);
},36,30);
const field=new THREE.Mesh(new THREE.PlaneGeometry(300,240),new THREE.MeshLambertMaterial({map:riceTex}));
field.rotation.x=-Math.PI/2; field.position.set(0,-.05,-110); scene.add(field);
// núi xa
const mts=new THREE.MeshLambertMaterial({color:0x7fa9c0,flatShading:true,fog:true});
for(let i=0;i<9;i++){const m=new THREE.Mesh(new THREE.ConeGeometry(22+Math.random()*14,16+Math.random()*14,6),mts);
  m.position.set(-110+i*28,7,-125-Math.random()*10); scene.add(m);}

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
const kinds=[palm,house,haystack,bamboo,scarecrow,palm];
for(let i=0;i<12;i++)for(const sx of [-1,1]){const k=kinds[(i*2+(sx>0?1:0)+Math.floor(Math.random()*2))%6];
  addDeco(k(),sx*(k===house?11+Math.random()*3:k===palm?6+Math.random()*2:7+Math.random()*4),-i*10-(sx>0?5:0));}
const clouds=[];
for(let i=0;i<7;i++){const g=new THREE.Group(),m=new THREE.MeshBasicMaterial({color:0xffffff,fog:false});
  for(let k=0;k<5;k++){const s=new THREE.Mesh(new THREE.SphereGeometry(3+Math.random()*2,8,6),m);s.position.set(k*3.5-7,Math.random()*1.5,Math.random()*2);s.scale.y=.6;g.add(s);}
  g.position.set(-60+Math.random()*120,22+Math.random()*10,-80-Math.random()*30); scene.add(g); clouds.push(g);}
function shadow(){const s=new THREE.Mesh(new THREE.CircleGeometry(.6,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.28}));
  s.rotation.x=-Math.PI/2; s.position.y=.04; s.scale.y=1.6; return s;}

/* ================= NHÂN VẬT LOW-POLY ================= */
const skin=L(0x3a2216), player=new THREE.Group(), lim={};
function limb(w,h,d,mat,x,y,hand,shoe){const p=new THREE.Group();p.position.set(x,y,0);
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.y=-h/2;p.add(m);
  if(hand){const hd=new THREE.Mesh(new THREE.IcosahedronGeometry(.13,0),skin);hd.position.y=-h-.02;p.add(hd);}
  if(shoe){const s=bx(.32,.16,.48,0xffffff,0,-h-.05,-.06);p.add(s);p.add(bx(.34,.05,.5,0xe53935,0,-h-.14,-.06));}
  player.add(p);return p;}
player.add(bx(.85,.9,.5,0xff7043,0,1.2,0));                 // áo hoodie
player.add(bx(.86,.12,.52,0xffffff,0,.8,0));                // viền áo
player.add(bx(.55,.6,.25,0x1e88e5,0,1.25,.36));             // ba lô
player.add(bx(.5,.18,.1,0x1565c0,0,1.4,.5));
const hoodie=new THREE.Mesh(new THREE.SphereGeometry(.25,6,5),L(0xff7043)); hoodie.position.set(0,1.62,.12); player.add(hoodie);
const head=new THREE.Mesh(new THREE.SphereGeometry(.34,8,6),skin); head.position.y=1.9; player.add(head);
for(const x of [-.34,.34]){const e=new THREE.Mesh(new THREE.SphereGeometry(.09,5,4),skin);e.position.set(x,1.88,0);player.add(e);}
const nose=new THREE.Mesh(new THREE.ConeGeometry(.07,.13,4),skin); nose.rotation.x=-1.5; nose.position.set(0,1.86,-.36); player.add(nose);
player.add(bx(.52,.11,.06,0x000000,0,1.93,-.31));            // kính đen
for(let i=0;i<16;i++){const h=new THREE.Mesh(new THREE.IcosahedronGeometry(.13,0),L(0x0a0a0a));
  const a=Math.random()*6.28,e=Math.random()*1.1; h.position.set(Math.cos(a)*.27*Math.cos(e),2.02+Math.sin(e)*.27,Math.sin(a)*.27*Math.cos(e)); player.add(h);}
player.add(bx(.7,.1,.7,0xfdd835,0,2.05,0));                  // băng đô vàng
lim.armL=limb(.22,.75,.24,L(0xff7043),-.56,1.55,true); lim.armR=limb(.22,.75,.24,L(0xff7043),.56,1.55,true);
lim.legL=limb(.3,.75,.3,L(0x263238),-.21,.8,false,true); lim.legR=limb(.3,.75,.3,L(0x263238),.21,.8,false,true);
player.add(shadow()); scene.add(player);

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
const LANES=[-2,0,2], SPD0=.15, SPDMAX=.36;
let lane=1,y=0,vy=0,speed=SPD0,score=0,coins=0,alive=false,items=[],timer=0,gap=4,shake=0,t=0,jaw=0,
    duckT=0,dying=0,stepS=0,breathT=0,pantT=0,barkT=200,growlT=150,poolS=0;
function box(w,h,d,c,x,y,z){return bx(w,h,d,c,x,y,z);}
function wheel(r,x,y,z){const w=cyl(r,r,.2,0x212121,x,y,z,10);w.rotation.z=Math.PI/2;return w;}
function mk(type,l,zo){
  const g=new THREE.Group(); let hz=.6;
  if(type==='fence'){for(const x of [-.8,0,.8])g.add(box(.12,.9,.12,0x8d6e63,x,.45,0)); g.add(box(1.8,.12,.08,0xa1785c,0,.35,0)); g.add(box(1.8,.12,.08,0xa1785c,0,.68,0)); hz=.3;}
  else if(type==='buffalo'){g.add(box(1,.85,1.7,0x455a64,0,1.05,0)); g.add(box(.9,.5,.4,0x37474f,0,1.1,-.9));
    for(const [x,z] of [[-.3,-.6],[.3,-.6],[-.3,.6],[.3,.6]])g.add(cyl(.11,.13,.75,0x37474f,x,.38,z,6));
    g.add(box(.5,.5,.55,0x455a64,0,1.15,-1.2)); g.add(box(.4,.25,.25,0x90a4ae,0,1.02,-1.5));
    for(const x of [-.4,.4]){const h=box(.5,.08,.08,0xf5f5dc,x,1.5,-1.15);h.rotation.z=x>0?.5:-.5;g.add(h);g.add(box(.08,.08,.08,0xff1744,x*.4,1.28,-1.45));}
    g.add(box(.08,.6,.08,0x37474f,0,1.0,.95)); hz=1.1;}
  else if(type==='truck'){g.add(box(1.7,.3,3.6,0x455a64,0,.6,0)); g.add(box(1.7,1.1,2.3,0x8d6e63,0,1.3,.6));
    for(let i=0;i<4;i++)g.add(box(.7,.45,.6,0xf5f0dc,i%2?.42:-.42,2.05,i<2?.1:1.1));
    g.add(box(1.6,1.3,1.1,0x2e7d32,0,1.25,-1.4)); g.add(box(1.4,.5,.06,0x81d4fa,0,1.6,-1.96));
    g.add(box(.3,.15,.06,0xfff59d,-.5,.85,-1.82)); g.add(box(.3,.15,.06,0xfff59d,.5,.85,-1.82));
    for(const z of [-1.4,.4,1.4])for(const x of [-.85,.85])g.add(wheel(.36,x,.36,z)); g.add(box(1.72,.12,2.3,0xd32f2f,0,.85,.6)); hz=2.4;}
  else if(type==='haycart'){g.add(box(1.6,.25,2.4,0x8d6e63,0,.6,0)); g.add(box(1.5,1.2,2.2,0xe6c35c,0,1.3,0)); g.add(box(1.3,.4,1.8,0xd9b04a,0,2.0,0));
    g.add(wheel(.45,-.85,.45,.3)); g.add(wheel(.45,.85,.45,.3)); g.add(box(.1,.1,1.5,0x6d4c41,0,.55,-1.7)); hz=1.3;}
  else if(type==='pit'){const m=new THREE.Mesh(new THREE.PlaneGeometry(2.4,3),new THREE.MeshLambertMaterial({color:0x4fc3f7,emissive:0x0277bd}));m.rotation.x=-Math.PI/2;m.position.y=.03;g.add(m);
    g.add(box(2.4,.1,.3,0x795548,0,.06,-1.6)); g.add(box(2.4,.1,.3,0x795548,0,.06,1.6)); hz=1.5;}
  else if(type==='gate'){for(const x of [-1.1,1.1])g.add(cyl(.09,.11,1.9,0x9ccc65,x,.95,0,6)); const beam=cyl(.09,.09,2.4,0x7cb342,0,1.85,0,6); beam.rotation.z=Math.PI/2; g.add(beam); g.add(box(1.4,.35,.04,0xd32f2f,0,1.6,0)); hz=.4;}
  else{const m=new THREE.Mesh(new THREE.CylinderGeometry(.4,.4,.1,14),new THREE.MeshLambertMaterial({color:0xffd600,emissive:0x8a6d00}));m.rotation.x=Math.PI/2;m.position.y=1.1;g.add(m);}
  g.position.set(LANES[l],0,-80-(zo||0)); scene.add(g); items.push({m:g,type,hz});
}
const OB=['fence','buffalo','truck','haycart','pit','gate'];
function spawn(){
  const lv=Math.min(1,(speed-SPD0)/(SPDMAX-SPD0)), l=Math.floor(Math.random()*3);
  if(Math.random()<.3){for(let i=0;i<4;i++)mk('coin',l,i*2.5);return;}
  mk(OB[Math.floor(Math.random()*6)],l);
  if(Math.random()<.08+lv*.3)mk(OB[Math.floor(Math.random()*6)],(l+1+Math.floor(Math.random()*2))%3);
}
function reset(){
  items.forEach(o=>scene.remove(o.m)); items=[];
  lane=1;y=0;vy=0;speed=SPD0;score=0;coins=0;timer=0;gap=4;shake=0;duckT=0;dying=0;alive=true;
  player.position.set(0,0,0);player.rotation.set(0,0,0);player.scale.y=1;dog.position.set(0,0,4);dog.rotation.y=0;mouthBone.visible=false;
  drops.forEach(d=>d.m.visible=false); pool.visible=false; boneFly.visible=false; $('blood').style.opacity=0;
}
function end(type){
  alive=false; dying=140; music(false);
  if(type==='pit')sfx.splash(); else sfx.crash();
  sfx.scream(); sfx.growl(); sfx.bark();
}
function bloodBurst(){
  drops.forEach(d=>{d.m.position.set(player.position.x,.6+Math.random()*.8,.2); d.vx=(Math.random()-.5)*.14; d.vy=.06+Math.random()*.12; d.vz=(Math.random()-.3)*.14; d.m.visible=true;});
  pool.position.set(player.position.x,.05,.2); pool.visible=true; poolS=0; $('blood').style.opacity=.85;
}
function showOver(){
  if(score>best){best=Math.floor(score);try{localStorage.setItem('best_'+NAME,best)}catch(e){}}
  $('res').innerHTML='🐕 Chó cắn rồi!<br><b style="color:#e65100;font-size:24px">'+NAME+' gà quá! 🐔</b><br><small>Điểm: '+Math.floor(score)+' | Xu: '+coins+'</small>';
  $('best').textContent='🏆 Điểm cao: '+best; $('go').textContent='↻ CHƠI LẠI'; view('vMain'); $('msg').style.display='flex'; sfx.over();
}
const left=()=>{if(alive&&lane>0)lane--}, right=()=>{if(alive&&lane<2)lane++};
const jump=()=>{if(alive&&y===0){vy=.34;sfx.jump();}};
const duck=()=>{if(!alive)return; if(y>0)vy=-.4; else if(duckT===0){duckT=45;sfx.swoosh();}};
addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'){if(e.key==='Enter')$('ok').click();return;}
  if(e.key==='ArrowLeft'||e.key==='a')left();
  if(e.key==='ArrowRight'||e.key==='d')right();
  if(['ArrowUp',' ','w'].includes(e.key)){e.preventDefault();jump();}
  if(e.key==='ArrowDown'||e.key==='s'){e.preventDefault();duck();}
});
$('bl').onclick=left; $('brt').onclick=right; $('bj').onclick=jump; $('bd').onclick=duck;
let tx,ty;
wrap.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;});
wrap.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx,dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)){if(dx>30)right();else if(dx<-30)left();} else if(dy<-30)jump(); else if(dy>30)duck();});
$('go').onclick=()=>{if(!NAME){view('vName');return;} ac(); if(AC.state==='suspended')AC.resume(); $('msg').style.display='none'; reset(); music(true); window.focus();};

function loop(){
  requestAnimationFrame(loop); t+=.016;
  const mv=alive?speed:(dying>0?0:.09);
  if(dying>0){
    const k=140-dying; dying--; shake=k>25?5:0;
    if(k<25){dog.position.z+=(.4-dog.position.z)*.2; dog.position.x+=(player.position.x-dog.position.x)*.2; dog.position.y=Math.sin(k/25*Math.PI)*.9; jaw=.7;}
    else{ dog.position.set(player.position.x,.1+Math.abs(Math.sin(k*.6))*.12,.4); dog.rotation.y=Math.sin(k*1.2)*.3; jaw=Math.sin(k*1.5)>0?.6:.05;
      player.rotation.x+=(-1.45-player.rotation.x)*.12; player.position.y=.18; player.scale.y=1; }
    if(k===25){bloodBurst(); sfx.bite(); sfx.scream(); sfx.growl();}
    if(k===45){boneFly.position.set(player.position.x,.6,.2); boneFly.visible=true; bfv=.16; sfx.crash();}
    if(k>45&&k<70&&boneFly.visible){boneFly.position.y+=bfv; bfv-=.012; boneFly.position.z-=.02; boneFly.rotation.z+=.3;}
    if(k===70){boneFly.visible=false; mouthBone.visible=true; sfx.bark();}
    if(k>75&&k%16===0)sfx.chomp();
    if(k>25&&poolS<1.6){poolS+=.03; pool.scale.set(poolS,poolS*1.3,1);}
    if(dying===0)showOver();
  } else if(alive){
    speed=Math.min(SPDMAX,speed+.00003); score+=speed*.25; timer++;
    if(timer%Math.max(26,Math.floor(66-(speed-SPD0)*150))===0)spawn();
    player.position.x+=(LANES[lane]-player.position.x)*.2; player.rotation.z=(player.position.x-LANES[lane])*.18;
    vy-=.02; y=Math.max(0,y+vy); if(y===0)vy=0; player.position.y=y;
    if(duckT>0)duckT--;
    player.scale.y+=((duckT>0&&y===0?.5:1)-player.scale.y)*.4;
    const gT=3.5+Math.sin(t*1.5)*.35; gap+=(gT-gap)*.03;
    dog.position.z=gap; dog.position.x+=(player.position.x-dog.position.x)*.1; tail.rotation.z=Math.sin(t*18)*.5;
    breathT++; if(breathT>=Math.max(42,Math.floor(80-(speed-SPD0)*220))){breathT=0;sfx.breath();}
    pantT++; if(pantT>=60){pantT=0;sfx.pant();}
    if(--barkT<=0){barkT=200+Math.random()*220;sfx.bark();}
    if(--growlT<=0){growlT=260+Math.random()*200;sfx.growl();}
    for(let i=items.length-1;i>=0;i--){
      const o=items[i]; o.m.position.z+=speed*2;
      if(o.type==='coin')o.m.rotation.y+=.1;
      const dz=Math.abs(o.m.position.z-player.position.z),dx=Math.abs(o.m.position.x-player.position.x);
      if(dz<o.hz+.4&&dx<.9){
        if(o.type==='coin'){coins++;score+=2;sfx.coin();scene.remove(o.m);items.splice(i,1);continue;}
        const bad=o.type==='fence'?y<.7:o.type==='buffalo'?y<1.7:o.type==='haycart'?y<2.1:o.type==='truck'?true:o.type==='pit'?y<.35:(duckT===0||y>0);
        if(bad){end(o.type);break;}
      }
      if(o.m.position.z>10){scene.remove(o.m);items.splice(i,1);}
    }
    $('s').textContent=Math.floor(score); $('c').textContent=coins; $('lv').textContent=Math.floor((speed-SPD0)/.03)+1;
  }
  const cyc=t*(9+mv*12), air=y>0&&alive;
  if(dying===0){
    lim.legL.rotation.x=air?.5:Math.sin(cyc)*.9; lim.legR.rotation.x=air?-.5:-Math.sin(cyc)*.9;
    lim.armL.rotation.x=air?-2.5:-Math.sin(cyc)*.9; lim.armR.rotation.x=air?-2.5:Math.sin(cyc)*.9;
    dl.forEach((q,i)=>q.rotation.x=Math.sin(cyc*1.3+(i%2?Math.PI:0))*.9);
    if(!alive)dog.position.set(0,Math.abs(Math.sin(cyc*1.3))*.1,3.6); else dog.position.y=Math.abs(Math.sin(cyc*1.3))*.12;
    if(alive){const sg=Math.sign(Math.sin(cyc)); if(sg!==stepS&&y===0&&duckT===0){stepS=sg;sfx.step();}}
    jaw*=.86;
  }
  jawG.rotation.x=-jaw;
  drops.forEach(d=>{if(!d.m.visible)return; d.vy-=.006; d.m.position.x+=d.vx; d.m.position.y+=d.vy; d.m.position.z+=d.vz;
    if(d.m.position.y<.06){d.m.position.y=.06;d.vx=d.vy=d.vz=0;}});
  roadTex.offset.y+=mv*2/8; riceTex.offset.y+=mv*2/8;
  deco.forEach(d=>{d.position.z+=mv*2; if(d.position.z>8)d.position.z-=120;});
  clouds.forEach(c=>{c.position.x+=.03; if(c.position.x>80)c.position.x=-80;});
  const sh=shake>0?(shake--,(Math.random()-.5)*.3):0;
  cam.position.set(player.position.x*.4+sh,3.6+sh,6.5); cam.lookAt(player.position.x*.2,1.2,-6);
  renderer.render(scene,cam);
}
loop();
addEventListener('resize',()=>{renderer.setSize(W(),H());cam.aspect=W()/H();cam.updateProjectionMatrix();});
</script>
"""

components.html(GAME_HTML, height=680, scrolling=False)
