import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Race Master 3D Clone")

st.title("🏎️ Siêu Game Đua Xe 3D - Race Master Style")
st.write("Dùng phím **Mũi tên Trái (⬅️) / Phải (➡️)** để đánh lái né xe đối thủ trên đường đua hẻm núi!")

# Giao diện điều khiển cấu hình bên cạnh
col_ctrl, col_game = st.columns([1, 3])

with col_ctrl:
    st.subheader("🏆 Phòng Điều Khiển")
    player_color = st.color_picker("Đổi màu xe của bạn:", "#ffcc00")
    speed_boost = st.slider("Cấu hình Nitro tối đa (km/h):", 150, 300, 220, step=10)
    st.info("💡 Mẹo: Né các xe màu xanh và màu đen để không bị nổ lốp!")

# Mã nguồn Three.js dựng đồ họa mô phỏng hẻm núi núi đất sét và xe đua F1
game_source_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cloudflare.com"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #87CEEB; font-family: sans-serif; }}
        canvas {{ display: block; width: 100vw; height: 85vh; }}
        #hud {{
            position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
            color: #fff; font-size: 24px; font-weight: bold; text-align: center;
            background: rgba(0,0,0,0.6); padding: 10px 30px; border-radius: 20px;
            box-shadow: 0 0 15px rgba(255,255,255,0.3); border: 2px solid #fff;
        }}
        .btn-ui {{
            position: absolute; bottom: 40px; width: 70px; height: 70px;
            background: rgba(255,255,255,0.2); border: 3px solid #fff; border-radius: 50%;
            display: flex; align-items: center; justify-content: center; font-size: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }}
        #shield {{ left: 40px; }}
        #nitro {{ right: 40px; }}
    </style>
</head>
<body>
    <div id="hud">🏁 LEVEL 1 <br> <span style="color: #ffcc00;" id="speed-text">0</span> KM/H</div>
    <div id="shield" class="btn-ui">🛡️</div>
    <div id="nitro" class="btn-ui">⚡</div>

    <script>
        let scene, camera, renderer, playerCar;
        let opponents = [];
        let roadStripes = [];
        let gameSpeed = 1.2;
        let maxSpeed = {speed_boost} / 100;
        let currentSpeed = 0;
        let isMovingLeft = false, isMovingRight = false;
        let gameOver = false;

        function init() {{
            // 1. Khởi tạo môi trường đồ họa & bầu trời bầu không khí
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xfca060); // Màu hẻm núi hoàng hôn rực rỡ
            scene.fog = new THREE.FogExp2(0xfca060, 0.015);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 3.2, 7.5); // Góc nhìn cao từ phía sau chuẩn Race Master
            camera.lookAt(0, 1, -5);

            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // 2. Tạo đường đua chạy dài vô tận và vách núi hai bên
            const roadGeo = new THREE.PlaneGeometry(12, 1000);
            const roadMat = new THREE.MeshStandardMaterial({{ color: 0x444446, roughness: 0.7 }});
            const road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            scene.add(road);

            // Tạo vách núi màu cam sa mạc hai bên đường
            for (let i = 0; i < 20; i++) {{
                const wallGeo = new THREE.BoxGeometry(15, 25, 50);
                const wallMat = new THREE.MeshStandardMaterial({{ color: 0xd97d41, roughness: 0.9 }});
                
                const leftWall = new THREE.Mesh(wallGeo, wallMat);
                leftWall.position.set(-14, 8, -i * 50);
                scene.add(leftWall);

                const rightWall = new THREE.Mesh(wallGeo, wallMat);
                rightWall.position.set(14, 8, -i * 50);
                scene.add(rightWall);
            }}

            // Tạo vạch kẻ đường ở giữa
            for (let i = 0; i < 30; i++) {{
                const stripeGeo = new THREE.PlaneGeometry(0.3, 4);
                const stripeMat = new THREE.MeshBasicMaterial({{ color: 0xffe600 }});
                const stripe = new THREE.Mesh(stripeGeo, stripeMat);
                stripe.rotation.x = -Math.PI / 2;
                stripe.position.set(0, 0.02, -i * 15);
                scene.add(stripe);
                roadStripes.push(stripe);
            }}

            // 3. Dựng xe đua F1 của người chơi (Ghép từ nhiều khối 3D chi tiết)
            playerCar = createF1Car('{player_color}');
            playerCar.position.set(0, 0, 2);
            scene.add(playerCar);

            // 4. Hệ thống ánh sáng cường độ cao
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
            dirLight.position.set(5, 20, 10);
            scene.add(dirLight);

            // 5. Khởi tạo xe đối thủ ngẫu nhiên chạy trên các làn đường
            spawnOpponents();

            // Nhận diện bấm phím di chuyển đánh lái
            window.addEventListener('keydown', (e) => {{
                if (e.key === 'ArrowLeft') isMovingLeft = true;
                if (e.key === 'ArrowRight') isMovingRight = true;
            }});
            window.addEventListener('keyup', (e) => {{
                if (e.key === 'ArrowLeft') isMovingLeft = false;
                if (e.key === 'ArrowRight') isMovingRight = false;
            }});

            animate();
        }}

        // Hàm ghép linh kiện thành một chiếc xe đua F1 siêu thể thao
        function createF1Car(colorHex) {{
            const carGroup = new THREE.Group();
            
            // Thân xe chính dài và dẹt
            const bodyGeo = new THREE.BoxGeometry(1.3, 0.4, 2.8);
            const bodyMat = new THREE.MeshStandardMaterial({{ color: colorHex, metalness: 0.6, roughness: 0.1 }});
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 0.35;
            carGroup.add(body);

            // Cánh gió phía sau (Spoiler) cao hẳn lên
            const spoilerGeo = new THREE.BoxGeometry(1.8, 0.1, 0.5);
            const spoilerMat = new THREE.MeshStandardMaterial({{ color: 0x111111 }});
            const spoiler = new THREE.Mesh(spoilerGeo, spoilerMat);
            spoiler.position.set(0, 0.9, 1.2);
            carGroup.add(spoiler);

            const spoilerLegGeo = new THREE.BoxGeometry(0.1, 0.6, 0.2);
            const legLeft = new THREE.Mesh(spoilerLegGeo, spoilerMat);
            legLeft.position.set(-0.6, 0.6, 1.2);
            const legRight = legLeft.clone();
            legRight.position.x = 0.6;
            carGroup.add(legLeft, legRight);

            // Bánh xe 3D dày cộm ở 4 góc
            const wheelGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.5, 16);
            const wheelMat = new THREE.MeshStandardMaterial({{ color: 0x222222, roughness: 0.9 }});
            
            const positions = [
                [-0.85, 0.45, -0.9], [0.85, 0.45, -0.9], // Hai bánh trước
                [-0.9, 0.45, 0.9], [0.9, 0.45, 0.9]     // Hai bánh sau
            ];

            positions.forEach(pos => {{
                const wheel = new THREE.Mesh(wheelGeo, wheelMat);
                wheel.rotation.z = Math.PI / 2;
                wheel.position.set(pos[0], pos[1], pos[2]);
                carGroup.add(wheel);
            }});

            return carGroup;
        }}

        function spawnOpponents() {{
            if (gameOver) return;
            const colors = [0x1e3d59, 0x111111, 0xff6f61]; // Các màu xe đối thủ (xanh, đen)
            const lanes = [-3.8, 0, 3.8];
            
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            const randomLane = lanes[Math.floor(Math.random() * lanes.length)];
            
            const oppCar = createF1Car(randomColor);
            oppCar.position.set(randomLane, 0, -80);
            scene.add(oppCar);
            opponents.push(oppCar);

            setTimeout(spawnOpponents, 1800); // Cứ mỗi 1.8 giây sinh ra 1 xe đối thủ cản đường
        }}

        function animate() {{
            if (gameOver) return;
            requestAnimationFrame(animate);

            // Tăng tốc dần đều từ 0 lên tốc độ tối đa cấu hình
            if (currentSpeed < maxSpeed) currentSpeed += 0.05;
            document.getElementById('speed-text').innerText = Math.round(currentSpeed * 100);

            // Xử lý di chuyển xe mượt mà và giới hạn lề đường đua
            if (isMovingLeft && playerCar.position.x > -4.5) playerCar.position.x -= 0.18;
            if (isMovingRight && playerCar.position.x < 4.5) playerCar.position.x += 0.18;

            // Camera lắc nhẹ góc nhìn theo vị trí xe đua
            camera.position.x = playerCar.position.x * 0.4;

            // Chạy vạch kẻ đường tạo cảm giác xe di chuyển siêu tốc
            roadStripes.forEach(stripe => {{
                stripe.position.z += currentSpeed;
                if (stripe.position.z > 10) stripe.position.z = -120;
            }});

            // Cập nhật và kiểm tra va chạm xe đối thủ
            for (let i = opponents.length - 1; i >= 0; i--) {{
                let opp = opponents[i];
                opp.position.z += (currentSpeed - 0.4); // Xe đối thủ đi chậm hơn xe mình tạo cảm giác mình đang đuổi vượt

                // Thuật toán kiểm tra va chạm vật thể 3D giữa xe ta và xe địch
                if (Math.abs(playerCar.position.x - opp.position.x) < 1.5 && Math.abs(playerCar.position.z - opp.position.z) < 2.5) {{
                    gameOver = true;
                    alert("💥 BẠN ĐÃ VA CHẠM VÀO XE KHÁC! Trò chơi sẽ tải lại.");
                    location.reload();
                }}

