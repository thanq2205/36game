import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Retro Neon Racing 2D", layout="centered")

st.title("⚡ Đua Xe Cổ Điển: Neon Horizon")
st.write("Sử dụng phím **Mũi tên Trái (⬅️) / Phải (➡️)** hoặc chạm màn hình để đánh lái né xe cảnh sát!")

# Đoạn mã xử lý game engine 2D Canvas mượt mà, đồ họa Neon cực chất
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background-color: #0b0b1e; display: flex; justify-content: center; align-items: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        canvas { border: 4px solid #00f3ff; border-radius: 12px; box-shadow: 0 0 20px #00f3ff; background: #12122c; max-width: 100%; }
        #game-container { position: relative; text-align: center; }
        .score-board { position: absolute; top: 15px; left: 15px; color: #fff; font-size: 20px; font-weight: bold; text-shadow: 0 0 8px #00f3ff; font-family: monospace; background: rgba(0,0,0,0.4); padding: 5px 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div id="game-container">
        <div class="score-board">SCORE: <span id="scoreVal">0</span></div>
        <canvas id="gameCanvas" width="400" height="550"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Cấu hình vật thể
        let player = { x: 175, y: 450, w: 50, h: 80, speed: 6 };
        let obstacles = [];
        let score = 0;
        let gameSpeed = 5;
        let gameOver = false;
        let trackOffset = 0;

        // Trạng thái phím bấm
        let keys = { ArrowLeft: false, ArrowRight: false };

        window.addEventListener("keydown", e => { if(e.key in keys) keys[e.key] = true; });
        window.addEventListener("keyup", e => { if(e.key in keys) keys[e.key] = false; });

        // Hỗ trợ chơi trên điện thoại (Chạm nửa màn hình trái/phải để rẽ)
        canvas.addEventListener("touchstart", e => {
            let touchX = e.touches[0].clientX - canvas.getBoundingClientRect().left;
            if(touchX < canvas.width / 2) keys.ArrowLeft = true;
            else keys.ArrowRight = true;
        });
        canvas.addEventListener("touchend", () => { keys.ArrowLeft = false; keys.ArrowRight = false; });

        function spawnObstacle() {
            if (gameOver) return;
            // Chia làm 3 làn đường chính
            const lanes =;
            const randomLane = lanes[Math.floor(Math.random() * lanes.length)];
            
            // Không sinh xe quá sát nhau ở cùng một làn
            if(obstacles.length === 0 || obstacles[obstacles.length - 1].y > 200) {
                obstacles.push({ x: randomLane, y: -100, w: 50, h: 80, color: "#ff0055" });
            }
            setTimeout(spawnObstacle, Math.max(1000, 2000 - score * 5));
        }

        function checkCollision(rect1, rect2) {
            return rect1.x < rect2.x + rect2.w &&
                   rect1.x + rect1.w > rect2.x &&
                   rect1.y < rect2.y + rect2.h &&
                   rect1.y + rect1.h > rect2.y;
        }

        function update() {
            if (gameOver) return;

            // Xử lý di chuyển mượt mà của người chơi
            if (keys.ArrowLeft && player.x > 30) player.x -= player.speed;
            if (keys.ArrowRight && player.x < canvas.width - 30 - player.w) player.x += player.speed;

            // Cuộn hiệu ứng đường đua động
            trackOffset += gameSpeed;
            if (trackOffset >= 40) trackOffset = 0;

            // Di chuyển và xử lý chướng ngại vật
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.y += gameSpeed;

                // Kiểm tra va chạm pixel
                if (checkCollision(player, obs)) {
                    gameOver = true;
                    ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = "#ff0055";
                    ctx.font = "bold 35px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("💥 TAI NẠN RỒI!", canvas.width/2, canvas.height/2 - 20);
                    ctx.fillStyle = "#fff";
                    ctx.font = "18px sans-serif";
                    ctx.fillText("Chạm màn hình hoặc F5 để chơi lại", canvas.width/2, canvas.height/2 + 30);
                    
                    canvas.addEventListener("click", () => location.reload(), {once: true});
                    return;
                }

                // Đi qua an toàn
                if (obs.y > canvas.height) {
                    obstacles.splice(i, 1);
                    score += 10;
                    document.getElementById("scoreVal").innerText = score;
                    if(score % 50 === 0) gameSpeed += 0.5; // Tăng dần độ khó tốc độ
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ lề đường Neon uốn lượn
            ctx.strokeStyle = "#00f3ff";
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.moveTo(25, 0); ctx.lineTo(25, canvas.height);
            ctx.moveTo(canvas.width - 25, 0); ctx.lineTo(canvas.width - 25, canvas.height);
            ctx.stroke();

            // 2. Vẽ vạch kẻ phân làn chuyển động động
            ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
            ctx.lineWidth = 4;
            ctx.setLineDash([25, 15]);
            
            ctx.beginPath();
            ctx.moveTo(135, trackOffset - 40); ctx.lineTo(135, canvas.height + 40);
            ctx.moveTo(265, trackOffset - 40); ctx.lineTo(265, canvas.height + 40);
            ctx.stroke();
            ctx.setLineDash([]); // Reset line dash

            // 3. Vẽ chiếc xe của người chơi (Thiết kế phong cách Cyberpunk Cybercar)
            ctx.fillStyle = "#00ff66"; // Thân xe màu xanh neon phát sáng
            ctx.shadowBlur = 15;
            ctx.shadowColor = "#00ff66";
            ctx.fillRect(player.x, player.y, player.w, player.h);
            
            // Kính chắn gió và đèn xe
            ctx.fillStyle = "#111";
            ctx.fillRect(player.x + 5, player.y + 20, player.w - 10, 20);
            ctx.fillStyle = "#fff";
            ctx.fillRect(player.x + 5, player.y + 5, 10, 5);
            ctx.fillRect(player.x + player.w - 15, player.y + 5, 10, 5);

            // 4. Vẽ các xe đối thủ cản đường
            obstacles.forEach(obs => {
                ctx.fillStyle = obs.color;
                ctx.shadowBlur = 15;
                ctx.shadowColor = obs.color;
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                
                // Chi tiết xe đối thủ
                ctx.fillStyle = "#111";
                ctx.fillRect(obs.x + 5, obs.y + 40, obs.w - 10, 20);
                ctx.fillStyle = "#ffea00";
                ctx.fillRect(obs.x + 5, obs.y + 70, 10, 5);
                ctx.fillRect(obs.x + obs.w - 15, obs.y + 70, 10, 5);
            });
            
            ctx.shadowBlur = 0; // Reset hiệu ứng phát sáng cho khung hình sau
        }

        function gameLoop() {
            update();
            draw();
            if (!gameOver) requestAnimationFrame(gameLoop);
        }

        spawnObstacle();
        gameLoop();
    </script>
</body>
</html>
"""

# Nhúng thẳng khung game mượt này vào giao diện Streamlit
components.html(game_html, height=600, scrolling=False)
