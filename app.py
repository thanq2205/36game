import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Runner", page_icon="🏃", layout="centered")
st.title("🏃 3D Runner (kiểu Subway Surfers)")
st.caption("Bấm vào khung game trước. ← → đổi làn, ↑ / Space nhảy. Trên điện thoại: vuốt hoặc dùng nút.")

GAME_HTML = """
<style>
  html,body{margin:0;background:#111;overflow:hidden;font-family:sans-serif}
  #wrap{position:relative;width:100%;height:560px}
  canvas{display:block;width:100%;height:100%}
  #hud{position:absolute;top:8px;left:12px;color:#fff;font-size:18px;text-shadow:0 0 4px #000}
  #msg{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
       justify-content:center;color:#fff;background:rgba(0,0,0,.55);font-size:22px;text-align:center}
  button{font-size:18px;padding:8px 18px;margin:4px;border-radius:8px;border:0;cursor:pointer}
  #pad{position:absolute;bottom:8px;width:100%;display:flex;justify-content:center;gap:8px}
  #pad button{opacity:.6}
</style>
<div id="wrap">
  <div id="hud">Điểm: <span id="s">0</span> | Xu: <span id="c">0</span></div>
  <div id="msg"><div id="t">3D Runner</div><button id="go">▶ Chơi</button></div>
  <div id="pad">
    <button id="bl">◀</button><button id="bj">▲</button><button id="br">▶</button>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const wrap=document.getElementById('wrap');
const W=()=>wrap.clientWidth, H=()=>wrap.clientHeight;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,15,60);
const cam=new THREE.PerspectiveCamera(70,W()/H(),0.1,100);
cam.position.set(0,3.5,6); cam.lookAt(0,1,-6);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W(),H()); wrap.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x444444,1));
const sun=new THREE.DirectionalLight(0xffffff,0.6); sun.position.set(5,10,5); scene.add(sun);

// Đường + vạch làn
const road=new THREE.Mesh(new THREE.PlaneGeometry(8,200),new THREE.MeshLambertMaterial({color:0x333333}));
road.rotation.x=-Math.PI/2; road.position.z=-90; scene.add(road);
const lines=[];
for(let i=0;i<30;i++){
  for(const x of [-1,1]){
    const l=new THREE.Mesh(new THREE.PlaneGeometry(0.1,2),new THREE.MeshBasicMaterial({color:0xffffff}));
    l.rotation.x=-Math.PI/2; l.position.set(x,0.01,-i*4); scene.add(l); lines.push(l);
  }
}
// Nhà hai bên
const bld=[];
for(let i=0;i<20;i++){
  for(const x of [-7,7]){
    const h=3+Math.random()*8;
    const b=new THREE.Mesh(new THREE.BoxGeometry(4,h,4),
      new THREE.MeshLambertMaterial({color:new THREE.Color().setHSL(Math.random(),0.4,0.5)}));
    b.position.set(x,h/2,-i*6); scene.add(b); bld.push(b);
  }
}
// Nhân vật
const player=new THREE.Mesh(new THREE.BoxGeometry(0.9,1.6,0.9),new THREE.MeshLambertMaterial({color:0xff5722}));
scene.add(player);

const LANES=[-2,0,2];
let lane=1,vy=0,y=0,speed,score,coins,alive=false,items=[],timer;

function reset(){
  items.forEach(o=>scene.remove(o.m)); items=[];
  lane=1;y=0;vy=0;speed=0.25;score=0;coins=0;timer=0;alive=true;
}
function spawn(){
  const l=Math.floor(Math.random()*3);
  if(Math.random()<0.6){
    const m=new THREE.Mesh(new THREE.BoxGeometry(1.4,1.2,1.2),new THREE.MeshLambertMaterial({color:0xd32f2f}));
    m.position.set(LANES[l],0.6,-70); scene.add(m); items.push({m,type:'ob',lane:l});
  }else{
    const m=new THREE.Mesh(new THREE.CylinderGeometry(0.4,0.4,0.1,16),new THREE.MeshLambertMaterial({color:0xffd600}));
    m.rotation.x=Math.PI/2; m.position.set(LANES[l],1,-70); scene.add(m); items.push({m,type:'coin',lane:l});
  }
}
function end(){
  alive=false;
  document.getElementById('t').innerHTML='Thua rồi! 💥<br>Điểm: '+Math.floor(score)+' | Xu: '+coins;
  document.getElementById('go').textContent='↻ Chơi lại';
  document.getElementById('msg').style.display='flex';
}
function left(){ if(alive&&lane>0)lane--; }
function right(){ if(alive&&lane<2)lane++; }
function jump(){ if(alive&&y===0)vy=0.32; }

addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='a')left();
  if(e.key==='ArrowRight'||e.key==='d')right();
  if(e.key==='ArrowUp'||e.key===' '||e.key==='w'){e.preventDefault();jump();}
});
bl.onclick=left; br.onclick=right; bj.onclick=jump;
let tx,ty;
wrap.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;ty=e.touches[0].clientY;});
wrap.addEventListener('touchend',e=>{
  const dx=e.changedTouches[0].clientX-tx, dy=e.changedTouches[0].clientY-ty;
  if(Math.abs(dx)>Math.abs(dy)){ if(dx>30)right(); else if(dx<-30)left(); }
  else if(dy<-30)jump();
});
document.getElementById('go').onclick=()=>{
  document.getElementById('msg').style.display='none'; reset(); window.focus();
};

function loop(){
  requestAnimationFrame(loop);
  if(alive){
    speed+=0.00008; score+=speed*2; timer++;
    if(timer%35===0)spawn();
    player.position.x+=(LANES[lane]-player.position.x)*0.2;
    vy-=0.02; y=Math.max(0,y+vy); if(y===0)vy=0;
    player.position.y=0.8+y;
    for(let i=items.length-1;i>=0;i--){
      const o=items[i]; o.m.position.z+=speed*2;
      if(o.type==='coin')o.m.rotation.z+=0.1;
      const dz=Math.abs(o.m.position.z-player.position.z);
      const dx=Math.abs(o.m.position.x-player.position.x);
      if(dz<0.9&&dx<0.9){
        if(o.type==='ob'&&y<1.0){end();}
        if(o.type==='coin'){coins++;scene.remove(o.m);items.splice(i,1);continue;}
      }
      if(o.m.position.z>10){scene.remove(o.m);items.splice(i,1);}
    }
    lines.forEach(l=>{l.position.z+=speed*2; if(l.position.z>6)l.position.z-=120;});
    bld.forEach(b=>{b.position.z+=speed*2; if(b.position.z>8)b.position.z-=120;});
    document.getElementById('s').textContent=Math.floor(score);
    document.getElementById('c').textContent=coins;
  }
  renderer.render(scene,cam);
}
loop();
addEventListener('resize',()=>{renderer.setSize(W(),H());cam.aspect=W()/H();cam.updateProjectionMatrix();});
</script>
"""

components.html(GAME_HTML, height=580, scrolling=False)
