
import streamlit as st

st.set_page_config(
    page_title="다이어리 테마 설정",
    page_icon="🎨",
    layout="centered",
)

if "diary_theme" not in st.session_state:
    st.session_state.diary_theme = "기본"

if "diary_font" not in st.session_state:
    st.session_state.diary_font = "돋움체"

font_map = {
    "돋움체": '"돋움", "Dotum", sans-serif',
    "궁서체": '"궁서", "Gungsuh", serif',
    "바탕체": '"바탕", "Batang", serif',
    "맑은 고딕": '"맑은 고딕", "Malgun Gothic", sans-serif',
    "굴림체": '"굴림", "Gulim", sans-serif',
}
preview_font = font_map.get(
    st.session_state.diary_font, font_map["돋움체"]
)

st.markdown(
    f"""
    <style>
    html, body, p, label, button, input, textarea, h1, h2, h3 {{
        font-family: {preview_font} !important;
    }}
    .stApp {{
        background-color: #f2e7d5;
        color: #594632;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎨 다이어리 꾸미기")
st.write("원하는 테마와 글씨체를 선택해 봐.")

st.divider()

st.subheader("1. 테마 선택")

theme_options = ["선택 안 함", "도트", "숲", "호러", "한국"]

theme = st.selectbox(
    "다이어리 테마",
    theme_options,
    index=0,
    help="선택 안 함을 유지하면 현재 테마가 바뀌지 않아.",
)

theme_previews = {
    "도트": "🟪 🟦 🟩 픽셀 장식과 파스텔 색상",
    "숲": "🌿 🍃 🌳 차분한 초록색과 자연의 분위기",
    "호러": "🌑 🕯️ 🩸 어두운 배경과 붉은 포인트",
    "한국": "🏯 🪷 📜 한지와 전통 색상의 분위기",
}

if theme != "선택 안 함":
    st.info(theme_previews[theme])
else:
    st.caption(f"현재 테마: {st.session_state.diary_theme}")

st.divider()

st.subheader("2. 글씨체 선택")

font_options = [
    "선택 안 함",
    "돋움체",
    "궁서체",
    "바탕체",
    "맑은 고딕",
    "굴림체",
]

font = st.selectbox(
    "다이어리 글씨체",
    font_options,
    index=0,
    help="선택 안 함을 유지하면 현재 글씨체가 바뀌지 않아.",
)

font_samples = {
    "돋움체": "돋움",
    "궁서체": "궁서",
    "바탕체": "바탕",
    "맑은 고딕": "맑은 고딕",
    "굴림체": "굴림",
}

if font != "선택 안 함":
    st.write(f"미리 보기: 나의 종이 다이어리 — {font_samples[font]}")

st.divider()

if st.button("✨ 선택한 디자인 적용", use_container_width=True):
    if theme != "선택 안 함":
        st.session_state.diary_theme = theme

    if font != "선택 안 함":
        st.session_state.diary_font = font

    st.success("선택한 디자인을 적용했어!")
    st.switch_page("main.py")

if st.button("📔 메인 다이어리로 돌아가기", use_container_width=True):
    st.switch_page("main.py")
