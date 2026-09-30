import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Đua Xe", page_icon="🏎️", layout="centered")

st.title("🏎️ Đua Xe")

GAME_HTML = """
<div style="display:flex;flex-direction:column;align-items:center;font-family:sans-serif;">
  <canvas id="game" width="400" height="600" tabindex="0"
    style="background:#222;border:3px solid #444;border-radius:8px;max-width:100%;outline:none;touch-action:none;"></canvas>
  <div style="margin-top:10px;display:flex;gap:12px;">
    <button id="btnL" style="font-size:24px;padding:10px 30px;border-radius:8px;">⬅️</button>
    <button id="btnR" style="font-size:24px;padding:10px 30px;border-radius:8px;">➡️</button>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

const ROAD_X = 40, ROAD_W = 320, LANES = 4, LANE_W = ROAD_W / LANES;
const CAR_W = 40, CAR_H = 70;
const START_SPEED = 240, ACCEL = 16, MAX_SPEED = 1100;   // tốc độ tăng dần đều
const SCORE_DIV = 150, COIN_BONUS = 5;                  // điểm tăng chậm
const LANE_TIME = 0.22;                                 // giây để đổi 1 làn
const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const COLORS = ['#e74c3c','#3498db','#f1c40f','#9b59b6','#1abc9c','#e67e22'];

// ---------- Điểm cao (localStorage, có dự phòng bộ nhớ tạm) ----------
const KEY = 'racing_scores_v2';
let memScores = [];
function loadScores() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return memScores; }
}
function saveScores(list) {
  memScores = list;
  try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {}
}
let scores = loadScores();
function addScore(s, coins) {
  const entry = { s, coins, d: new Date().toLocaleDateString('vi-VN') };
  scores.push(entry);
  scores.sort((a, b) => b.s - a.s);
  scores = scores.slice(0, 10);
  saveScores(scores);
  return scores.indexOf(entry);            // -1 nếu không lọt top 10
}
const bestScore = () => scores.length ? scores[0].s : 0;

// ---------- Trạng thái ----------
let scene = 'menu';                        // menu | play | over | scores | help
let menuSel = 0, keys = {}, lastT = 0, buttons = [];
let state, lastRank = -1;

const laneX = l => ROAD_X + l * LANE_W + (LANE_W - CAR_W) / 2;
function moveLane(d) {
  if (scene !== 'play' || state.paused) return;
  const nl = Math.max(0, Math.min(LANES - 1, state.lane + d));
  if (nl === state.lane) return;
  state.lane = nl;
  state.fromX = state.x; state.toX = laneX(nl); state.t = 0;
}

function reset() {
  state = {
    paused: false, lane: 1, x: laneX(1), fromX: laneX(1), toX: laneX(1), t: 1, y: H - CAR_H - 30,
    speed: START_SPEED, dist: 0, score: 0, enemies: [], coins: [],
    spawnTimer: 0, coinTimer: 0, coinCount: 0, roadOffset: state ? state.roadOffset : 0
  };
}
reset();

function startGame() { reset(); scene = 'play'; }
function toMenu() { scene = 'menu'; state.paused = false; }
function gameOver() {
  lastRank = addScore(state.score, state.coinCount);
  scene = 'over';
}

const menuActions = [startGame, () => { scene = 'scores'; }, () => { scene = 'help'; }];
const menuLabels = ['▶  Chơi ngay', '🏆  Điểm cao', '❓  Hướng dẫn'];

// ---------- Sinh vật thể ----------
// kind: car = vẽ xe; còn lại vẽ emoji. v = tốc độ tự chạy về phía trước (0 = đứng yên)
const OBSTACLES = [
  { kind: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 5 },
  { kind: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 3 },
  { kind: 'emoji', e: '🚶', w: 28, h: 50, size: 46, pad: 3, weight: 2, v: 0 },
  { kind: 'emoji', e: '🐕', w: 44, h: 32, size: 40, pad: 3, weight: 2, v: 0 },
  { kind: 'emoji', e: '🐈', w: 34, h: 30, size: 34, pad: 3, weight: 2, v: 0 },
  { kind: 'emoji', e: '🐄', w: 50, h: 40, size: 46, pad: 4, weight: 1, v: 0 },
  { kind: 'emoji', e: '🚧', w: 42, h: 36, size: 40, pad: 3, weight: 2, v: 0 },
  { kind: 'emoji', e: '🛢️', w: 32, h: 40, size: 38, pad: 3, weight: 1, v: 0 },
  { kind: 'emoji', e: '🪨', w: 38, h: 32, size: 36, pad: 3, weight: 1, v: 0 },
];
const TOTAL_W = OBSTACLES.reduce((a, o) => a + o.weight, 0);
function pickObstacle() {
  let r = Math.random() * TOTAL_W;
  for (const o of OBSTACLES) { if ((r -= o.weight) <= 0) return o; }
  return OBSTACLES[0];
}
function spawnEnemy() {
  const lane = Math.floor(Math.random() * LANES);
  if (state.enemies.some(e => e.lane === lane && e.y < 140)) return;
  const o = pickObstacle();
  const cx = ROAD_X + lane * LANE_W + LANE_W / 2;
  state.enemies.push({
    ...o, lane, x: cx - o.w / 2, y: -o.h - 10,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    v: o.kind === 'car' ? 60 + Math.random() * 80 : 0
  });
}
function spawnCoin() {
  const lane = Math.floor(Math.random() * LANES);
  if (state.enemies.some(e => e.lane === lane && e.y < 110)) return;
  state.coins.push({ x: ROAD_X + lane * LANE_W + LANE_W / 2, y: -20 });
}

// ---------- Vẽ ----------
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
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.beginPath(); ctx.ellipse(e.x + e.w / 2, e.y + e.h - 2, e.w / 2, 5, 0, 0, 7); ctx.fill();
  ctx.font = e.size + 'px serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(e.e, e.x + e.w / 2, e.y + e.h / 2);
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

  if (scene === 'menu') {
    overlay(0.55);
    text('🏎️ ĐUA XE', W / 2, 130, 40);
    text('Điểm cao nhất: ' + bestScore(), W / 2, 170, 16, '#8f8');
    menuLabels.forEach((l, i) => button(l, 100, 230 + i * 65, 200, 48, menuActions[i], i === menuSel, i));
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
      text(medal, 50, y, 18, '#fff', 'left');
      text(r.s + ' điểm', 100, y, 18, i === 0 ? '#ffd700' : '#fff', 'left');
      text('🪙' + (r.coins || 0), 240, y, 15, '#ffd700', 'left');
      text(r.d, W - 40, y, 13, '#aaa', 'right');
    });
    button('⬅ Quay lại', 40, H - 70, 150, 44, toMenu, true);
    button('🗑 Xóa hết', 210, H - 70, 150, 44, () => { scores = []; saveScores([]); }, false);
    return;
  }

  if (scene === 'help') {
    overlay(0.75);
    text('❓ HƯỚNG DẪN', W / 2, 80, 28);
    const lines = ['← → hoặc A D : đổi sang làn kế bên', 'P hoặc Esc : tạm dừng', 'Nhặt xu 🪙 : +5 điểm',
                   'Tránh xe, người, chó mèo, chướng ngại', 'Xe càng chạy càng nhanh', 'Điện thoại: dùng 2 nút bên dưới'];
    lines.forEach((l, i) => text(l, W / 2, 150 + i * 42, 17, '#eee'));
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
    overlay(0.7);
    text('💥 GAME OVER', W / 2, 190, 38, '#ff5252');
    text('Điểm: ' + state.score, W / 2, 240, 24);
    if (lastRank === 0) text('🏆 KỶ LỤC MỚI!', W / 2, 280, 22, '#ffd700');
    else if (lastRank > 0) text('Xếp hạng #' + (lastRank + 1) + ' trong top 10', W / 2, 280, 17, '#8f8');
    else text('Kỷ lục hiện tại: ' + bestScore(), W / 2, 280, 16, '#aaa');
    button('🔄 Chơi lại', 100, 330, 200, 48, startGame, true);
    button('🏠 Menu', 100, 395, 200, 48, toMenu, false);
    text('Enter: chơi lại • Esc: menu', W / 2, H - 25, 13, '#aaa');
  } else if (state.paused) {
    overlay(0.6);
    text('⏸ TẠM DỪNG', W / 2, 220, 34);
    button('▶ Tiếp tục', 100, 270, 200, 48, () => { state.paused = false; }, true);
    button('🏠 Về menu', 100, 335, 200, 48, toMenu, false);
  }
}

// ---------- Cập nhật ----------
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
  s.score = Math.floor(s.dist / SCORE_DIV) + s.coinCount * COIN_BONUS;

  s.spawnTimer -= dt;
  if (s.spawnTimer <= 0) { spawnEnemy(); s.spawnTimer = Math.max(0.3, 1.1 - s.speed / 1400) * (0.6 + Math.random() * 0.8); }
  s.coinTimer -= dt;
  if (s.coinTimer <= 0) { spawnCoin(); s.coinTimer = 1.5 + Math.random() * 2; }

  for (const e of s.enemies) e.y += (s.speed - e.v) * dt;
  for (const c of s.coins) c.y += s.speed * dt;
  s.enemies = s.enemies.filter(e => e.y < H + 100);
  s.coins = s.coins.filter(c => c.y < H + 30);

  s.coins = s.coins.filter(c => {
    if (Math.abs(c.x - (s.x + CAR_W / 2)) < 26 && Math.abs(c.y - (s.y + CAR_H / 2)) < 45) { s.coinCount++; return false; }
    return true;
  });
  s.score = Math.floor(s.dist / SCORE_DIV) + s.coinCount * COIN_BONUS;
  for (const e of s.enemies) if (hit({ x: s.x, y: s.y }, e)) { gameOver(); break; }
}

function loop(t) {
  const dt = Math.min(0.05, (t - lastT) / 1000 || 0);
  lastT = t;
  update(dt);
  drawScene();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// ---------- Điều khiển ----------
window.addEventListener('keydown', e => {
  const k = e.key;
  keys[k] = true;
  if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(k)) e.preventDefault();

  if (scene === 'menu') {
    if (k === 'ArrowUp' || k === 'w' || k === 'W') menuSel = (menuSel + 2) % 3;
    else if (k === 'ArrowDown' || k === 's' || k === 'S') menuSel = (menuSel + 1) % 3;
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
window.addEventListener('keyup', e => { keys[e.key] = false; });

function canvasPos(e) {
  const r = canvas.getBoundingClientRect();
  return { x: (e.clientX - r.left) * W / r.width, y: (e.clientY - r.top) * H / r.height };
}
function buttonAt(p) {
  return buttons.find(b => p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h);
}
canvas.addEventListener('click', e => {
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
  const go = e => { e.preventDefault(); moveLane(d); };
  b.addEventListener('mousedown', go);
  b.addEventListener('touchstart', go);
}
bindBtn('btnL', -1); bindBtn('btnR', 1);
canvas.focus();
</script>
"""

components.html(GAME_HTML, height=720, scrolling=False)
