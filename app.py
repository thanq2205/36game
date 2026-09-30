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
    <button id="btnH" style="font-size:24px;padding:10px 14px;border-radius:8px;">📢</button>
    <button id="btnM" style="font-size:24px;padding:10px 14px;border-radius:8px;">🔊</button>
    <button id="btnR" style="font-size:24px;padding:10px 30px;border-radius:8px;">➡️</button>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

const ROAD_X = 70, ROAD_W = 260, LANES = 4, LANE_W = ROAD_W / LANES;
const CAR_W = 40, CAR_H = 70;
const START_SPEED = 240, ACCEL = 16, MAX_SPEED = 1100;
const SCORE_DIV = 150, COIN_BONUS = 5;
const LANE_TIME = 0.22;
const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const rnd = Math.random;
const COLORS = ['#e74c3c','#3498db','#f1c40f','#9b59b6','#1abc9c','#e67e22'];

// =====================================================================
//  ÂM THANH (WebAudio, tự tổng hợp - không cần file)
// =====================================================================
let AC = null, master, musicGain, sfxGain, noiseBuf, muted = false, hasPan = false;
let engA, engB, engSub, engFilt, engGain, roadGain, roadFilt, windGain, windFilt;
let lastGear = 0, lastVoice = 0, lastPass = 0, ambT = 4;
const m2f = m => 440 * Math.pow(2, (m - 69) / 12);

function makeImpulse(sec, decay) {                       // hồi âm (reverb) giả lập
  const len = Math.floor(AC.sampleRate * sec), b = AC.createBuffer(2, len, AC.sampleRate);
  for (let c = 0; c < 2; c++) {
    const d = b.getChannelData(c);
    for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
  }
  return b;
}
function loopNoise(dest, ftype, freq, q) {
  const src = AC.createBufferSource(); src.buffer = noiseBuf; src.loop = true;
  const f = AC.createBiquadFilter(); f.type = ftype; f.frequency.value = freq; if (q) f.Q.value = q;
  const g = AC.createGain(); g.gain.value = 0;
  src.connect(f); f.connect(g); g.connect(dest); src.start();
  return { f, g };
}
function initAudio() {
  if (AC) { if (AC.state === 'suspended') AC.resume(); return; }
  try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; return; }
  hasPan = typeof AC.createStereoPanner === 'function';
  master = AC.createGain(); master.gain.value = muted ? 0 : 0.85;
  const comp = AC.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 4;
  master.connect(comp); comp.connect(AC.destination);

  const rev = AC.createConvolver(); rev.buffer = makeImpulse(1.6, 2.6);
  const revG = AC.createGain(); revG.gain.value = 0.28; rev.connect(revG); revG.connect(master);
  musicGain = AC.createGain(); musicGain.gain.value = 0.2; musicGain.connect(master);
  const mSend = AC.createGain(); mSend.gain.value = 0.25; musicGain.connect(mSend); mSend.connect(rev);
  sfxGain = AC.createGain(); sfxGain.gain.value = 0.6; sfxGain.connect(master);
  const sSend = AC.createGain(); sSend.gain.value = 0.35; sfxGain.connect(sSend); sSend.connect(rev);

  noiseBuf = AC.createBuffer(1, AC.sampleRate * 2, AC.sampleRate);
  const nd = noiseBuf.getChannelData(0);
  for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;

  // động cơ xe của bạn: 2 sóng răng cưa lệch nhẹ + sub + rung xi-lanh, qua bộ lọc
  engA = AC.createOscillator(); engA.type = 'sawtooth';
  engB = AC.createOscillator(); engB.type = 'sawtooth';
  engSub = AC.createOscillator(); engSub.type = 'sine';
  engFilt = AC.createBiquadFilter(); engFilt.type = 'lowpass'; engFilt.frequency.value = 500; engFilt.Q.value = 2;
  const trem = AC.createGain(); trem.gain.value = 0.75;
  const lfo = AC.createOscillator(), lfoG = AC.createGain(); lfo.frequency.value = 26; lfoG.gain.value = 0.25;
  lfo.connect(lfoG); lfoG.connect(trem.gain); lfo.start();
  const subG = AC.createGain(); subG.gain.value = 0.9;
  engGain = AC.createGain(); engGain.gain.value = 0;
  engA.connect(engFilt); engB.connect(engFilt); engSub.connect(subG); subG.connect(engFilt);
  engFilt.connect(trem); trem.connect(engGain); engGain.connect(sfxGain);
  engA.start(); engB.start(); engSub.start();
  const road = loopNoise(sfxGain, 'lowpass', 400); roadGain = road.g; roadFilt = road.f;   // tiếng lốp trên đường
  const wind = loopNoise(sfxGain, 'bandpass', 1500, 0.7); windGain = wind.g; windFilt = wind.f; // tiếng gió

  nextT = AC.currentTime + 0.1;
  setInterval(scheduler, 50);
}

function toneAt(f, d, type, vol, t, dest, slide) {
  const o = AC.createOscillator(), g = AC.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t);
  if (slide) o.frequency.exponentialRampToValueAtTime(slide, t + d);
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(dest || sfxGain); o.start(t); o.stop(t + d + 0.03);
}
function noiseAt(d, vol, f0, f1, ftype, t, dest, q) {
  const src = AC.createBufferSource(); src.buffer = noiseBuf;
  const fl = AC.createBiquadFilter(); fl.type = ftype; if (q) fl.Q.value = q;
  fl.frequency.setValueAtTime(f0, t); fl.frequency.exponentialRampToValueAtTime(f1, t + d);
  const g = AC.createGain();
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  src.connect(fl); fl.connect(g); g.connect(dest || sfxGain); src.start(t); src.stop(t + d + 0.03);
}
function pannedDest(pan) {
  if (!hasPan) return sfxGain;
  const p = AC.createStereoPanner(); p.pan.value = pan; p.connect(sfxGain); return p;
}
function brassAt(f, d, t, vol, slide) {                  // kèn "wah wah" khi thua
  const o = AC.createOscillator(), o2 = AC.createOscillator(), fl = AC.createBiquadFilter(), g = AC.createGain();
  o.type = 'sawtooth'; o2.type = 'sawtooth'; o2.detune.value = 8;
  [o, o2].forEach(x => { x.frequency.setValueAtTime(f, t); if (slide) x.frequency.exponentialRampToValueAtTime(slide, t + d); });
  fl.type = 'lowpass'; fl.frequency.setValueAtTime(400, t);
  fl.frequency.linearRampToValueAtTime(1600, t + d * 0.25); fl.frequency.linearRampToValueAtTime(700, t + d);
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.05);
  g.gain.setValueAtTime(vol, t + d * 0.75); g.gain.linearRampToValueAtTime(0.0001, t + d);
  o.connect(fl); o2.connect(fl); fl.connect(g); g.connect(sfxGain);
  o.start(t); o2.start(t); o.stop(t + d + 0.03); o2.stop(t + d + 0.03);
}
function hornAt(freqs, d, t, vol, dest) {                // còi xe
  const g = AC.createGain(), fl = AC.createBiquadFilter();
  fl.type = 'lowpass'; fl.frequency.value = 2200;
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.02);
  g.gain.setValueAtTime(vol, t + d - 0.05); g.gain.linearRampToValueAtTime(0.0001, t + d);
  freqs.forEach(f => {
    ['square', 'sawtooth'].forEach((ty, k) => {
      const o = AC.createOscillator(), og = AC.createGain();
      o.type = ty; o.frequency.value = f * (k ? 1.005 : 1); og.gain.value = 0.5;
      o.connect(og); og.connect(fl); o.start(t); o.stop(t + d + 0.03);
    });
  });
  fl.connect(g); g.connect(dest || sfxGain);
}

// ---- giọng / tiếng kêu: sóng răng cưa qua các bộ lọc formant có trượt tần số ----
// forms: [[f đầu, f cuối, Q, gain], ...]   o: {mid:[tỉ lệ, tần số], vib:[Hz, độ sâu], rasp, breath, att}
function voiceAt(fa, fb, d, vol, t, forms, o) {
  o = o || {};
  const osc = AC.createOscillator(); osc.type = 'sawtooth';
  osc.frequency.setValueAtTime(fa, t);
  if (o.mid) osc.frequency.linearRampToValueAtTime(o.mid[1], t + d * o.mid[0]);
  osc.frequency.linearRampToValueAtTime(fb, t + d);
  if (o.vib) {
    const l = AC.createOscillator(), lg = AC.createGain();
    l.frequency.value = o.vib[0]; lg.gain.value = o.vib[1];
    l.connect(lg); lg.connect(osc.frequency); l.start(t); l.stop(t + d + 0.05);
  }
  const src = AC.createGain(); src.gain.value = 1;
  if (o.rasp) {                                            // giọng khàn/rè
    const r = AC.createOscillator(), rg = AC.createGain();
    r.frequency.value = o.rasp; rg.gain.value = 0.45; src.gain.value = 0.55;
    r.connect(rg); rg.connect(src.gain); r.start(t); r.stop(t + d + 0.05);
  }
  osc.connect(src);
  const g = AC.createGain(), att = o.att || 0.03;
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + att);
  g.gain.setValueAtTime(vol, t + Math.max(att, d * 0.7)); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  const dry = AC.createGain(); dry.gain.value = 0.1; src.connect(dry); dry.connect(g);
  forms.forEach(fm => {
    const b = AC.createBiquadFilter(); b.type = 'bandpass'; b.Q.value = fm[2];
    b.frequency.setValueAtTime(fm[0], t); b.frequency.linearRampToValueAtTime(fm[1], t + d);
    const fg = AC.createGain(); fg.gain.value = fm[3];
    src.connect(b); b.connect(fg); fg.connect(g);
  });
  if (o.breath) {                                          // hơi thở
    const n = AC.createBufferSource(); n.buffer = noiseBuf;
    const nb = AC.createBiquadFilter(); nb.type = 'bandpass'; nb.frequency.value = forms[1] ? forms[1][0] : 2000; nb.Q.value = 1.2;
    const ng = AC.createGain(); ng.gain.value = 0.35;
    n.connect(nb); nb.connect(ng); ng.connect(g); n.start(t); n.stop(t + d + 0.05);
  }
  g.connect(o.dest || sfxGain); osc.start(t); osc.stop(t + d + 0.05);
}
function speak(txt, lang, rate, pitch) {                 // câu "meme" đọc bằng giọng của trình duyệt
  if (muted || !('speechSynthesis' in window)) return;
  try {
    const u = new SpeechSynthesisUtterance(txt);
    u.lang = lang; u.rate = rate || 1; u.pitch = pitch || 1; u.volume = 0.9;
    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
  } catch (e) {}
}
function stopSpeech() { try { window.speechSynthesis.cancel(); } catch (e) {} }

// ---- tiếng động vật ----
function sfxDog() {
  if (!AC) return; const t = AC.currentTime;
  [0, 0.26].forEach((d, k) => {
    voiceAt(300 - k * 20, 140, 0.16, 0.9, t + d, [[650, 900, 6, 3.5], [1100, 1400, 6, 2.5]], { mid: [0.15, 340], att: 0.008, breath: 1 });
    noiseAt(0.05, 0.3, 2500, 800, 'bandpass', t + d, sfxGain);
  });
}
function sfxCat() {
  if (!AC) return; const t = AC.currentTime;
  voiceAt(450, 780, 0.22, 0.85, t, [[420, 850, 5, 3], [2200, 1500, 6, 2.5]], { vib: [6, 14] });
  voiceAt(780, 420, 0.42, 0.85, t + 0.2, [[850, 500, 5, 3], [1500, 950, 6, 2.5]], { vib: [6, 12] });
}
function sfxCow() {
  if (!AC) return;
  voiceAt(100, 88, 1.3, 0.95, AC.currentTime, [[330, 480, 5, 4], [800, 900, 5, 2]], { mid: [0.25, 125], vib: [5, 4], att: 0.08 });
}
// ---- tiếng xe cộ ----
function sfxHonk(kind, dest, vol) {
  if (!AC) return; const t = AC.currentTime; vol = vol || 0.26;
  if (kind === undefined) kind = Math.floor(rnd() * 4);
  if (kind === 0) { hornAt([420, 530], 0.16, t, vol, dest); hornAt([420, 530], 0.16, t + 0.24, vol, dest); }      // bíp bíp
  else if (kind === 1) hornAt([400, 500], 0.75, t, vol, dest);                                                    // bíiiip dài
  else if (kind === 2) hornAt([196, 247, 311], 0.95, t, vol * 1.1, dest);                                         // còi xe tải
  else { hornAt([560, 700], 0.12, t, vol, dest); hornAt([560, 700], 0.12, t + 0.17, vol, dest); hornAt([560, 700], 0.25, t + 0.34, vol, dest); } // xe máy
}
function sfxPass() {
  if (!AC) return; const t = AC.currentTime;
  if (t - lastPass < 0.3) return; lastPass = t;
  noiseAt(0.5, 0.28, 2200, 300, 'bandpass', t, sfxGain, 1);
}
function sfxShift() {                                     // sang số
  if (!AC) return;
  noiseAt(0.14, 0.28, 3200, 900, 'bandpass', AC.currentTime, sfxGain, 1.2);
}
function sfxScreech() {                                   // phanh rít
  if (!AC) return; const t = AC.currentTime;
  noiseAt(0.7, 0.5, 6000, 2500, 'highpass', t, sfxGain);
  toneAt(1800, 0.6, 'sawtooth', 0.1, t, sfxGain, 1100);
}
function sfxAmbientTraffic() {                            // xe cộ ở xa trên phố
  if (!AC) return; const t = AC.currentTime, d = pannedDest((rnd() < 0.5 ? -1 : 1) * 0.8), k = Math.floor(rnd() * 4);
  if (k === 0) sfxHonk(undefined, d, 0.1);
  else if (k === 1) { toneAt(140, 1.4, 'sawtooth', 0.1, t, d, 320); noiseAt(1.4, 0.12, 1500, 600, 'bandpass', t, d); }   // xe máy vù qua
  else if (k === 2) { noiseAt(2.2, 0.16, 220, 90, 'lowpass', t, d); toneAt(70, 2.2, 'sawtooth', 0.08, t, d, 45); }        // xe tải rền
  else for (let i = 0; i < 4; i++) toneAt(i % 2 ? 700 : 950, 0.45, 'sine', 0.07, t + i * 0.5, d);                          // còi hụ xa
}

// ---- tiếng động cơ của từng xe trong giao thông (có hiệu ứng Doppler khi lướt qua) ----
function ensureCarVoice(e) {
  if (e.voice || !AC || e.kind !== 'car') return;
  const o1 = AC.createOscillator(), o2 = AC.createOscillator(), f = AC.createBiquadFilter(), g = AC.createGain();
  const p = hasPan ? AC.createStereoPanner() : null;
  e.pitch = 70 + rnd() * 60;
  o1.type = 'sawtooth'; o2.type = 'square'; f.type = 'lowpass'; f.frequency.value = 600; g.gain.value = 0;
  o1.frequency.value = e.pitch; o2.frequency.value = e.pitch * 0.5;
  o1.connect(f); o2.connect(f); f.connect(g);
  if (p) { g.connect(p); p.connect(sfxGain); } else g.connect(sfxGain);
  o1.start(); o2.start();
  e.voice = { o1, o2, g, p, f };
}
function updateCarVoice(e) {
  const v = e.voice; if (!v) return;
  const now = AC.currentTime, dy = e.y - state.y, dist = Math.abs(dy);
  const near = Math.exp(-Math.pow(dist / 220, 2));
  const dop = 1 - 0.18 * Math.tanh(dy / 70);                // xe đang tới: cao hơn, đã qua: thấp xuống
  v.g.gain.setTargetAtTime(0.2 * near, now, 0.05);
  v.o1.frequency.setTargetAtTime(e.pitch * dop, now, 0.05);
  v.o2.frequency.setTargetAtTime(e.pitch * 0.5 * dop, now, 0.05);
  v.f.frequency.setTargetAtTime(350 + 450 * near, now, 0.08);
  if (v.p) v.p.pan.setTargetAtTime(Math.max(-1, Math.min(1, (e.x - state.x) / 180)), now, 0.05);
}
function endVoice(e) {
  const v = e.voice; if (!v) return;
  e.voice = null;
  try { v.g.gain.setTargetAtTime(0, AC.currentTime, 0.05); v.o1.stop(AC.currentTime + 0.3); v.o2.stop(AC.currentTime + 0.3); } catch (er) {}
}
function endAllVoices() { if (state) state.enemies.forEach(endVoice); }

// ---- tiếng hét khi bị tông ----
function sfxScream(who) {
  if (!AC) return; const t = AC.currentTime;
  if (who === 'person') {
    voiceAt(650, 1150, 1.15, 1.0, t, [[850, 1000, 5, 3.5], [1400, 1700, 5, 3], [2800, 3100, 6, 2]], { mid: [0.2, 1400], vib: [6.5, 45], rasp: 60, breath: 1 });
    voiceAt(660, 1180, 1.1, 0.7, t + 0.03, [[900, 1050, 5, 3], [1500, 1800, 5, 2.5]], { mid: [0.2, 1440], vib: [7, 50], rasp: 55 });
  } else if (who === 'dog') {
    voiceAt(800, 600, 0.45, 0.9, t, [[900, 1100, 5, 3], [2300, 2600, 6, 2]], { mid: [0.25, 1800], vib: [10, 50] });
  } else if (who === 'cat') {
    voiceAt(850, 1500, 0.7, 0.9, t, [[1300, 1600, 4, 3], [2900, 3200, 6, 2]], { mid: [0.3, 2100], vib: [26, 80], rasp: 70, breath: 1 });
  } else if (who === 'cow') {
    voiceAt(150, 140, 1.2, 1.0, t, [[380, 500, 5, 4], [850, 900, 5, 2]], { mid: [0.3, 250], vib: [6, 10] });
  }
}
const IDLE_PHRASES = [['Ê ê ê!', 'vi-VN'], ['Ơ kìa!', 'vi-VN'], ['Bruh', 'en-US'], ['Ayo?', 'en-US'], ['Đi đâu vậy trời', 'vi-VN']];
const HIT_PHRASES = [['Ối giời ơi!', 'vi-VN'], ['Bruh', 'en-US'], ['Oh no no no no', 'en-US'], ['Trời ơi!', 'vi-VN']];
function ambientSound(e) {                                // khi vật cản xuất hiện
  const now = performance.now();
  if (now - lastVoice < 700) return;
  if (e.snd === 'car') { if (rnd() < 0.6) { sfxHonk(); lastVoice = now; } return; }
  lastVoice = now;
  if (e.snd === 'dog') sfxDog();
  else if (e.snd === 'cat') sfxCat();
  else if (e.snd === 'cow') sfxCow();
  else if (e.snd === 'person') { const p = IDLE_PHRASES[Math.floor(rnd() * IDLE_PHRASES.length)]; speak(p[0], p[1], 1.05, 1.1); }
}

// ---- hiệu ứng chung ----
function sfxSwoosh() {
  if (!AC) return; const t = AC.currentTime;
  noiseAt(0.22, 0.4, 500, 2400, 'bandpass', t, sfxGain, 1.2);
  if (state.speed > 560) {                                // phanh lốp rít khi đánh lái gấp
    noiseAt(0.25, 0.16, 7000, 4000, 'highpass', t, sfxGain);
    toneAt(1500, 0.22, 'sine', 0.05, t, sfxGain, 1100);
  }
}
function sfxCoin() {
  if (!AC) return; const t = AC.currentTime;
  [1319, 1760, 2093].forEach((f, i) => toneAt(f, 0.22 - i * 0.03, 'triangle', 0.22, t + i * 0.06, sfxGain));
  toneAt(2637, 0.3, 'sine', 0.08, t + 0.18, sfxGain);
}
function sfxStart() {
  if (!AC) return; const t = AC.currentTime;
  toneAt(80, 0.6, 'sawtooth', 0.25, t, sfxGain, 260);     // rồ ga
  noiseAt(0.5, 0.15, 400, 1800, 'bandpass', t, sfxGain);
  [0, 0.12].forEach(d => toneAt(660, 0.09, 'square', 0.15, t + d, sfxGain));
  toneAt(990, 0.25, 'square', 0.18, t + 0.26, sfxGain);
}
function sfxCrash(living, who) {
  if (!AC) return; const t = AC.currentTime;
  if (living) {                                           // "bịch" + tiếng hét
    toneAt(110, 0.28, 'sine', 1.0, t, sfxGain, 38);
    noiseAt(0.25, 0.9, 1200, 120, 'lowpass', t, sfxGain);
    noiseAt(0.2, 0.4, 3000, 500, 'bandpass', t + 0.04, sfxGain, 1.5);
    sfxScream(who);
  } else {                                                // nổ + kim loại + kính vỡ
    toneAt(95, 1.0, 'sine', 1.2, t, sfxGain, 26);
    noiseAt(1.3, 1.0, 4200, 70, 'lowpass', t, sfxGain);
    toneAt(150, 0.6, 'sawtooth', 0.6, t, sfxGain, 35);
    for (let i = 0; i < 6; i++) toneAt(200 + rnd() * 700, 0.12, 'square', 0.16, t + rnd() * 0.12, sfxGain, 60 + rnd() * 200);
    for (let i = 0; i < 16; i++) noiseAt(0.05, 0.22, 6500 + rnd() * 2000, 5000, 'highpass', t + 0.05 + rnd() * 0.7, sfxGain);
    if (who === 'car') sfxScreech();
  }
  [[311, 0.32], [294, 0.32], [277, 0.32]].forEach((n, k) => brassAt(n[0], n[1], t + 1.05 + k * 0.36, 0.3, n[0] * 0.985));
  brassAt(262, 1.1, t + 2.13, 0.3, 205);                  // "wah wah wah waaah"
  if (who === 'person') {
    const p = HIT_PHRASES[Math.floor(rnd() * HIT_PHRASES.length)];
    setTimeout(() => speak(p[0], p[1], 1.0, 1.2), 1500);
  }
}

// ---- nhạc nền: 4 hợp âm Am - F - C - G, có trống, bass, pad và giai điệu ----
const CHORDS = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]], BASS = [45, 41, 48, 43];
const MELODY = [76, 0, 72, 0, 74, 0, 72, 0,  77, 0, 74, 0, 72, 0, 69, 0,
                76, 0, 79, 0, 76, 0, 72, 0,  74, 0, 71, 0, 74, 0, 79, 0];
let nextT = 0, stepI = 0, stepD = 0.115;

function noteAt(f, d, t, vol, type, c0, c1, dest, det) {
  const o = AC.createOscillator(), fl = AC.createBiquadFilter(), g = AC.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t); if (det) o.detune.value = det;
  fl.type = 'lowpass'; fl.frequency.setValueAtTime(c0, t); fl.frequency.exponentialRampToValueAtTime(c1, t + d);
  g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(fl); fl.connect(g); g.connect(dest); o.start(t); o.stop(t + d + 0.03);
}
function musicShouldPlay() { return scene !== 'over' && scene !== 'crash' && !(scene === 'play' && state.paused); }
function playStep(i, t) {
  const bar = Math.floor(i / 8) % 4, chord = CHORDS[bar], st = i % 8, m = musicGain;
  if (i % 4 === 0) { toneAt(160, 0.13, 'sine', 0.9, t, m, 45); noiseAt(0.015, 0.25, 4000, 4000, 'highpass', t, m); }
  if (i % 16 === 4 || i % 16 === 12) { noiseAt(0.14, 0.45, 2500, 1500, 'bandpass', t, m); toneAt(210, 0.09, 'triangle', 0.35, t, m, 120); }
  if (i % 2 === 0) noiseAt(0.04, i % 4 === 2 ? 0.16 : 0.09, 7500, 7500, 'highpass', t, m);
  if (i % 16 === 14) noiseAt(0.18, 0.13, 7000, 7000, 'highpass', t, m);
  if ([1, 0, 1, 0, 1, 1, 0, 1][st]) noteAt(m2f(BASS[bar] + (st === 5 ? 12 : 0)), stepD * 1.7, t, 0.5, 'sawtooth', 900, 200, m);
  if (st === 0) chord.forEach(n => noteAt(m2f(n), stepD * 8, t, 0.07, 'triangle', 1200, 1100, m, (rnd() - 0.5) * 10));
  const mel = MELODY[i % 32];
  if (mel) {
    noteAt(m2f(mel), stepD * 3.2, t, 0.16, 'square', 3200, 700, m);
    noteAt(m2f(mel), stepD * 3.2, t, 0.10, 'sawtooth', 2600, 600, m, 9);
  }
}
function scheduler() {
  if (!AC || AC.state !== 'running') return;
  if (nextT < AC.currentTime - 0.3) nextT = AC.currentTime + 0.05;
  while (nextT < AC.currentTime + 0.25) {
    const bpm = scene === 'play' ? Math.min(176, 122 + (state.speed - START_SPEED) / 14) : 122;
    stepD = 60 / bpm / 4;
    if (musicShouldPlay()) playStep(stepI, nextT);
    stepI++; nextT += stepD;
  }
}

// ---- động cơ / lốp / gió theo tốc độ, có sang số ----
const GEAR_LIM = [380, 540, 700, 880, 1100];
function audioTick() {
  if (!AC) return;
  const now = AC.currentTime, on = scene === 'play' && !state.paused, sp = state.speed;
  let gi = 0; while (gi < GEAR_LIM.length - 1 && sp >= GEAR_LIM[gi]) gi++;
  const lo = gi ? GEAR_LIM[gi - 1] : 200;
  const frac = Math.max(0, Math.min(1, (sp - lo) / (GEAR_LIM[gi] - lo)));
  const f = 58 + frac * 72 + gi * 9;
  if (scene === 'play') { if (!state.paused && gi > lastGear) sfxShift(); lastGear = gi; }
  engGain.gain.setTargetAtTime(on ? 0.14 : 0, now, 0.08);
  engA.frequency.setTargetAtTime(f, now, 0.06);
  engB.frequency.setTargetAtTime(f * 1.012, now, 0.06);
  engSub.frequency.setTargetAtTime(f * 0.5, now, 0.06);
  engFilt.frequency.setTargetAtTime(380 + frac * 450 + gi * 90, now, 0.1);
  roadGain.gain.setTargetAtTime(on ? Math.min(0.14, sp / 1100 * 0.14) : 0, now, 0.15);
  roadFilt.frequency.setTargetAtTime(220 + sp * 0.45, now, 0.2);
  windGain.gain.setTargetAtTime(on ? Math.max(0, (sp - 450) / 650 * 0.09) : 0, now, 0.2);
  windFilt.frequency.setTargetAtTime(900 + sp * 1.1, now, 0.2);
  if (!on) state.enemies.forEach(e => { if (e.voice) e.voice.g.gain.setTargetAtTime(0, now, 0.05); });
}

const btnM = document.getElementById('btnM');
btnM.addEventListener('click', () => {
  initAudio(); muted = !muted;
  if (master) master.gain.value = muted ? 0 : 0.85;
  btnM.textContent = muted ? '🔇' : '🔊';
  if (muted) stopSpeech();
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
    spawnTimer: 0, coinTimer: 0, coinCount: 0, roadOffset: state ? state.roadOffset : 0,
    fx: null, scenery: makeScenery(), sceneryAcc: 0
  };
}
reset();

function startGame() { endAllVoices(); stopSpeech(); lastGear = 0; ambT = 4; reset(); scene = 'play'; sfxStart(); }
function toMenu() { endAllVoices(); stopSpeech(); scene = 'menu'; state.paused = false; }
function gameOver(e) {
  lastRank = addScore(state.score, state.coinCount);
  const living = e.kind === 'emoji' && !!e.walk;          // người / động vật
  const px = state.x + CAR_W / 2, py = state.y + CAR_H / 2;
  const ex = e.x + e.w / 2, ey = e.y + e.h / 2;
  state.fx = makeFx(living ? 'blood' : 'boom', (px + ex) / 2, (py + ey) / 2);
  if (e.kind === 'car') { e.wreck = true; e.rot = (Math.random() - 0.5) * 0.9; }
  else e.dead = true;
  state.fx.spin = living ? 0 : (Math.random() < 0.5 ? -1 : 1) * (0.25 + Math.random() * 0.35);
  scene = 'crash';
  endAllVoices();
  sfxCrash(living, e.snd);
}
const menuActions = [startGame, () => { scene = 'scores'; }, () => { scene = 'help'; }, () => { scene = 'name'; }];
const menuLabels = ['▶  Chơi ngay', '🏆  Điểm cao', '❓  Hướng dẫn', '✏️  Đổi tên'];

// =====================================================================
//  CHƯỚNG NGẠI VẬT
// =====================================================================
const OBSTACLES = [
  { kind: 'car', snd: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 5 },
  { kind: 'car', snd: 'car', w: CAR_W, h: CAR_H, pad: 6, weight: 3 },
  { kind: 'emoji', snd: 'person', e: '🚶', w: 28, h: 50, size: 46, pad: 3, weight: 2, walk: 55 },
  { kind: 'emoji', snd: 'dog', e: '🐕', w: 44, h: 32, size: 40, pad: 3, weight: 2, walk: 100 },
  { kind: 'emoji', snd: 'cat', e: '🐈', w: 34, h: 30, size: 34, pad: 3, weight: 2, walk: 85 },
  { kind: 'emoji', snd: 'cow', e: '🐄', w: 50, h: 40, size: 46, pad: 4, weight: 1, walk: 35 },
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
//  HIỆU ỨNG VA CHẠM + CÂY CỎ
// =====================================================================
function makeFx(kind, x, y) {
  const fx = { kind, x, y, t: 0, parts: [], stains: [], spin: 0 };
  if (kind === 'boom') {
    fx.stains.push({ x, y, r: 34, c: 'rgba(0,0,0,0.45)' });
    for (let i = 0; i < 45; i++) {
      const a = rnd() * 6.283, sp = 40 + rnd() * 260, l = 0.35 + rnd() * 0.7;
      fx.parts.push({ t: 'fire', x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, life: l, max: l, size: 6 + rnd() * 12 });
    }
    for (let i = 0; i < 22; i++) {
      const l = 1.2 + rnd() * 1.8;
      fx.parts.push({ t: 'smoke', x: x + (rnd() - 0.5) * 20, y, vx: (rnd() - 0.5) * 40, vy: -20 - rnd() * 50, life: l, max: l, size: 10 + rnd() * 14 });
    }
    for (let i = 0; i < 16; i++) {
      const a = rnd() * 6.283, sp = 80 + rnd() * 240, l = 0.8 + rnd() * 0.8;
      fx.parts.push({ t: 'debris', x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 80, g: 500, life: l, max: l, rot: 0, vr: (rnd() - 0.5) * 20 });
    }
  } else {
    for (let i = 0; i < 55; i++) {
      const a = rnd() * 6.283, sp = 60 + rnd() * 300, l = 0.5 + rnd() * 0.7;
      fx.parts.push({ t: 'blood', x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, g: 420, life: l, max: l, size: 2 + rnd() * 4 });
    }
    fx.stains.push({ x, y, r: 20 });
    for (let i = 0; i < 9; i++) fx.stains.push({ x: x + (rnd() - 0.5) * 70, y: y + (rnd() - 0.5) * 60, r: 5 + rnd() * 16 });
  }
  return fx;
}
function updateFx(dt) {
  const fx = state.fx; if (!fx) return;
  fx.t += dt;
  if (fx.kind === 'boom') {
    if (fx.t < 2.6 && rnd() < dt * 35)
      fx.parts.push({ t: 'smoke', x: fx.x + (rnd() - 0.5) * 26, y: fx.y + (rnd() - 0.5) * 20, vx: (rnd() - 0.5) * 25, vy: -30 - rnd() * 40, life: 1.5, max: 1.5, size: 9 + rnd() * 10 });
    if (fx.t < 1.6 && rnd() < dt * 30)
      fx.parts.push({ t: 'fire', x: fx.x + (rnd() - 0.5) * 24, y: fx.y + (rnd() - 0.5) * 18, vx: (rnd() - 0.5) * 30, vy: -40 - rnd() * 40, life: 0.5, max: 0.5, size: 6 + rnd() * 6 });
  }
  for (const p of fx.parts) {
    p.x += p.vx * dt; p.y += p.vy * dt;
    if (p.g) p.vy += p.g * dt;
    if (p.rot !== undefined) p.rot += p.vr * dt;
    p.life -= dt;
    if (p.life <= 0 && p.t === 'blood' && fx.stains.length < 160) fx.stains.push({ x: p.x, y: p.y, r: 1.5 + rnd() * 3 });
  }
  fx.parts = fx.parts.filter(p => p.life > 0);
}
function circ(x, y, r, col) { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); }
function ell(x, y, rx, ry, col) { ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x, y, rx, ry, 0, 0, 7); ctx.fill(); }
function tri(ax, ay, bx, by, cx, cy, col) {
  ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.lineTo(cx, cy); ctx.closePath(); ctx.fill();
}
function drawStains() {
  const fx = state.fx; if (!fx) return;
  for (const st of fx.stains) circ(st.x, st.y, st.r, st.c || 'rgba(140,0,0,0.9)');
}
function drawFxParticles() {
  const fx = state.fx; if (!fx) return;
  if (fx.kind === 'boom' && fx.t < 0.45) {
    const k = fx.t / 0.45;
    circ(fx.x, fx.y, 30 + k * 50, 'rgba(255,240,200,' + (0.9 * (1 - k)) + ')');
    ctx.strokeStyle = 'rgba(255,200,100,' + (1 - k) + ')'; ctx.lineWidth = 6 * (1 - k) + 1;
    ctx.beginPath(); ctx.arc(fx.x, fx.y, 20 + k * 140, 0, 7); ctx.stroke();
  }
  for (const p of fx.parts) {
    const a = Math.max(0, p.life / p.max);
    if (p.t === 'fire') {
      const col = a > 0.6 ? 'rgba(255,240,120,' : a > 0.3 ? 'rgba(255,140,30,' : 'rgba(200,40,20,';
      circ(p.x, p.y, p.size * (0.4 + a * 0.8), col + a + ')');
    } else if (p.t === 'smoke') {
      circ(p.x, p.y, p.size * (1.6 - a), 'rgba(70,70,70,' + (a * 0.6) + ')');
    } else if (p.t === 'debris') {
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.fillStyle = '#222'; ctx.fillRect(-3, -2, 6, 4); ctx.restore();
    } else {
      circ(p.x, p.y, p.size, 'rgba(190,20,20,' + Math.min(1, a * 1.5) + ')');
    }
  }
  if (fx.kind === 'blood' && fx.t < 0.35) {
    ctx.fillStyle = 'rgba(180,0,0,' + (0.35 * (1 - fx.t / 0.35)) + ')'; ctx.fillRect(0, 0, W, H);
  }
}
function drawWreck(x, y, rot, color, player) {
  ctx.save();
  ctx.translate(x + CAR_W / 2, y + CAR_H / 2); ctx.rotate(rot);
  drawCar(-CAR_W / 2, -CAR_H / 2, color, player);
  ctx.fillStyle = 'rgba(15,15,15,0.62)'; ctx.beginPath(); ctx.roundRect(-CAR_W / 2, -CAR_H / 2, CAR_W, CAR_H, 8); ctx.fill();
  ctx.strokeStyle = '#000'; ctx.lineWidth = 2; ctx.beginPath();
  ctx.moveTo(-14, -30); ctx.lineTo(-4, -14); ctx.lineTo(-12, -2); ctx.lineTo(2, 12);
  ctx.moveTo(12, -20); ctx.lineTo(4, -6); ctx.lineTo(14, 8); ctx.stroke();
  ctx.restore();
}

// cây cỏ hai bên đường
function addScen(list, y) {
  [-1, 1].forEach(side => {
    if (rnd() > 0.85) return;
    const r = rnd(), t = r < 0.35 ? 'tree' : r < 0.55 ? 'pine' : r < 0.8 ? 'bush' : 'flower';
    const sz = (t === 'tree' || t === 'pine') ? 15 + rnd() * 7 : t === 'bush' ? 9 + rnd() * 5 : 3 + rnd() * 2;
    const lo = sz + 2, hi = Math.max(lo, ROAD_X - sz - 6);
    const cx = lo + rnd() * (hi - lo);
    list.push({ x: side < 0 ? cx : W - cx, y: y + rnd() * 10, t, s: sz, c: ['#ffffff', '#ffeb3b', '#f48fb1', '#ff8a65'][Math.floor(rnd() * 4)] });
  });
}
function makeScenery() { const a = []; for (let y = -40; y < H + 60; y += 46) addScen(a, y); return a; }
function moveScenery(d) {
  const s = state;
  for (const o of s.scenery) o.y += d;
  s.scenery = s.scenery.filter(o => o.y < H + 70);
  s.sceneryAcc += d;
  while (s.sceneryAcc >= 46) { s.sceneryAcc -= 46; addScen(s.scenery, -50 + s.sceneryAcc); }
}
function drawScenery() {
  for (const o of state.scenery) {
    const x = o.x, y = o.y, s = o.s;
    if (o.t === 'tree') {
      ell(x + 3, y + s * 0.75, s * 0.9, s * 0.35, 'rgba(0,0,0,0.25)');
      ctx.fillStyle = '#5d4037'; ctx.fillRect(x - 3, y - 2, 6, s * 0.8);
      circ(x, y - s * 0.35, s, '#2e7d32'); circ(x - s * 0.3, y - s * 0.5, s * 0.6, '#43a047'); circ(x + s * 0.3, y - s * 0.6, s * 0.35, '#66bb6a');
    } else if (o.t === 'pine') {
      ctx.fillStyle = '#5d4037'; ctx.fillRect(x - 2, y + s * 0.4, 4, s * 0.5);
      tri(x, y - s * 1.1, x - s * 0.8, y - s * 0.1, x + s * 0.8, y - s * 0.1, '#1b5e20');
      tri(x, y - s * 0.6, x - s * 0.95, y + s * 0.5, x + s * 0.95, y + s * 0.5, '#2e7d32');
    } else if (o.t === 'bush') {
      ell(x, y, s * 1.1, s * 0.75, '#388e3c'); ell(x - s * 0.3, y - s * 0.2, s * 0.6, s * 0.45, '#66bb6a');
    } else {
      circ(x - 4, y, s * 0.7, o.c); circ(x + 4, y + 2, s * 0.7, o.c); circ(x, y - 4, s * 0.7, o.c); circ(x, y, s * 0.5, '#fdd835');
    }
  }
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
  if (e.dead) return;
  if (e.kind === 'car') {
    if (e.wreck) drawWreck(e.x, e.y, e.rot * Math.min(1, state.fx.t * 3), e.color, false);
    else drawCar(e.x, e.y, e.color, false);
    return;
  }
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
  ctx.fillStyle = '#388e3c';
  for (let y = -80 + (state.roadOffset % 80); y < H; y += 80) {
    ctx.fillRect(0, y, ROAD_X, 40); ctx.fillRect(ROAD_X + ROAD_W, y, W - ROAD_X - ROAD_W, 40);
  }
  ctx.fillStyle = '#3a3a3a'; ctx.fillRect(ROAD_X, 0, ROAD_W, H);
  ctx.fillStyle = '#fff'; ctx.fillRect(ROAD_X - 4, 0, 4, H); ctx.fillRect(ROAD_X + ROAD_W, 0, 4, H);
  ctx.fillStyle = '#ddd';
  for (let l = 1; l < LANES; l++)
    for (let y = -40 + (state.roadOffset % 40); y < H; y += 40)
      ctx.fillRect(ROAD_X + l * LANE_W - 2, y, 4, 20);
  drawScenery();
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
  const fx = state.fx;
  if (scene === 'crash' && fx) {
    const m = 12 * Math.max(0, 1 - fx.t / 0.6);
    ctx.save(); ctx.translate((rnd() - 0.5) * m, (rnd() - 0.5) * m);
    drawSceneInner(); ctx.restore();
  } else drawSceneInner();
}
function drawSceneInner() {
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
                   'Tránh xe, người, chó mèo, chướng ngại', 'Xe càng chạy càng nhanh', 'H hoặc nút 📢 : bấm còi • 🔊 : bật/tắt tiếng',
                   'Điện thoại: dùng 2 nút bên dưới'];
    lines.forEach((l, i) => text(l, W / 2, 145 + i * 40, 17, '#eee'));
    button('⬅ Quay lại', 100, H - 80, 200, 46, toMenu, true);
    return;
  }

  // play / crash / over
  drawStains();
  for (const c of state.coins) {
    ctx.fillStyle = '#ffd700'; ctx.beginPath(); ctx.arc(c.x, c.y, 10, 0, 7); ctx.fill();
    ctx.strokeStyle = '#b8860b'; ctx.lineWidth = 2; ctx.stroke();
  }
  for (const e of state.enemies) drawObstacle(e);
  const fx = state.fx;
  if (fx && fx.kind === 'boom') {
    drawWreck(state.x, state.y, fx.spin * Math.min(1, fx.t * 3), '#d32f2f', true);
  } else {
    const tilt = (state.toX - state.x) / LANE_W * 0.35;
    ctx.save();
    ctx.translate(state.x + CAR_W / 2, state.y + CAR_H / 2);
    ctx.rotate(tilt);
    drawCar(-CAR_W / 2, -CAR_H / 2, '#d32f2f', true);
    if (fx) {                                            // máu bắn lên đầu xe
      circ(-8, -CAR_H / 2 + 6, 5, '#b71c1c'); circ(9, -CAR_H / 2 + 12, 4, '#c62828');
      circ(0, -CAR_H / 2 + 20, 6, '#8e0000'); circ(-12, -CAR_H / 2 + 24, 3, '#b71c1c');
    }
    ctx.restore();
  }
  drawFxParticles();
  drawHUD();

  if (scene === 'over') {
    overlay(0.6);
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
  if (scene === 'crash' || scene === 'over') {
    updateFx(dt);
    if (scene === 'crash' && s.fx && s.fx.t > 1.6) scene = 'over';
    return;
  }
  if (scene !== 'play') { s.roadOffset += 120 * dt; moveScenery(120 * dt); return; }
  if (s.paused) return;

  ambT -= dt;
  if (ambT <= 0) { sfxAmbientTraffic(); ambT = 5 + rnd() * 8; }

  s.t = Math.min(1, s.t + dt / LANE_TIME);
  s.x = s.fromX + (s.toX - s.fromX) * easeInOut(s.t);

  s.speed = Math.min(MAX_SPEED, s.speed + dt * ACCEL);
  s.dist += s.speed * dt;
  s.roadOffset += s.speed * dt;
  moveScenery(s.speed * dt);

  s.spawnTimer -= dt;
  if (s.spawnTimer <= 0) { spawnEnemy(); s.spawnTimer = Math.max(0.3, 1.1 - s.speed / 1400) * (0.6 + Math.random() * 0.8); }
  s.coinTimer -= dt;
  if (s.coinTimer <= 0) { spawnCoin(); s.coinTimer = 1.5 + Math.random() * 2; }

  for (const e of s.enemies) {
    e.y += (s.speed - e.v) * dt;
    if (e.kind === 'car') { ensureCarVoice(e); updateCarVoice(e); }
    if (!e.said && e.y > 30) { e.said = true; ambientSound(e); }
    if (e.kind === 'car' && !e.passed && e.y > s.y + CAR_H) {
      e.passed = true;
      if (Math.abs(laneOf(e) - s.lane) <= 1) sfxPass();
    }
    if (e.vx) {
      e.x += e.vx * dt;
      const minX = ROAD_X + 2, maxX = ROAD_X + ROAD_W - e.w - 2;
      if (e.x < minX) { e.x = minX; e.vx = Math.abs(e.vx); }
      if (e.x > maxX) { e.x = maxX; e.vx = -Math.abs(e.vx); }
    }
  }
  for (const c of s.coins) c.y += s.speed * dt;
  for (const e of s.enemies) if (e.y >= H + 100) endVoice(e);
  s.enemies = s.enemies.filter(e => e.y < H + 100);
  s.coins = s.coins.filter(c => c.y < H + 30);

  s.coins = s.coins.filter(c => {
    if (Math.abs(c.x - (s.x + CAR_W / 2)) < 26 && Math.abs(c.y - (s.y + CAR_H / 2)) < 45) {
      s.coinCount++; sfxCoin(); return false;
    }
    return true;
  });
  s.score = Math.floor(s.dist / SCORE_DIV) + s.coinCount * COIN_BONUS;
  for (const e of s.enemies) if (hit({ x: s.x, y: s.y }, e)) { gameOver(e); break; }
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
    else if (!e.repeat && (k === 'h' || k === 'H') && !state.paused) sfxHonk(0, sfxGain, 0.3);
    else if (state.paused && (k === 'm' || k === 'M')) toMenu();
  } else if (scene === 'over') {
    if (k === 'Enter' || k === ' ') startGame();
    else if (k === 'Escape' || k === 'm' || k === 'M') toMenu();
  } else if (scene === 'crash') {
    if (k === 'Enter' || k === ' ') scene = 'over';
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
document.getElementById('btnH').addEventListener('click', () => { initAudio(); if (scene === 'play' && !state.paused) sfxHonk(0, sfxGain, 0.3); canvas.focus(); });
</script>
"""

components.html(GAME_HTML, height=740, scrolling=False)
