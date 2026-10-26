
import streamlit as st

st.set_page_config(
    page_title="종이 다이어리",
    page_icon="📔",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f2e7d5;
        color: #594632;
    }

    html, body, p, label, button, input, textarea,
    h1, h2, h3, [class*="st-"] {
        font-family: "궁서", "Gungsuh", serif !important;
    }

    h1, h2, h3 {
        color: #765638;
    }

    div.stButton > button {
        background: rgba(255, 250, 240, 0.92);
        color: #594632;
        border: 1px solid #dfc9aa;
        border-radius: 8px;
        min-height: 45px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📔 나의 종이 다이어리")
st.subheader("두 번째 페이지")

if st.button("← 첫 페이지로 돌아가기"):
    st.switch_page("main.py")

st.divider()

st.subheader("나만의 기록")
st.write("이곳에 새로운 기록 기능을 추가할 수 있어.")

