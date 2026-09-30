import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Game Đua Xe 2D", page_icon="🏎️", layout="centered")

st.title("🏎️ Game Đua Xe 2D")
st.caption("Click vào khung game để bắt đầu • ← → hoặc A D để lái • Space/Enter để chơi lại • P để tạm dừng")

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

let state, keys = {}, lastT = 0, best = 0;
try { best = parseInt(localStorage.getItem('racing_best') || '0'); } catch(e) {}

function reset() {
  state = {
    running: false, over: false, paused: false,
    x: ROAD_X + ROAD_W / 2 - CAR_W / 2, y: H - CAR_H - 30,
    vx: 0, speed: 260, dist: 0, score: 0,
    enemies: [], spawnTimer: 0, roadOffset: 0, coins: [], coinTimer: 0, coinCount: 0
  };
}
reset();

const COLORS = ['#e74c3c','#3498db','#f1c40f','#9b59b6','#1abc9c','#e67e22'];

function spawnEnemy() {
  // không chặn hết làn: chỉ spawn 1 xe mỗi lần, tránh chồng lên xe khác
  const lane = Math.floor(Math.random() * LANES);
  const x = ROAD_X + lane * LANE_W + (LANE_W - CAR_W) / 2;
  if (state.enemies.some(e => Math.abs(e.x - x) < 5 && e.y < 120)) return;
  state.enemies.push({
    x, y: -CAR_H - 10, color: COLORS[Math.floor(Math.random() * COLORS.length)],
    v: 60 + Math.random() * 80
  });
}

function spawnCoin() {
  const lane = Math.floor(Math.random() * LANES);
  const x = ROAD_X + lane * LANE_W + LANE_W / 2;
  if (state.enemies.some(e => Math.abs(e.x + CAR_W/2 - x) < 30 && e.y < 100)) return;
  state.coins.push({ x, y: -20 });
}

function drawCar(x, y, color, player) {
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.fillRect(x + 3, y + 4, CAR_W, CAR_H);
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.roundRect(x, y, CAR_W, CAR_H, 8); ctx.fill();
  ctx.fillStyle = '#111';                      // bánh xe
  ctx.fillRect(x - 4, y + 10, 5, 16); ctx.fillRect(x + CAR_W - 1, y + 10, 5, 16);
  ctx.fillRect(x - 4, y + CAR_H - 26, 5, 16); ctx.fillRect(x + CAR_W - 1, y + CAR_H - 26, 5, 16);
  ctx.fillStyle = 'rgba(180,220,255,0.9)';      // kính
  ctx.fillRect(x + 6, y + (player ? 16 : 30), CAR_W - 12, 16);
  if (player) {
    ctx.fillStyle = '#fff';                     // sọc đua
    ctx.fillRect(x + CAR_W/2 - 3, y, 6, CAR_H);
    ctx.fillStyle = '#ffe9a0';
    ctx.fillRect(x + 4, y + 2, 8, 4); ctx.fillRect(x + CAR_W - 12, y + 2, 8, 4);
  }
}

function drawRoad() {
  ctx.fillStyle = '#2e7d32'; ctx.fillRect(0, 0, W, H);            // cỏ
  ctx.fillStyle = '#3a3a3a'; ctx.fillRect(ROAD_X, 0, ROAD_W, H);  // đường
  ctx.fillStyle = '#fff';
  ctx.fillRect(ROAD_X - 4, 0, 4, H); ctx.fillRect(ROAD_X + ROAD_W, 0, 4, H);
  ctx.fillStyle = '#ddd';
  for (let l = 1; l < LANES; l++) {
    for (let y = -40 + (state.roadOffset % 40); y < H; y += 40) {
      ctx.fillRect(ROAD_X + l * LANE_W - 2, y, 4, 20);
    }
  }
}

function hit(a, b) {
  const p = 6; // nới lỏng va chạm
  return a.x + p < b.x + CAR_W - p && a.x + CAR_W - p > b.x + p &&
         a.y + p < b.y + CAR_H - p && a.y + CAR_H - p > b.y + p;
}

function update(dt) {
  const s = state;
  if (!s.running || s.over || s.paused) return;

  const left = keys['ArrowLeft'] || keys['a'] || keys['A'] || keys.__L;
  const right = keys['ArrowRight'] || keys['d'] || keys['D'] || keys.__R;
  const target = (right ? 1 : 0) - (left ? 1 : 0);
  s.vx += (target * 320 - s.vx) * Math.min(1, dt * 10);
  s.x += s.vx * dt;
  s.x = Math.max(ROAD_X + 2, Math.min(ROAD_X + ROAD_W - CAR_W - 2, s.x));

  s.speed = Math.min(650, s.speed + dt * 6);
  s.dist += s.speed * dt;
  s.roadOffset += s.speed * dt;
  s.score = Math.floor(s.dist / 10) + s.coinCount * 50;

  s.spawnTimer -= dt;
  if (s.spawnTimer <= 0) {
    spawnEnemy();
    s.spawnTimer = Math.max(0.35, 1.1 - s.speed / 900) * (0.6 + Math.random() * 0.8);
  }
  s.coinTimer -= dt;
  if (s.coinTimer <= 0) { spawnCoin(); s.coinTimer = 1.5 + Math.random() * 2; }

  for (const e of s.enemies) e.y += (s.speed - e.v) * dt;
  for (const c of s.coins) c.y += s.speed * dt;
  s.enemies = s.enemies.filter(e => e.y < H + 100);
  s.coins = s.coins.filter(c => c.y < H + 30);

  const me = { x: s.x, y: s.y };
  for (const e of s.enemies) {
    if (hit(me, e)) {
      s.over = true;
      if (s.score > best) {
        best = s.score;
        try { localStorage.setItem('racing_best', String(best)); } catch(err) {}
      }
    }
  }
  s.coins = s.coins.filter(c => {
    if (Math.abs(c.x - (s.x + CAR_W/2)) < 26 && Math.abs(c.y - (s.y + CAR_H/2)) < 45) {
      s.coinCount++; return false;
    }
    return true;
  });
}

function text(t, x, y, size, color, align) {
  ctx.font = 'bold ' + size + 'px sans-serif';
  ctx.fillStyle = color || '#fff';
  ctx.textAlign = align || 'center';
  ctx.fillText(t, x, y);
}

function draw() {
  drawRoad();
  for (const c of state.coins) {
    ctx.fillStyle = '#ffd700'; ctx.beginPath(); ctx.arc(c.x, c.y, 10, 0, 7); ctx.fill();
    ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2; ctx.stroke();
  }
  for (const e of state.enemies) drawCar(e.x, e.y, e.color, false);
  drawCar(state.x, state.y, '#d32f2f', true);

  // HUD
  ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, W, 34);
  text('Điểm: ' + state.score, 10, 23, 16, '#fff', 'left');
  text('🪙 ' + state.coinCount, W/2, 23, 16, '#ffd700');
  text('Kỷ lục: ' + best, W - 10, 23, 16, '#8f8', 'right');
  text(Math.round(state.speed / 3) + ' km/h', W - 10, H - 12, 14, '#fff', 'right');

  if (!state.running) {
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, W, H);
    text('🏎️ ĐUA XE 2D', W/2, 240, 36);
    text('Nhấn Space / Enter hoặc click để bắt đầu', W/2, 290, 15, '#ddd');
    text('← → hoặc A D để lái • Nhặt xu 🪙 • Tránh xe', W/2, 320, 14, '#aaa');
  } else if (state.over) {
    ctx.fillStyle = 'rgba(0,0,0,0.65)'; ctx.fillRect(0, 0, W, H);
    text('💥 GAME OVER', W/2, 250, 38, '#ff5252');
    text('Điểm: ' + state.score, W/2, 295, 22);
    text('Nhấn Space / Enter để chơi lại', W/2, 335, 15, '#ddd');
  } else if (state.paused) {
    ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H);
    text('⏸ TẠM DỪNG', W/2, 300, 32);
  }
}

function loop(t) {
  const dt = Math.min(0.05, (t - lastT) / 1000 || 0);
  lastT = t;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

function startOrRestart() {
  if (!state.running || state.over) { reset(); state.running = true; }
}

window.addEventListener('keydown', e => {
  keys[e.key] = true;
  if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key)) e.preventDefault();
  if (e.key === ' ' || e.key === 'Enter') startOrRestart();
  if (e.key === 'p' || e.key === 'P') { if (state.running && !state.over) state.paused = !state.paused; }
});
window.addEventListener('keyup', e => { keys[e.key] = false; });
canvas.addEventListener('click', () => { canvas.focus(); startOrRestart(); });

// Nút cảm ứng cho điện thoại
function bindBtn(id, key) {
  const b = document.getElementById(id);
  const on = e => { e.preventDefault(); keys[key] = true; if (!state.running || state.over) startOrRestart(); };
  const off = e => { e.preventDefault(); keys[key] = false; };
  b.addEventListener('mousedown', on); b.addEventListener('touchstart', on);
  b.addEventListener('mouseup', off); b.addEventListener('mouseleave', off);
  b.addEventListener('touchend', off);
}
bindBtn('btnL', '__L'); bindBtn('btnR', '__R');
canvas.focus();
</script>
"""

components.html(GAME_HTML, height=720, scrolling=False)

st.markdown(
    "**Mẹo:** Xe càng chạy càng nhanh. Nhặt xu 🪙 được +50 điểm. "
    "Kỷ lục được lưu trong trình duyệt của bạn."
)
