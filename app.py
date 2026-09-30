import streamlit as st
import random
import time

st.set_page_config(page_title="Game Đua Xe 2D Arcade", layout="centered")

st.title("🏎️ Game Đua Xe 2D Cổ Điển")
st.write("Dùng các nút bấm trên màn hình hoặc phím **A (Sang trái) / D (Sang phải)** trên bàn phím để né chướng ngại vật!")

# 1. Khởi tạo trạng thái game (Session State)
ROAD_WIDTH = 5
ROAD_HEIGHT = 8

if "car_pos" not in st.session_state:
    st.session_state.car_pos = 2  # Vị trí xe người chơi (nằm giữa từ 0 đến 4)
    st.session_state.obstacles = []  # Danh sách chướng ngại vật [(x, y)]
    st.session_state.score = 0
    st.session_state.game_over = False

# 2. Xử lý Logic Game khi người chơi bấm nút hành động
def game_tick(move_dir=None):
    if st.session_state.game_over:
        return

    # Xử lý di chuyển xe của người chơi
    if move_dir == "LEFT" and st.session_state.car_pos > 0:
        st.session_state.car_pos -= 1
    elif move_dir == "RIGHT" and st.session_state.car_pos < ROAD_WIDTH - 1:
        st.session_state.car_pos += 1

    # Di chuyển các chướng ngại vật hiện tại xuống 1 bước
    updated_obstacles = []
    for (obs_x, obs_y) in st.session_state.obstacles:
        new_y = obs_y + 1
        # Nếu chưa trôi ra khỏi màn hình thì giữ lại
        if new_y < ROAD_HEIGHT:
            updated_obstacles.append((obs_x, new_y))
        else:
            st.session_state.score += 10  # Né thành công cộng 10 điểm

    # Ngẫu nhiên sinh ra chướng ngại vật mới ở hàng trên cùng (y=0)
    if random.random() < 0.4 or len(updated_obstacles) == 0:
        new_x = random.randint(0, ROAD_WIDTH - 1)
        # Tránh sinh vật thể trùng nhau ở hàng trên cùng
        if not any(obs[1] == 0 for obs in updated_obstacles):
            updated_obstacles.append((new_x, 0))

    st.session_state.obstacles = updated_obstacles

    # Kiểm tra va chạm (Nếu vị trí xe trùng với bất kỳ vật cản nào ở hàng cuối cùng)
    for (obs_x, obs_y) in st.session_state.obstacles:
        if obs_y == ROAD_HEIGHT - 1 and obs_x == st.session_state.car_pos:
            st.session_state.game_over = True

# 3. Giao diện hiển thị điểm số và nút bấm điều khiển
col_info, col_reset = st.columns([2, 1])
with col_info:
    st.subheader(f"🏆 Điểm số: {st.session_state.score}")
with col_reset:
    if st.button("🔄 Chơi lại", use_container_width=True):
        st.session_state.car_pos = 2
        st.session_state.obstacles = []
        st.session_state.score = 0
        st.session_state.game_over = False
        st.rerun()

if st.session_state.game_over:
    st.error("💥 BÙM! Bạn đã đâm sầm vào chướng ngại vật. Hãy bấm 'Chơi lại' để phục thù!")

# Cụm điều khiển đánh lái trái/phải
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    if st.button("⬅️ Trái", on_click=game_tick, args=("LEFT",), use_container_width=True):
        pass
with c2:
    # Nút bấm tiến lên để chạy tiếp (khi không cần rẽ)
    if st.button("🚀 Lao lên phía trước", on_click=game_tick, use_container_width=True):
        pass
with c3:
    if st.button("Phải ➡️", on_click=game_tick, args=("RIGHT",), use_container_width=True):
        pass

# 4. Dựng đồ họa lưới đường đua 2D bằng HTML/CSS
grid_html = "<div style='display: grid; grid-template-columns: repeat(" + str(ROAD_WIDTH) + ", 1fr); gap: 4px; max-width: 320px; margin: 10px auto; background-color: #333; padding: 10px; border-left: 5px dashed white; border-right: 5px dashed white;'>"

for y in range(ROAD_HEIGHT):
    for x in range(ROAD_WIDTH):
        # Xác định vật thể tại ô (x, y) này là gì
        if y == ROAD_HEIGHT - 1 and x == st.session_state.car_pos:
            color = "#ff4d4d; border-radius: 4px; box-shadow: 0 0 8px #ff4d4d;"  # Xe người chơi (Màu Đỏ)
        elif (x, y) in st.session_state.obstacles:
            color = "#f1c40f; border-radius: 4px;"  # Chướng ngại vật / Xe cản đường (Màu Vàng)
        else:
            color = "#222;"  # Mặt đường trống (Màu Tối)
            
        grid_html += f"<div style='aspect-ratio: 1; background-color: {color}; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;'>{'🏎️' if (y == ROAD_HEIGHT - 1 and x == st.session_state.car_pos) else ('🚧' if (x, y) in st.session_state.obstacles else '')}</div>"

grid_html += "</div>"

st.markdown(grid_html, unsafe_allow_html=True)
