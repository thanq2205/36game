import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Runner", page_icon="🏃", layout="wide")
st.title("🏃 3D Runner: Chạy trốn chó dữ")
st.caption("Bấm vào khung game trước. ← → đổi làn, ↑/Space nhảy, ↓/S cúi/trượt. Điện thoại: vuốt hoặc dùng nút.")

name = st.text_input("Nhập username trước khi chơi", max_chars=16, placeholder="VD: Speedy123")

GAME_HTML = r"""
<style>
  html,body{margin:0;background:#111;overflow:hidden;font-family:sans-serif}
  #wrap{position:relative;width:100%;height:660px}
  canvas{display:block;width:100%;height:100%}
  #hud{position:absolute;top:8px;left:12px;color:#fff;font-size:18px;text-shadow:0 0 4px #000}
  #msg{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
       justify-content:center;color:#fff;background:rgba(0,0,0,.6);font-size:24px;text-align:center}
  button{font-size:18px;padding:8px 18px;margin:4px;border-radius:8px;border:0;cursor:pointer}
  #pad{position:absolute;bottom:8px;width:100%;display:flex;justify-content:center;gap:8px}
  #pad button{opacity:.55}
  #blood{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .3s;background:radial-gradient(transparent 35%,rgba(200,0,0,.85))}
  #mute{position:absolute;top:6px;right:8px;opacity:.7;padding:4px 10px}
  #danger{position:absolute;top:34px;left:12px;color:#ff5252;font-size:14px;text-shadow:0 0 4px #000}
</style>
<div id="wrap">
  <div id="hud">👤 <span id="n"></span> | Điểm: <span id="s">0</span> | Xu: <span id="c">0</span> | Cấp: <span id="lv">1</span></div><div id="blood"></div>
  <div id="danger"></div>
  <button id="mute">🔊</button>
  <div id="msg"><div id="t"></div><button id="go">▶ Chơi</button></div>
  <div id="pad"><button id="bl">◀</button><button id="bj">▲</button><button id="bd">▼</button><button id="br">▶</button></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const NAME=__NAME__;
document.getElementById('n').textContent=NAME;
document.getElementById('t').innerHTML='Chào <b>'+NAME+'</b>!<br>Chạy đi, chó đang đuổi 🐕';
const $=id=>document.getElementById(id);
const wrap=$('wrap'), W=()=>wrap.clientWidth, H=()=>wrap.clientHeight;

/* ---------- ÂM THANH (WebAudio tự tạo) ---------- */
let AC=null, muted=false, musicT=null;
function ac(){ if(!AC) AC=new (window.AudioContext||window.webkitAudioContext)(); return AC; }
function tone(f1,f2,d,type,vol){
  if(muted||!AC) return;
  const o=AC.createOscillator(), g=AC.createGain();
  o.type=type; o.frequency.setValueAtTime(f1,AC.currentTime);
  o.frequency.exponentialRampToValueAtTime(Math.max(f2,1),AC.currentTime+d);
  g.gain.setValueAtTime(vol,AC.currentTime); g.gain.exponentialRampToValueAtTime(0.001,AC.currentTime+d);
  o.connect(g); g.connect(AC.destination); o.start(); o.stop(AC.currentTime+d);
}
function noise(d,vol,freq){
  if(muted||!AC) return;
  const b=AC.createBuffer(1,AC.sampleRate*d,AC.sampleRate), a=b.getChannelData(0);
  for(let i=0;i<a.length;i++) a[i]=(Math.random()*2-1)*(1-i/a.length);
  const s=AC.createBufferSource(); s.buffer=b;
  const f=AC.createBiquadFilter(); f.type='lowpass'; f.frequency.value=freq;
  const g=AC.createGain(); g.gain.value=vol;
  s.connect(f); f.connect(g); g.connect(AC.destination); s.start();
}
const sfx={
  coin:()=>tone(880,1500,.12,'square',.07),
  jump:()=>tone(250,600,.18,'sine',.15),
  crash:()=>{noise(.4,.6,700);tone(140,35,.4,'sawtooth',.25)},
  splash:()=>noise(.5,.4,3500),
  bark:()=>{tone(420,160,.12,'sawtooth',.18); setTimeout(()=>tone(400,140,.12,'sawtooth',.18),160)},
  growl:()=>tone(80,55,.5,'sawtooth',.12),
  ah:()=>tone(700,450,.3,'sawtooth',.1),
  scream:()=>{
    if(muted||!AC) return;
    const o=AC.createOscillator(),l=AC.createOscillator(),lg=AC.createGain(),g=AC.createGain();
    o.type='sawtooth'; o.frequency.value=780; l.frequency.value=9; lg.gain.value=60;
    l.connect(lg); lg.connect(o.frequency);
    g.gain.setValueAtTime(.16,AC.currentTime); g.gain.exponentialRampToValueAtTime(.001,AC.currentTime+.9);
    o.connect(g); g.connect(AC.destination); o.start(); l.start(); o.stop(AC.currentTime+.9); l.stop(AC.currentTime+.9);
  },
  bite:()=>{noise(.15,.6,2000); tone(200,60,.2,'square',.15)},
  step:()=>noise(.06,.18,700),
  breath:()=>noise(.3,.07,2200),
  swoosh:()=>noise(.25,.2,1800),
  thunder:()=>noise(1.6,.8,300),
  over:()=>tone(400,60,1,'triangle',.25)
};
const scale=[110,130.8,146.8,164.8,196,164.8,146.8,130.8];
let step=0;
function music(on){
  clearInterval(musicT);
  if(on) musicT=setInterval(()=>{ tone(scale[step%8],scale[step%8]*.98,.22,'square',.035);
    if(step%2==0) tone(55,50,.15,'sine',.12); step++; },230);
}
$('mute').onclick=()=>{muted=!muted;$('mute').textContent=muted?'🔇':'🔊';};

/* ---------- CẢNH + BẦU TRỜI MÂY ĐEN ---------- */
function canvasTex(w,h,draw,rx,ry){
  const c=document.createElement('canvas'); c.width=w; c.height=h; draw(c.getContext('2d'),w,h);
  const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping;
  if(rx) t.repeat.set(rx,ry); return t;
}
const sky=canvasTex(512,256,(x,w,h)=>{
  const g=x.createLinearGradient(0,0,0,h); g.addColorStop(0,'#14171c'); g.addColorStop(1,'#5b616b');
  x.fillStyle=g; x.fillRect(0,0,w,h);
  for(let i=0;i<90;i++){
    const px=Math.random()*w, py=Math.random()*h*.8, r=30+Math.random()*60;
    const rg=x.createRadialGradient(px,py,0,px,py,r);
    const dark=Math.random()<.6;
    rg.addColorStop(0,dark?'rgba(20,22,26,.55)':'rgba(140,146,156,.35)'); rg.addColorStop(1,'rgba(0,0,0,0)');
    x.fillStyle=rg; x.fillRect(px-r,py-r,r*2,r*2);
  }
});
const scene=new THREE.Scene();
scene.background=sky;
scene.fog=new THREE.Fog(0x4a4f57,12,65);
const cam=new THREE.PerspectiveCamera(70,W()/H(),0.1,100);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W(),H()); wrap.prepend(renderer.domElement);
const hemi=new THREE.HemisphereLight(0x99a3b5,0x2a2a2a,.85); scene.add(hemi);
const sun=new THREE.DirectionalLight(0xbcc6d8,.5); sun.position.set(-5,10,6); scene.add(sun);

/* Đường nhựa có vạch kẻ */
const roadTex=canvasTex(256,256,(x,w,h)=>{
  x.fillStyle='#2b2b2e'; x.fillRect(0,0,w,h);
  for(let i=0;i<5000;i++){const v=30+Math.random()*30;x.fillStyle='rgb('+v+','+v+','+v+')';x.fillRect(Math.random()*w,Math.random()*h,2,2);}
  x.fillStyle='#e8e8e8'; x.fillRect(w*.375-3,0,6,h*.5); x.fillRect(w*.625-3,0,6,h*.5);
  x.fillStyle='#d4a017'; x.fillRect(4,0,6,h); x.fillRect(w-10,0,6,h);
},1,25);
const road=new THREE.Mesh(new THREE.PlaneGeometry(8,200),new THREE.MeshLambertMaterial({map:roadTex}));
road.rotation.x=-Math.PI/2; road.position.z=-90; scene.add(road);
const gTex=canvasTex(64,64,(x,w,h)=>{x.fillStyle='#2f3a2c';x.fillRect(0,0,w,h);
  for(let i=0;i<400;i++){x.fillStyle=Math.random()<.5?'#3a4836':'#25301f';x.fillRect(Math.random()*w,Math.random()*h,2,2);}},30,30);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.MeshLambertMaterial({map:gTex}));
ground.rotation.x=-Math.PI/2; ground.position.set(0,-.02,-80); scene.add(ground);

/* Toà nhà có cửa sổ phát sáng */
const bTex=canvasTex(128,256,(x,w,h)=>{
  x.fillStyle='#8a8f98'; x.fillRect(0,0,w,h);
  for(let r=0;r<10;r++)for(let c=0;c<4;c++){
    x.fillStyle=Math.random()<.35?'#ffd76a':'#1b1e24'; x.fillRect(10+c*29,10+r*24,18,14);
  }
});
const bld=[], tints=[0xb0b8c8,0xc8a890,0x9db0a0];
for(let i=0;i<20;i++)for(const sx of [-1,1]){
  const s=.7+Math.random()*.9;
  const b=new THREE.Mesh(new THREE.BoxGeometry(4,10,4),new THREE.MeshLambertMaterial({map:bTex,color:tints[i%3]}));
  b.scale.y=s; b.position.set(sx*(6.5+Math.random()*1.5),5*s,-i*6); scene.add(b); bld.push(b);
}

/* ---------- NHÂN VẬT (da đen, tóc xoăn, áo đỏ) ---------- */
const skin=new THREE.MeshLambertMaterial({color:0x3a2216});
const M=(c)=>new THREE.MeshLambertMaterial({color:c});
const player=new THREE.Group(), lim={};
function limb(w,h,d,mat,x,y){const p=new THREE.Group();p.position.set(x,y,0);
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat); m.position.y=-h/2; p.add(m); player.add(p); return p;}
const torso=new THREE.Mesh(new THREE.BoxGeometry(.8,.85,.45),M(0xd32f2f)); torso.position.y=1.15; player.add(torso);
const head=new THREE.Mesh(new THREE.SphereGeometry(.34,16,16),skin); head.position.y=1.85; player.add(head);
for(let i=0;i<14;i++){const h=new THREE.Mesh(new THREE.SphereGeometry(.13,8,8),M(0x0a0a0a));
  const a=Math.random()*Math.PI*2, e=Math.random()*1.1;
  h.position.set(Math.cos(a)*.27*Math.cos(e),1.95+Math.sin(e)*.28,Math.sin(a)*.27*Math.cos(e)); player.add(h);}
const shades=new THREE.Mesh(new THREE.BoxGeometry(.5,.1,.05),M(0x000000)); shades.position.set(0,1.88,-.32); player.add(shades);
lim.armL=limb(.22,.7,.22,skin,-.52,1.5); lim.armR=limb(.22,.7,.22,skin,.52,1.5);
lim.legL=limb(.28,.75,.28,M(0x1a237e),-.2,.75); lim.legR=limb(.28,.75,.28,M(0x1a237e),.2,.75);
for(const x of [-.2,.2]){const s=new THREE.Mesh(new THREE.BoxGeometry(.3,.12,.4),M(0xffffff));s.position.set(x,.06,-.05);player.add(s);}
scene.add(player);

/* ---------- CHÓ ĐUỔI ---------- */
const dog=new THREE.Group(), dm=M(0x6d4c2a), dl=[];
const dbody=new THREE.Mesh(new THREE.BoxGeometry(.6,.55,1.2),dm); dbody.position.y=.7; dog.add(dbody);
const dhead=new THREE.Mesh(new THREE.BoxGeometry(.45,.42,.5),dm); dhead.position.set(0,.95,-.75); dog.add(dhead);
const snout=new THREE.Mesh(new THREE.BoxGeometry(.25,.2,.3),M(0x3e2a15)); snout.position.set(0,.88,-1.1); dog.add(snout);
const nose=new THREE.Mesh(new THREE.BoxGeometry(.1,.08,.05),M(0)); nose.position.set(0,.95,-1.27); dog.add(nose);
for(const x of [-.17,.17]){const e=new THREE.Mesh(new THREE.BoxGeometry(.12,.28,.1),M(0x3e2a15));e.position.set(x,1.25,-.7);dog.add(e);
  const eye=new THREE.Mesh(new THREE.BoxGeometry(.07,.07,.03),M(0xff1744));eye.position.set(x,1.02,-1.01);dog.add(eye);}
const tail=new THREE.Mesh(new THREE.BoxGeometry(.1,.1,.5),dm); tail.position.set(0,.95,.75); tail.rotation.x=.6; dog.add(tail);
for(const [x,z] of [[-.2,-.4],[.2,-.4],[-.2,.4],[.2,.4]]){
  const p=new THREE.Group();p.position.set(x,.45,z);const l=new THREE.Mesh(new THREE.BoxGeometry(.13,.45,.13),dm);l.position.y=-.22;p.add(l);dog.add(p);dl.push(p);}
scene.add(dog);

/* ---------- LOGIC GAME ---------- */
const LANES=[-2,0,2];
let lane,y,vy,speed,score,coins,alive=false,items=[],timer,gap,inv,shake,flash=0,t=0,duckT=0,dying=0,stepS=0,breathT=0;
function reset(){
  items.forEach(o=>scene.remove(o.m)); items=[];
  lane=1;y=0;vy=0;speed=.25;score=0;coins=0;timer=0;gap=4;inv=0;shake=0;alive=true;duckT=0;dying=0;
  player.position.x=0;player.rotation.x=0;player.scale.y=1;player.visible=true;$('blood').style.opacity=0;dog.position.y=0;
}
const wood=canvasTex(64,64,(x,w,h)=>{x.fillStyle='#8d6e63';x.fillRect(0,0,w,h);x.fillStyle='#4e342e';
  for(let i=0;i<64;i+=16)x.fillRect(i,0,3,h);x.fillStyle='#3e2723';x.fillRect(0,14,w,5);x.fillRect(0,40,w,5);});
const coinM=new THREE.MeshLambertMaterial({color:0xffd600,emissive:0x8a6d00});
const carCols=[0xc62828,0x1565c0,0xf9a825,0x2e7d32,0xeeeeee];
function box(w,h,d,c,x,y,z){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshLambertMaterial({color:c}));m.position.set(x,y,z);return m;}
function mk(type,l){
  const g=new THREE.Group(); let hz=.6;
  if(type==='fence'){const m=new THREE.Mesh(new THREE.BoxGeometry(1.7,.75,.25),new THREE.MeshLambertMaterial({map:wood}));m.position.y=.4;g.add(m);hz=.3;}
  else if(type==='car'){
    g.add(box(1.6,.7,3.2,carCols[Math.floor(Math.random()*5)],0,.6,0)); g.add(box(1.3,.55,1.5,0x263238,0,1.2,.2));
    for(const [x,z] of [[-.8,-1],[.8,-1],[-.8,1],[.8,1]]){const w=new THREE.Mesh(new THREE.CylinderGeometry(.32,.32,.2,12),new THREE.MeshLambertMaterial({color:0x111111}));w.rotation.z=Math.PI/2;w.position.set(x,.32,z);g.add(w);}
    g.add(box(.3,.15,.05,0xfff59d,-.5,.65,-1.62)); g.add(box(.3,.15,.05,0xfff59d,.5,.65,-1.62)); hz=1.6;}
  else if(type==='pit'){const m=new THREE.Mesh(new THREE.PlaneGeometry(2.2,3),new THREE.MeshLambertMaterial({color:0x1e88e5,emissive:0x0a2a50}));m.rotation.x=-Math.PI/2;m.position.y=.03;g.add(m);hz=1.5;}
  else if(type==='pipe'){
    const c=new THREE.Mesh(new THREE.CylinderGeometry(.35,.35,2.2,16),new THREE.MeshLambertMaterial({color:0x78909c}));c.rotation.z=Math.PI/2;c.position.y=1.7;g.add(c);
    g.add(box(.2,1.7,.3,0x455a64,-1.05,.85,0)); g.add(box(.2,1.7,.3,0x455a64,1.05,.85,0)); hz=.4;}
  else{const m=new THREE.Mesh(new THREE.CylinderGeometry(.4,.4,.1,20),coinM);m.rotation.x=Math.PI/2;m.position.y=1.1;g.add(m);}
  g.position.set(LANES[l],0,-70); scene.add(g); items.push({m:g,type,hz});
}
function spawn(){
  const lv=Math.min(1,(speed-.25)/.3), r=Math.random(); let type;
  if(r<.22)type='coin'; else if(r<.42)type='fence'; else if(r<.62)type='car'; else if(r<.8)type='pit'; else type='pipe';
  const l=Math.floor(Math.random()*3); mk(type,l);
  if(type!=='coin'&&Math.random()<.15+lv*.35){mk(['fence','car','pit','pipe'][Math.floor(Math.random()*4)],(l+1+Math.floor(Math.random()*2))%3);}
}
function end(){
  alive=false; dying=90; music(false); sfx.scream(); sfx.bark();
  setTimeout(sfx.bite,350); setTimeout(sfx.scream,550); $('danger').textContent=''; $('blood').style.opacity=.8;
}
function showOver(){
  $('t').innerHTML='🐕 Chó cắn rồi!<br><b style="color:#ffca28">'+NAME+' gà quá! 🐔</b><br><small>Điểm: '+Math.floor(score)+' | Xu: '+coins+'</small>';
  $('go').textContent='↻ Chơi lại'; $('msg').style.display='flex'; sfx.over();
}
const left=()=>{if(alive&&lane>0)lane--}, right=()=>{if(alive&&lane<2)lane++};
const jump=()=>{if(alive&&y===0){vy=.34;sfx.jump();}};
const duck=()=>{if(!alive)return; if(y>0)vy=-.4; else if(duckT===0){duckT=45;sfx.swoosh();}};
addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='s'){e.preventDefault();duck();}});
addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='a')left();
  if(e.key==='ArrowRight'||e.key==='d')right();
  if(['ArrowUp',' ','w'].includes(e.key)){e.preventDefault();jump();}
});
$('bl').onclick=left; $('br').onclick=right; $('bj').onclick=jump; $('bd').onclick=duck;
let tx,ty;
wrap.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;});
wrap.addEventListener('touchend',e=>{
  const dx=e.changedTouches[0].clientX-tx, dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)){if(dx>30)right();else if(dx<-30)left();} else if(dy<-30)jump(); else if(dy>30)duck();
});
$('go').onclick=()=>{ac(); if(AC.state==='suspended')AC.resume(); $('msg').style.display='none'; reset(); music(true); window.focus();};

function hit(o){
  if(o.type==='pit')sfx.splash(); else sfx.crash();
  sfx.ah(); sfx.bark(); gap-=1.8; inv=80; shake=14;
  $('blood').style.opacity=.6; setTimeout(()=>{if(alive)$('blood').style.opacity=0},250);
  scene.remove(o.m); items.splice(items.indexOf(o),1);
  if(gap<=1.1) end();
}
function loop(){
  requestAnimationFrame(loop); t+=.016;
  if(Math.random()<.003){flash=7; if(alive) setTimeout(sfx.thunder,300);}
  hemi.intensity=flash>0?2.2:.85; if(flash>0)flash--;
  if(dying>0){
    dying--; shake=6;
    dog.position.z+=(.2-dog.position.z)*.15; dog.position.x+=(player.position.x-dog.position.x)*.2;
    dog.position.y=.4+Math.abs(Math.sin(dying*.5))*.35; dhead.rotation.x=Math.sin(dying*.8)*.3;
    player.rotation.x+=(-1.4-player.rotation.x)*.1; player.position.y=.15; player.visible=true; player.scale.y=1;
    if(dying===0) showOver();
  } else if(alive){
    speed=Math.min(.62,speed+.00006); score+=speed*.35; timer++;
    if(timer%Math.max(13,Math.floor(38-(speed-.25)*70))===0) spawn();
    player.position.x+=(LANES[lane]-player.position.x)*.22;
    vy-=.02; y=Math.max(0,y+vy); if(y===0)vy=0;
    player.position.y=y;
    if(duckT>0)duckT--;
    player.scale.y+=((duckT>0&&y===0?.5:1)-player.scale.y)*.4;
    const cyc=t*(10+speed*10), air=y>0;
    lim.legL.rotation.x=air?.5:Math.sin(cyc)*.9; lim.legR.rotation.x=air?-.5:-Math.sin(cyc)*.9;
    lim.armL.rotation.x=air?-2.5:-Math.sin(cyc)*.9; lim.armR.rotation.x=air?-2.5:Math.sin(cyc)*.9;
    const sg=Math.sign(Math.sin(cyc)); if(sg!==stepS&&y===0&&duckT===0){stepS=sg;sfx.step();}
    breathT++; if(breathT>=(gap<2.6?20:42)){breathT=0;sfx.breath();}
    if(gap<2.6&&timer%90===0)sfx.growl();
    if(inv>0){inv--; player.visible=inv%8<4;} else player.visible=true;
    if(gap<4) gap+=.003;
    dog.position.z=gap; dog.position.x+=(player.position.x-dog.position.x)*.1;
    dl.forEach((q,i)=>q.rotation.x=Math.sin(cyc*1.3+(i%2?Math.PI:0))*.9);
    dog.position.y=Math.abs(Math.sin(cyc*1.3))*.12; tail.rotation.z=Math.sin(t*20)*.5;
    $('danger').textContent=gap<2.6?'⚠️ CHÓ SẮP CẮN!':'';
    for(let i=items.length-1;i>=0;i--){
      const o=items[i]; o.m.position.z+=speed*2;
      if(o.type==='coin')o.m.rotation.y+=.1;
      const dz=Math.abs(o.m.position.z-player.position.z), dx=Math.abs(o.m.position.x-player.position.x);
      if(dz<o.hz+.4&&dx<.9){
        if(o.type==='coin'){coins++;sfx.coin();scene.remove(o.m);items.splice(i,1);continue;}
        if(inv===0){
          const bad=o.type==='fence'?y<.7:o.type==='car'?y<1.6:o.type==='pit'?y<.35:(duckT===0||y>0);
          if(bad){hit(o); if(dying>0)break; continue;}
        }
      }
      if(o.m.position.z>10){scene.remove(o.m);items.splice(i,1);}
    }
    roadTex.offset.y+=speed*2/8;
    bld.forEach(b=>{b.position.z+=speed*2;if(b.position.z>8)b.position.z-=120;});
    $('s').textContent=Math.floor(score); $('c').textContent=coins; $('lv').textContent=Math.floor((speed-.25)/.05)+1;
  }
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
