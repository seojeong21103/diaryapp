import base64
import calendar
from datetime import date
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="종이 다이어리", page_icon="📔", layout="centered")

# 선택한 테마와 글씨체 불러오기
theme = st.session_state.get("diary_theme", "기본")
font = st.session_state.get("diary_font", "돋움체")

font_map = {
    "돋움체": '"돋움", "Dotum", sans-serif',
    "궁서체": '"궁서", "Gungsuh", serif',
    "바탕체": '"바탕", "Batang", serif',
    "맑은 고딕": '"맑은 고딕", "Malgun Gothic", sans-serif',
    "굴림체": '"굴림", "Gulim", sans-serif',
}
font_family = font_map.get(font, font_map["돋움체"])

# 테마별 색상
themes = {
    "기본": {
        "background": "#f2e7d5",
        "color": "#594632",
        "heading": "#765638",
        "button": "rgba(255, 250, 240, 0.92)",
        "button_hover": "#ead7bb",
        "border": "#dfc9aa",
        "paper": "rgba(255, 250, 240, 0.72)",
    },
    "도트": {
        "background": "#e9e4f7",
        "color": "#40375d",
        "heading": "#62518e",
        "button": "#f5f1ff",
        "button_hover": "#dcd2f5",
        "border": "#bcb0df",
        "paper": "rgba(250, 247, 255, 0.82)",
    },
    "숲": {
        "background": "#e3eddf",
        "color": "#344b35",
        "heading": "#426b45",
        "button": "#f3f8ef",
        "button_hover": "#d1e2cb",
        "border": "#b4c9ad",
        "paper": "rgba(247, 251, 243, 0.82)",
    },
    "호러": {
        "background": "#211f24",
        "color": "#eee5e5",
        "heading": "#d06a70",
        "button": "#393139",
        "button_hover": "#563b43",
        "border": "#76515b",
        "paper": "rgba(48, 42, 49, 0.88)",
    },
    "한국": {
        "background": "#eee3cf",
        "color": "#554333",
        "heading": "#8b493d",
        "button": "#faf2e3",
        "button_hover": "#e8d2b4",
        "border": "#c9aa83",
        "paper": "rgba(255, 248, 232, 0.82)",
    },
}
colors = themes.get(theme, themes["기본"])

# 기본 테마일 때만 종이 이미지 사용
paper_path = Path(__file__).parent / "paper.jpg"
background_css = f"background-color: {colors['background']};"
if theme == "기본" and paper_path.exists():
    paper_base64 = base64.b64encode(paper_path.read_bytes()).decode("utf-8")
    background_css = (
        f'background-image: url("data:image/jpeg;base64,{paper_base64}");'
    )

st.markdown(
    f"""
    <style>
    .stApp {{
        {background_css}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: {colors["color"]};
        font-family: {font_family} !important;
    }}

    .stApp p, .stApp label, .stApp input, .stApp textarea,
    .stApp button, .stApp h1, .stApp h2, .stApp h3,
    .stApp [data-testid="stMarkdownContainer"] {{
        font-family: {font_family} !important;
        color: {colors["color"]};
    }}

    h1, h2, h3 {{
        color: {colors["heading"]} !important;
    }}

    div.stButton > button {{
        background: {colors["button"]};
        color: {colors["color"]};
        border: 1px solid {colors["border"]};
        border-radius: 8px;
        min-height: 45px;
    }}

    div.stButton > button:hover {{
        background: {colors["button_hover"]};
        border-color: {colors["border"]};
    }}

    .paper {{
        background: {colors["paper"]};
        border: 1px solid {colors["border"]};
        border-radius: 12px;
        padding: 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "calendar"
if "year" not in st.session_state:
    st.session_state.year = date.today().year
if "month" not in st.session_state:
    st.session_state.month = date.today().month
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().isoformat()
if "events" not in st.session_state:
    st.session_state.events = {}

title_col, icon_col = st.columns([10, 1])

with title_col:
    st.title("나의 종이 다이어리")

with icon_col:
    st.write("")
    if st.button("📔", key="go_next"):
        st.switch_page("pages/next.py")

if st.session_state.page == "calendar":
    left, center, right = st.columns([1, 3, 1])

    with left:
        if st.button("← 이전"):
            st.session_state.month -= 1
            if st.session_state.month < 1:
                st.session_state.month = 12
                st.session_state.year -= 1
            st.rerun()

    with center:
        st.subheader(f"{st.session_state.year}년 {st.session_state.month}월")

    with right:
        if st.button("다음 →"):
            st.session_state.month += 1
            if st.session_state.month > 12:
                st.session_state.month = 1
                st.session_state.year += 1
            st.rerun()

    st.markdown('<div class="paper">', unsafe_allow_html=True)

    cols = st.columns(7)
    for col, weekday in zip(cols, ["일", "월", "화", "수", "목", "금", "토"]):
        col.markdown(f"**{weekday}**")

    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(
        st.session_state.year, st.session_state.month
    )

    for week in weeks:
        cols = st.columns(7)
        for col, day in zip(cols, week):
            if day == 0:
                col.write("")
                continue

            selected = date(st.session_state.year, st.session_state.month, day)
            key = selected.isoformat()
            info = st.session_state.events.get(key, {})
            label = str(day)

            if info.get("title"):
                label += "\n✦ " + info["title"][:6]

            if col.button(label, key=f"day_{key}", use_container_width=True):
                st.session_state.selected_date = key
                st.session_state.page = "day"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("날짜를 클릭하면 해당 날짜의 일정 페이지로 이동해.")

else:
    selected = date.fromisoformat(st.session_state.selected_date)
    key = selected.isoformat()

    if st.button("← 달력으로 돌아가기"):
        st.session_state.page = "calendar"
        st.rerun()

    st.header(f"{selected.year}년 {selected.month}월 {selected.day}일")

    info = st.session_state.events.setdefault(
        key, {"title": "", "tasks": []}
    )

    info["title"] = st.text_input("중요한 날의 제목", value=info["title"])

    st.divider()
    st.subheader("오늘의 일정")

    with st.form("add_task", clear_on_submit=True):
        task_time = st.time_input("시간")
        task_text = st.text_input("할 일", placeholder="예: 수학 공부하기")
        add = st.form_submit_button("일정 추가")

    if add and task_text.strip():
        info["tasks"].append(
            {
                "time": task_time.strftime("%H:%M"),
                "text": task_text.strip(),
                "memo": "",
            }
        )
        st.rerun()

    for i, task in enumerate(info["tasks"]):
        with st.expander(f"{task['time']} · {task['text']}"):
            task["memo"] = st.text_area(
                "간편 메모",
                value=task.get("memo", ""),
                key=f"memo_{key}_{i}",
            )
            if st.button("일정 삭제", key=f"delete_{key}_{i}"):
                info["tasks"].pop(i)
                st.rerun()

    st.caption("현재 버전은 임시 저장 방식이야.")
