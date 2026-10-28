import base64
import calendar
from datetime import date
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="종이 다이어리", page_icon="📔", layout="centered")

# 종이 배경 이미지: main.py와 같은 폴더에 paper.jpg를 두세요.
paper_path = Path(__file__).parent / "paper.jpg"

if paper_path.exists():
    paper_base64 = base64.b64encode(paper_path.read_bytes()).decode("utf-8")
    background_css = f"""
    background-image: url("data:image/jpeg;base64,{paper_base64}");
    """
else:
    background_css = "background-color: #f2e7d5;"



st.markdown(
    """
    <style>
    .stApp {
        background-color: #f2e7d5;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #594632;
        font-family: "궁서", "Gungsuh", serif !important;
    }

    .stApp p,
    .stApp label,
    .stApp input,
    .stApp textarea,
    .stApp button,
    .stApp h1,
    .stApp h2,
    .stApp h3 {
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

    div.stButton > button:hover {
        background: #ead7bb;
    }

    .paper {
        background: rgba(255, 250, 240, 0.72);
        border: 1px solid #e2d1b7;
        border-radius: 12px;
        padding: 16px;
    }
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
