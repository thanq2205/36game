import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Đua Xe", page_icon="🏎️", layout="centered")

st.title("🏎️ Đua Xe")

GAME_HTML = """
<div style="display:flex;flex-direction:column;align-items:center;font-family:sans-serif;">
  <div style="position:relative;display:inline-block;max-width:100%;">
    <canvas id="game" width="400" height="600" tabindex="0"
      style="display:block;background:#222;border:3px solid #444;border-radius:8px;max-width:100%;outline:none;touch-action:none;"></canvas>
    <div id="nameBox" style="position:absolute;left:0;right:0;top:36%;text-align:center;display:none;">
      <input id="uname" type="text" maxlength="14" placeholder="Tên của bạn" autocomplete="off"
        style="width:220px;padding:10px 12px;font-size:18px;border-radius:10px;border:3px solid #ffd54f;text-align:center;outline:none;">
      <div style="margin-top:14px;">
        <button id="btnGo" style="font-size:18px;font-weight:bold;padding:10px 28px;border-radius:10px;border:none;background:#e53935;color:#fff;cursor:pointer;">Vào game ▶</button>
      </div>
    </div>
  </div>
  <div style="margin-top:10px;display:flex;gap:12px;">
    <button id="btnL" style="font-size:24px;padding:10px 30px;border-radius:8px;">⬅️</button>
    <button id="btnM" style="font-size:24px;padding:10px 18px;border-radius:8px;">🔊</button>
    <button id="btnR" style="font-size:24px;padding:10px 30px;border-radius:8px;">➡️</button>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

const ROAD_X = 40, ROAD_W = 320, LANES = 4, LANE_W = ROAD_W / LANES;
const CAR_W = 40, CAR_H = 70;
const START_SPEED = 240, ACCEL = 16, MAX_SPEED = 1100;
const SCORE_DIV = 150, COIN_BONUS = 5;
const LANE_TIME = 0.22;
const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const COLORS = ['#e74c3c','#3498db','#f1c40f','#9b59b6','#1abc9c','#e67e22'];

// =====================================================================
//  ÂM THANH (WebAudio, tự tổng hợp - không cần file)
// =====================================================================
let AC = null, master, musicGain, sfxGain, engOsc, engGain, noiseBuf, muted = false;
const m2f = m => 440 * Math.pow(2, (m - 69) / 12);

function initAudio() {
  if (AC) { if (AC.state === 'suspended') AC.resume(); return; }
  try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; return; }
  master = AC.createGain(); master.gain.value = muted ? 0 : 0.8; master.connect(AC.destination);
  musicGain = AC.createGain(); musicGain.gain.value = 0.16; musicGain.connect(master);
  sfxGain = AC.createGain(); sfxGain.gain.value = 0.55; sfxGain.connect(master);

  noiseBuf = AC.createBuffer(1, AC.sampleRate, AC.sampleRate);
  const d = noiseBuf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

  // tiếng động cơ
  engOsc = AC.createOscillator(); engOsc.type = 'sawtooth'; engOsc.frequency.value = 60;
  const f = AC.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 420;
  engGain = AC.createGain(); engGain.gain.value = 0;
  engOsc.connect(f); f.connect(engGain); engGain.connect(sfxGain); engOsc.start();

  nextT = AC.currentTime + 0.1;
  setInterval(scheduler, 50);
}

function toneAt(f, d, type, vol, t, dest, slide) {
  const o = AC.createOscillator(), g = AC.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t);
  if (slide) o.frequency.exponentialRampToValueAtTime(slide, t + d);
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(dest); o.start(t); o.stop(t + d + 0.03);
}
function noiseAt(d, vol, f0, f1, ftype, t, dest) {
  const src = AC.createBufferSource(); src.buffer = noiseBuf;
  const fl = AC.createBiquadFilter(); fl.type = ftype;
  fl.frequency.setValueAtTime(f0, t); fl.frequency.exponentialRampToValueAtTime(f1, t + d);
  const g = AC.createGain();
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  src.connect(fl); fl.connect(g); g.connect(dest); src.start(t); src.stop(t + d + 0.03);
}

function sfxSwoosh() { if (!AC) return; noiseAt(0.2, 0.5, 500, 2200, 'bandpass', AC.currentTime, sfxGain); }
function sfxCoin() {
  if (!AC) return; const t = AC.currentTime;
  toneAt(988, 0.09, 'square', 0.25, t, sfxGain); toneAt(1319, 0.18, 'square', 0.25, t + 0.08, sfxGain);
}
function sfxCrash() {
  if (!AC) return; const t = AC.currentTime;
  noiseAt(0.8, 1.0, 3000, 80, 'lowpass', t, sfxGain);
  toneAt(140, 0.5, 'sawtooth', 0.8, t, sfxGain, 35);
  [392, 330, 262, 196].forEach((f, i) => toneAt(f, 0.28, 'triangle', 0.35, t + 0.55 + i * 0.27, sfxGain));
}
function sfxStart() {
  if (!AC) return; const t = AC.currentTime;
  [523, 659, 784].forEach((f, i) => toneAt(f, 0.12, 'square', 0.2, t + i * 0.09, sfxGain));
}

// nhạc nền: 4 hợp âm Am - F - C - G, tempo tăng dần theo tốc độ xe
const CHORDS = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]];
const BASS = [45, 41, 48, 43], ARP = [0, 1, 2, 1, 0, 1, 2, 1];
let nextT = 0, stepI = 0, stepD = 0.115;

function musicShouldPlay() { return scene !== 'over' && !(scene === 'play' && state.paused); }
function playStep(i, t) {
  const ci = Math.floor(i / 8) % 4, chord = CHORDS[ci], st = i % 8;
  if (st % 2 === 0) toneAt(m2f(BASS[ci] + (st % 4 === 2 ? 12 : 0)), stepD * 1.8, 'triangle', 0.6, t, musicGain);
  toneAt(m2f(chord[ARP[st]] + 12), stepD * 0.9, 'square', 0.2, t, musicGain);
  if (i % 4 === 0) toneAt(150, 0.12, 'sine', 0.7, t, musicGain, 50);
  if (i % 2 === 1) noiseAt(0.04, 0.12, 7000, 7000, 'highpass', t, musicGain);
}
function scheduler() {
  if (!AC || AC.state !== 'running') return;
  if (nextT < AC.currentTime - 0.3) nextT = AC.currentTime + 0.05;
  while (nextT < AC.currentTime + 0.25) {
    const bpm = scene === 'play' ? Math.min(190, 125 + (state.speed - START_SPEED) / 12) : 125;
    stepD = 60 / bpm / 4;
    if (musicShouldPlay()) playStep(stepI, nextT);
    stepI++; nextT += stepD;
  }
}
function audioTick() {
  if (!AC) return;
  const on = scene === 'play' && !state.paused;
  engGain.gain.setTargetAtTime(on ? 0.11 : 0, AC.currentTime, 0.08);
  if (on) engOsc.frequency.setTargetAtTime(55 + state.speed * 0.13, AC.currentTime, 0.1);
}

const btnM = document.getElementById('btnM');
btnM.addEventListener('click', () => {
  initAudio(); muted = !muted;
  if (master) master.gain.value = muted ? 0 : 0.8;
  btnM.textContent = muted ? '🔇' : '🔊';
  canvas.focus();
});
['pointerdown', 'keydown', 'touchstart'].forEach(ev => window.addEventListener(ev, initAudio));

// =====================================================================
//  ĐIỂM CAO + TÊN NGƯỜI CHƠI
// =====================================================================
const KEY = 'racing_scores_v2';
let memScores = [];
function loadScores() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return memScores; } }
function saveScores(list) { memScores = list; try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {} }
let scores = loadScores();
function addScore(s, coins) {
  const entry = { s, coins, n: getName(), d: new Date().toLocaleDateString('vi-VN') };
  scores.push(entry);
  scores.sort((a, b) => b.s - a.s);
  scores = scores.slice(0, 10);
  saveScores(scores);
  return scores.indexOf(entry);
}
const bestScore = () => scores.length ? scores[0].s : 0;

const nameInput = document.getElementById('uname');
const nameBox = document.getElementById('nameBox');
let username = '', nameErr = 0;
try { username = localStorage.getItem('racing_user') || ''; } catch (e) {}
const getName = () => username || 'Bạn';
function submitName() {
  const v = nameInput.value.trim().slice(0, 14);
  if (!v) { nameErr = 1.8; nameInput.focus(); return; }
  username = v;
  try { localStorage.setItem('racing_user', v); } catch (e) {}
  nameInput.blur(); canvas.focus();
  scene = 'menu';
}
document.getElementById('btnGo').addEventListener('click', submitName);

// =====================================================================
//  TRẠNG THÁI GAME
// =====================================================================
let scene = 'name';                  // name | menu | play | over | scores | help
let menuSel = 0, lastT = 0, buttons = [], prevScene = null;
let state, lastRank = -1;

const laneX = l => ROAD_X + l * LANE_W + (LANE_W - CAR_W) / 2;
function moveLane(d) {
  if (scene !== 'play' || state.paused) return;
  const nl = Math.max(0, Math.min(LANES - 1, state.lane + d));
  if (nl === state.lane) return;
  state.lane = nl;
  state.fromX = state.x; state.toX = laneX(nl); state.t = 0;
  sfxSwoosh();
}
function reset() {
  state = {
    paused: false, lane: 1, x: laneX(1), fromX: laneX(1), toX: laneX(1), t: 1, y: H - CAR_H - 30,
    speed: START_SPEED, dist: 0, score: 0, enemies: [], coins: [],
    spawnTimer: 0, coinTimer: 0, coinCount: 0, roadOffset: state ? state.roadOffset : 0
  };
}
reset();

function startGame() { reset(); scene = 'play'; sfxStart(); }
function toMenu() { scene = 'menu'; state.paused = false; }
function gameOver() {
  lastRank = addScore(state.score, state.coinCount);
  scene = 'over';
  sfxCrash();
}
const menuActions = [startGame, () => { scene = 'scores'; }, () => { scene = 'help'; }, () => { scene = 'name'; }];
const menuLabels = ['▶  Chơi ngay', '🏆  Điểm cao', '❓  Hướng dẫn', '✏️  Đổi tên'];

// =====================================================================
//  CHƯỚNG NGẠI VẬT
// =====================================================================
const OBSTACLES = [
  { kind: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 5 },
  { kind: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 3 },
  { kind: 'emoji', e: '🚶', w: 28, h: 50, size: 46, pad: 3, weight: 2, walk: 55 },
  { kind: 'emoji', e: '🐕', w: 44, h: 32, size: 40, pad: 3, weight: 2, walk: 100 },
  { kind: 'emoji', e: '🐈', w: 34, h: 30, size: 34, pad: 3, weight: 2, walk: 85 },
  { kind: 'emoji', e: '🐄', w: 50, h: 40, size: 46, pad: 4, weight: 1, walk: 35 },
  { kind: 'emoji', e: '🚧', w: 42, h: 36, size: 40, pad: 3, weight: 2 },
  { kind: 'emoji', e: '🛢️', w: 32, h: 40, size: 38, pad: 3, weight: 1 },
  { kind: 'emoji', e: '🪨', w: 38, h: 32, size: 36, pad: 3, weight: 1 },
];
const TOTAL_W = OBSTACLES.reduce((a, o) => a + o.weight, 0);
function pickObstacle() {
  let r = Math.random() * TOTAL_W;
  for (const o of OBSTACLES) { if ((r -= o.weight) <= 0) return o; }
  return OBSTACLES[0];
}
const laneOf = e => Math.max(0, Math.min(LANES - 1, Math.floor((e.x + e.w / 2 - ROAD_X) / LANE_W)));
function spawnEnemy() {
  const lane = Math.floor(Math.random() * LANES);
  if (state.enemies.some(e => laneOf(e) === lane && e.y < 140)) return;
  const o = pickObstacle();
  const cx = ROAD_X + lane * LANE_W + LANE_W / 2;
  state.enemies.push({
    ...o, x: cx - o.w / 2, y: -o.h - 10, ph: Math.random() * 6,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    v: o.kind === 'car' ? 60 + Math.random() * 80 : 0,
    vx: o.walk ? (Math.random() < 0.5 ? -1 : 1) * o.walk * (0.75 + Math.random() * 0.5) : 0
  });
}
function spawnCoin() {
  const lane = Math.floor(Math.random() * LANES);
  if (state.enemies.some(e => laneOf(e) === lane && e.y < 110)) return;
  state.coins.push({ x: ROAD_X + lane * LANE_W + LANE_W / 2, y: -20 });
}

// =====================================================================
//  VẼ
// =====================================================================
function drawCar(x, y, color, player) {
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(x + 3, y + 4, CAR_W, CAR_H);
  ctx.fillStyle = color; ctx.beginPath(); ctx.roundRect(x, y, CAR_W, CAR_H, 8); ctx.fill();
  ctx.fillStyle = '#111';
  ctx.fillRect(x - 4, y + 10, 5, 16); ctx.fillRect(x + CAR_W - 1, y + 10, 5, 16);
  ctx.fillRect(x - 4, y + CAR_H - 26, 5, 16); ctx.fillRect(x + CAR_W - 1, y + CAR_H - 26, 5, 16);
  ctx.fillStyle = 'rgba(180,220,255,0.9)'; ctx.fillRect(x + 6, y + (player ? 16 : 30), CAR_W - 12, 16);
  if (player) {
    ctx.fillStyle = '#fff'; ctx.fillRect(x + CAR_W / 2 - 3, y, 6, CAR_H);
    ctx.fillStyle = '#ffe9a0'; ctx.fillRect(x + 4, y + 2, 8, 4); ctx.fillRect(x + CAR_W - 12, y + 2, 8, 4);
  }
}
function drawObstacle(e) {
  if (e.kind === 'car') { drawCar(e.x, e.y, e.color, false); return; }
  const cx = e.x + e.w / 2;
  const cy = e.y + e.h / 2 + (e.vx ? Math.sin(performance.now() / 110 + e.ph) * 2 : 0);
  ctx.save();
  ctx.translate(cx, cy);
  if (e.vx > 0) ctx.scale(-1, 1);
  ctx.font = e.size + 'px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(e.e, 0, 0);
  ctx.restore();
  ctx.textBaseline = 'alphabetic';
}
function drawRoad() {
  ctx.fillStyle = '#2e7d32'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#3a3a3a'; ctx.fillRect(ROAD_X, 0, ROAD_W, H);
  ctx.fillStyle = '#fff'; ctx.fillRect(ROAD_X - 4, 0, 4, H); ctx.fillRect(ROAD_X + ROAD_W, 0, 4, H);
  ctx.fillStyle = '#ddd';
  for (let l = 1; l < LANES; l++)
    for (let y = -40 + (state.roadOffset % 40); y < H; y += 40)
      ctx.fillRect(ROAD_X + l * LANE_W - 2, y, 4, 20);
}
function text(t, x, y, size, color, align) {
  ctx.font = 'bold ' + size + 'px sans-serif';
  ctx.fillStyle = color || '#fff'; ctx.textAlign = align || 'center';
  ctx.fillText(t, x, y);
}
function fitText(t, maxW, size, color, y) {
  ctx.font = 'bold ' + size + 'px sans-serif';
  while (size > 16 && ctx.measureText(t).width > maxW) { size -= 2; ctx.font = 'bold ' + size + 'px sans-serif'; }
  text(t, 0, y, size, color);
}
function overlay(a) { ctx.fillStyle = 'rgba(0,0,0,' + a + ')'; ctx.fillRect(0, 0, W, H); }
function button(label, x, y, w, h, action, selected, idx) {
  buttons.push({ x, y, w, h, action, idx });
  ctx.fillStyle = selected ? '#e53935' : 'rgba(255,255,255,0.12)';
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.fill();
  ctx.strokeStyle = selected ? '#fff' : 'rgba(255,255,255,0.35)'; ctx.lineWidth = 2; ctx.stroke();
  text(label, x + w / 2, y + h / 2 + 7, 19, '#fff');
}
function drawHUD() {
  ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, W, 34);
  text('Điểm: ' + state.score, 10, 23, 16, '#fff', 'left');
  text('🪙 ' + state.coinCount, W / 2, 23, 16, '#ffd700');
  text('Kỷ lục: ' + Math.max(bestScore(), state.score), W - 10, 23, 16, '#8f8', 'right');
  text(Math.round(state.speed / 3) + ' km/h', W - 10, H - 12, 14, '#fff', 'right');
}

function drawScene() {
  buttons = [];
  drawRoad();

  if (scene === 'name') {
    overlay(0.78);
    text('🏎️ ĐUA XE', W / 2, 120, 40);
    text('Nhập tên của bạn để vào game', W / 2, 185, 16, '#ddd');
    if (nameErr > 0) text('⚠ Bạn chưa nhập tên!', W / 2, 410, 17, '#ff5252');
    return;
  }

  if (scene === 'menu') {
    overlay(0.55);
    text('🏎️ ĐUA XE', W / 2, 115, 40);
    text('Điểm cao nhất: ' + bestScore(), W / 2, 155, 16, '#8f8');
    text('👤 ' + getName(), W / 2, 183, 15, '#fff');
    menuLabels.forEach((l, i) => button(l, 100, 210 + i * 62, 200, 48, menuActions[i], i === menuSel, i));
    text('↑ ↓ chọn • Enter xác nhận', W / 2, H - 25, 13, '#aaa');
    return;
  }

  if (scene === 'scores') {
    overlay(0.75);
    text('🏆 BẢNG ĐIỂM CAO', W / 2, 70, 28, '#ffd700');
    if (!scores.length) text('Chưa có điểm nào. Chơi thử đi!', W / 2, 260, 16, '#ccc');
    scores.forEach((r, i) => {
      const y = 115 + i * 34;
      const medal = ['🥇', '🥈', '🥉'][i] || (i + 1) + '.';
      text(medal, 32, y, 18, '#fff', 'left');
      text(r.n || 'Bạn', 72, y, 16, i === 0 ? '#ffd700' : '#fff', 'left');
      text(String(r.s), 262, y, 17, i === 0 ? '#ffd700' : '#fff', 'right');
      text(r.d, W - 20, y, 11, '#aaa', 'right');
    });
    button('⬅ Quay lại', 40, H - 70, 150, 44, toMenu, true);
    button('🗑 Xóa hết', 210, H - 70, 150, 44, () => { scores = []; saveScores([]); }, false);
    return;
  }

  if (scene === 'help') {
    overlay(0.75);
    text('❓ HƯỚNG DẪN', W / 2, 80, 28);
    const lines = ['← → hoặc A D : đổi sang làn kế bên', 'P hoặc Esc : tạm dừng', 'Nhặt xu 🪙 : +5 điểm',
                   'Tránh xe, người, chó mèo, chướng ngại', 'Xe càng chạy càng nhanh', 'Nút 🔊 : bật/tắt âm thanh',
                   'Điện thoại: dùng 2 nút bên dưới'];
    lines.forEach((l, i) => text(l, W / 2, 145 + i * 40, 17, '#eee'));
    button('⬅ Quay lại', 100, H - 80, 200, 46, toMenu, true);
    return;
  }

  // play / over
  for (const c of state.coins) {
    ctx.fillStyle = '#ffd700'; ctx.beginPath(); ctx.arc(c.x, c.y, 10, 0, 7); ctx.fill();
    ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2; ctx.stroke();
  }
  for (const e of state.enemies) drawObstacle(e);
  const tilt = (state.toX - state.x) / LANE_W * 0.35;
  ctx.save();
  ctx.translate(state.x + CAR_W / 2, state.y + CAR_H / 2);
  ctx.rotate(tilt);
  drawCar(-CAR_W / 2, -CAR_H / 2, '#d32f2f', true);
  ctx.restore();
  drawHUD();

  if (scene === 'over') {
    overlay(0.72);
    text('💥 GAME OVER', W / 2, 92, 28, '#ff5252');
    // bảng lớn "username gà quá"
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.beginPath(); ctx.roundRect(25, 115, 350, 185, 16); ctx.fill();
    ctx.strokeStyle = '#ffd54f'; ctx.lineWidth = 3; ctx.stroke();
    const pulse = 1 + 0.04 * Math.sin(performance.now() / 140);
    ctx.save();
    ctx.translate(W / 2, 208);
    ctx.scale(pulse, pulse);
    fitText(getName(), 320, 56, '#ffd54f', -10);
    text('gà quá! 🐔', 0, 55, 46, '#ff5252');
    ctx.restore();
    text('Điểm: ' + state.score, W / 2, 345, 24);
    if (lastRank === 0) text('🏆 KỶ LỤC MỚI!', W / 2, 378, 20, '#ffd700');
    else if (lastRank > 0) text('Xếp hạng #' + (lastRank + 1) + ' trong top 10', W / 2, 378, 17, '#8f8');
    else text('Kỷ lục hiện tại: ' + bestScore(), W / 2, 378, 16, '#aaa');
    button('🔄 Chơi lại', 100, 405, 200, 48, startGame, true);
    button('🏠 Menu', 100, 465, 200, 48, toMenu, false);
    text('Enter: chơi lại • Esc: menu', W / 2, H - 20, 13, '#aaa');
  } else if (state.paused) {
    overlay(0.6);
    text('⏸ TẠM DỪNG', W / 2, 220, 34);
    button('▶ Tiếp tục', 100, 270, 200, 48, () => { state.paused = false; }, true);
    button('🏠 Về menu', 100, 335, 200, 48, toMenu, false);
  }
}

// =====================================================================
//  CẬP NHẬT
// =====================================================================
function hit(a, b) {
  const p = b.pad;
  return a.x + 6 < b.x + b.w - p && a.x + CAR_W - 6 > b.x + p &&
         a.y + 6 < b.y + b.h - p && a.y + CAR_H - 6 > b.y + p;
}
function update(dt) {
  const s = state;
  if (scene !== 'play') { s.roadOffset += 120 * dt; return; }
  if (s.paused) return;

  s.t = Math.min(1, s.t + dt / LANE_TIME);
  s.x = s.fromX + (s.toX - s.fromX) * easeInOut(s.t);

  s.speed = Math.min(MAX_SPEED, s.speed + dt * ACCEL);
  s.dist += s.speed * dt;
  s.roadOffset += s.speed * dt;

  s.spawnTimer -= dt;
  if (s.spawnTimer <= 0) { spawnEnemy(); s.spawnTimer = Math.max(0.3, 1.1 - s.speed / 1400) * (0.6 + Math.random() * 0.8); }
  s.coinTimer -= dt;
  if (s.coinTimer <= 0) { spawnCoin(); s.coinTimer = 1.5 + Math.random() * 2; }

  for (const e of s.enemies) {
    e.y += (s.speed - e.v) * dt;
    if (e.vx) {
      e.x += e.vx * dt;
      const minX = ROAD_X + 2, maxX = ROAD_X + ROAD_W - e.w - 2;
      if (e.x < minX) { e.x = minX; e.vx = Math.abs(e.vx); }
      if (e.x > maxX) { e.x = maxX; e.vx = -Math.abs(e.vx); }
    }
  }
  for (const c of s.coins) c.y += s.speed * dt;
  s.enemies = s.enemies.filter(e => e.y < H + 100);
  s.coins = s.coins.filter(c => c.y < H + 30);

  s.coins = s.coins.filter(c => {
    if (Math.abs(c.x - (s.x + CAR_W / 2)) < 26 && Math.abs(c.y - (s.y + CAR_H / 2)) < 45) {
      s.coinCount++; sfxCoin(); return false;
    }
    return true;
  });
  s.score = Math.floor(s.dist / SCORE_DIV) + s.coinCount * COIN_BONUS;
  for (const e of s.enemies) if (hit({ x: s.x, y: s.y }, e)) { gameOver(); break; }
}

function loop(t) {
  const dt = Math.min(0.05, (t - lastT) / 1000 || 0);
  lastT = t;
  update(dt);
  if (nameErr > 0) nameErr -= dt;
  if (scene !== prevScene) {
    nameBox.style.display = scene === 'name' ? 'block' : 'none';
    if (scene === 'name') { nameInput.value = username; setTimeout(() => { nameInput.focus(); nameInput.select(); }, 30); }
    prevScene = scene;
  }
  audioTick();
  drawScene();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// =====================================================================
//  ĐIỀU KHIỂN
// =====================================================================
window.addEventListener('keydown', e => {
  const k = e.key;
  if (document.activeElement === nameInput) {
    if (k === 'Enter') submitName();
    else if (k === 'Escape' && username) { nameInput.blur(); canvas.focus(); scene = 'menu'; }
    return;
  }
  if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(k)) e.preventDefault();

  if (scene === 'name') {
    nameInput.focus();
  } else if (scene === 'menu') {
    if (k === 'ArrowUp' || k === 'w' || k === 'W') menuSel = (menuSel + 3) % 4;
    else if (k === 'ArrowDown' || k === 's' || k === 'S') menuSel = (menuSel + 1) % 4;
    else if (k === 'Enter' || k === ' ') menuActions[menuSel]();
  } else if (scene === 'play') {
    if (k === 'p' || k === 'P' || k === 'Escape') state.paused = !state.paused;
    else if (!e.repeat && (k === 'ArrowLeft' || k === 'a' || k === 'A')) moveLane(-1);
    else if (!e.repeat && (k === 'ArrowRight' || k === 'd' || k === 'D')) moveLane(1);
    else if (state.paused && (k === 'm' || k === 'M')) toMenu();
  } else if (scene === 'over') {
    if (k === 'Enter' || k === ' ') startGame();
    else if (k === 'Escape' || k === 'm' || k === 'M') toMenu();
  } else if (k === 'Escape' || k === 'Enter' || k === ' ') toMenu();
});

function canvasPos(e) {
  const r = canvas.getBoundingClientRect();
  return { x: (e.clientX - r.left) * W / r.width, y: (e.clientY - r.top) * H / r.height };
}
function buttonAt(p) {
  return buttons.find(b => p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h);
}
canvas.addEventListener('click', e => {
  if (scene === 'name') { nameInput.focus(); return; }
  canvas.focus();
  const b = buttonAt(canvasPos(e));
  if (b) b.action();
});
canvas.addEventListener('mousemove', e => {
  if (scene !== 'menu') return;
  const b = buttonAt(canvasPos(e));
  if (b && b.idx !== undefined) menuSel = b.idx;
});

function bindBtn(id, d) {
  const b = document.getElementById(id);
  const go = e => { e.preventDefault(); initAudio(); moveLane(d); };
  b.addEventListener('mousedown', go);
  b.addEventListener('touchstart', go);
}
bindBtn('btnL', -1); bindBtn('btnR', 1);
</script>
"""

components.html(GAME_HTML, height=740, scrolling=False)
