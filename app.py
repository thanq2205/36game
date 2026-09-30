import streamlit as st
import random

st.title("🎯 Game Đoán Số May Mắn")

if "target" not in st.session_state:
    st.session_state.target = random.randint(1, 100)
    st.session_state.score = 0

guess = st.number_input("Đoán một số từ 1 đến 100:", min_value=1, max_value=100, step=1)

if st.button("Kiểm tra kết quả"):
    st.session_state.score += 1
    if guess < st.session_state.target:
        st.warning("Số bạn chọn THẤP hơn số bí mật!")
    elif guess > st.session_state.target:
        st.warning("Số bạn chọn CAO hơn số bí mật!")
    else:
        st.success(f"🎉 Đúng rồi! Bạn đoán trúng sau {st.session_state.score} lần.")
        if st.button("Chơi lại"):
            st.session_state.target = random.randint(1, 100)
            st.session_state.score = 0
            st.rerun()
