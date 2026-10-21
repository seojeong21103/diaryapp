import os
from datetime import date, datetime, time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from google import genai

st.set_page_config(page_title="종이 다이어리", page_icon="📔", layout="wide")

# Register the small custom component used for reliable single/double-click handling.
_component_path = Path(__file__).parent / "calendar_component"
diary_ui = components.declare_component("paper_diary_ui", path=str(_component_path))

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');
:root { --paper:#fffaf0; --ink:#514334; --line:#e6d8c3; --accent:#a87952; }
.stApp { background:#f2e8d8; color:var(--ink); font-family:'Noto Sans KR',sans-serif; }
.block-container { max-width:1100px; padding-top:2rem; }
h1,h2,h3 { font-family:'Gowun Batang',serif !important; color:#594632; }
.paper-card { background:#fffaf0; border:1px solid #e6d8c3; border-radius:12px; padding:1.1rem; box-shadow:0 4px 14px #8a6c4710; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stTimeInput"] input { background:#fffdf8; border-color:#ddcbb3; }
.stButton button, .stFormSubmitButton button { background:#9b7655; color:white; border:0; border-radius:9px; }
.stButton button:hover, .stFormSubmitButton button:hover { background:#79583d; color:white; }
small, .muted { color:#8b7864; }
</style>
""", unsafe_allow_html=True)

def secrets_value(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default

@st.cache_resource
def get_supabase():
    url = secrets_value("SUPABASE_URL")
    key = secrets_value("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

def get_gemini():
    key = secrets_value("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)

db = get_supabase()
if db is None:
    st.error("Supabase 설정이 필요해요. README의 설정 방법에 따라 Streamlit Secrets에 SUPABASE_URL과 SUPABASE_KEY를 입력해 주세요.")
    st.stop()

def load_day(day_string):
    result = db.table("diary_days").select("*").eq("diary_date", day_string).limit(1).execute()
    return result.data[0] if result.data else {"diary_date": day_string, "title": "", "memo": ""}

def load_tasks(day_string):
    return db.table("diary_tasks").select("*").eq("diary_date", day_string).order("task_time").execute().data

def save_day(day_string, title, memo):
    db.table("diary_days").upsert(
        {"diary_date": day_string, "title": title, "memo": memo},
        on_conflict="diary_date"
    ).execute()

def save_task(day_string, task_time, task_text):
    db.table("diary_tasks").insert({
        "diary_date": day_string, "task_time": task_time, "task_text": task_text, "memo": ""
    }).execute()

def update_task(task_id, task_time, task_text, memo):
    db.table("diary_tasks").update({
        "task_time": task_time, "task_text": task_text, "memo": memo
    }).eq("id", task_id).execute()

def delete_task(task_id):
    db.table("diary_tasks").delete().eq("id", task_id).execute()

def all_day_data(year, month):
    start = date(year, month, 1).isoformat()
    if month == 12:
        end = date(year + 1, 1, 1).isoformat()
    else:
        end = date(year, month + 1, 1).isoformat()
    days = db.table("diary_days").select("diary_date,title").gte("diary_date", start).lt("diary_date", end).execute().data
    tasks = db.table("diary_tasks").select("diary_date,task_text").gte("diary_date", start).lt("diary_date", end).execute().data
    result = {}
    for item in days:
        result.setdefault(item["diary_date"], {})["title"] = item.get("title", "")
    for item in tasks:
        current = result.setdefault(item["diary_date"], {})
        current["count"] = current.get("count", 0) + 1
    return result

def ai_text(prompt):
    client = get_gemini()
    if client is None:
        st.warning("Gemini API 설정이 없어요. Streamlit Secrets에 GEMINI_API_KEY를 입력해 주세요.")
        return None
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as exc:
        st.error(f"Gemini 요청에 실패했어요: {exc}")
        return None

if "page" not in st.session_state:
    st.session_state.page = "calendar"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().isoformat()
if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = date.today().replace(day=1).isoformat()
if "memo_task_id" not in st.session_state:
    st.session_state.memo_task_id = None

def go_calendar():
    st.session_state.page = "calendar"
    st.session_state.memo_task_id = None

st.title("종이 다이어리")
st.caption("오늘의 계획을 따뜻한 종이 위에 기록해요.")

if st.session_state.page == "calendar":
    month_date = date.fromisoformat(st.session_state.calendar_month)
    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("← 이전 달", use_container_width=True):
            y, m = month_date.year, month_date.month - 1
            if m == 0: y, m = y - 1, 12
            st.session_state.calendar_month = date(y, m, 1).isoformat()
            st.rerun()
    with nav2:
        st.markdown(f"<h2 style='text-align:center;margin:0'>{month_date.year}년 {month_date.month}월</h2>", unsafe_allow_html=True)
    with nav3:
        if st.button("다음 달 →", use_container_width=True):
            y, m = month_date.year, month_date.month + 1
            if m == 13: y, m = y + 1, 1
            st.session_state.calendar_month = date(y, m, 1).isoformat()
            st.rerun()

    data = all_day_data(month_date.year, month_date.month)
    event = diary_ui(
        mode="calendar",
        year=month_date.year,
        month=month_date.month,
        today=date.today().isoformat(),
        days=data,
        key="paper-calendar",
        default=None,
    )
    if isinstance(event, dict) and event.get("action") in ("open_day", "edit_title"):
        st.session_state.selected_date = event["date"]
        st.session_state.page = "day"
        st.session_state.edit_title = event.get("action") == "edit_title"
        st.rerun()

    st.markdown("<div class='paper-card'><b>사용 방법</b><br>날짜를 한 번 클릭하면 해당 날짜의 일정 페이지로 이동해요. 날짜를 더블 클릭하면 그날의 제목을 작성할 수 있어요.</div>", unsafe_allow_html=True)

else:
    day_string = st.session_state.selected_date
    day_obj = date.fromisoformat(day_string)
    day_info = load_day(day_string)
    st.button("← 달력으로 돌아가기", on_click=go_calendar)
    st.markdown(f"## {day_obj.year}년 {day_obj.month}월 {day_obj.day}일")
    if st.session_state.get("edit_title", False):
        with st.form("title_form"):
            title = st.text_input("이 날짜의 제목", value=day_info.get("title") or "", placeholder="예: 중간고사, 생일, 약속")
            if st.form_submit_button("제목 저장"):
                save_day(day_string, title, day_info.get("memo") or "")
                st.session_state.edit_title = False
                st.success("제목을 저장했어요.")
                st.rerun()
    elif day_info.get("title"):
        st.markdown(f"<div class='paper-card'><b>✦ {day_info['title']}</b></div>", unsafe_allow_html=True)
        if st.button("날짜 제목 수정"):
            st.session_state.edit_title = True
            st.rerun()
    else:
        with st.expander("날짜 제목 작성"):
            with st.form("title_form_new"):
                title = st.text_input("중요한 날의 제목", placeholder="예: 시험, 생일, 약속")
                if st.form_submit_button("제목 저장"):
                    save_day(day_string, title, day_info.get("memo") or "")
                    st.success("제목을 저장했어요.")
                    st.rerun()

    st.markdown("### 일정")
    with st.form("add_task_form", clear_on_submit=True):
        task_time = st.time_input("시간", value=time(9, 0), step=300)
        task_text = st.text_input("할 일", placeholder="예: 수학 문제 풀기")
        submitted = st.form_submit_button("일정 추가")
        if submitted:
            if task_text.strip():
                save_task(day_string, task_time.strftime("%H:%M"), task_text.strip())
                st.success("일정을 저장했어요.")
                st.rerun()
            else:
                st.warning("할 일을 입력해 주세요.")

    tasks = load_tasks(day_string)
    if not tasks:
        st.info("아직 등록한 일정이 없어요.")
    else:
        st.caption("일정을 더블 클릭하면 간편 메모를 열 수 있어요.")
        event = diary_ui(
            mode="tasks",
            tasks=[{"id": t["id"], "time": t["task_time"], "text": t["task_text"]} for t in tasks],
            key=f"paper-tasks-{day_string}",
            default=None,
        )
        if isinstance(event, dict) and event.get("action") == "edit_task":
            st.session_state.memo_task_id = event.get("id")
            st.rerun()

        for task in tasks:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 1])
                c1.markdown(f"**{task['task_time']}**")
                c2.write(task["task_text"])
                if c3.button("삭제", key=f"delete-{task['id']}"):
                    delete_task(task["id"])
                    st.rerun()

    if st.session_state.memo_task_id is not None:
        selected = next((t for t in tasks if str(t["id"]) == str(st.session_state.memo_task_id)), None)
        if selected:
            st.markdown("### 간편 메모")
            with st.form(f"memo_form_{selected['id']}"):
                edited_time = st.time_input(
                    "시간 수정",
                    value=datetime.strptime(selected["task_time"], "%H:%M").time(),
                    key=f"time-{selected['id']}"
                )
                edited_text = st.text_input("할 일 수정", value=selected["task_text"], key=f"text-{selected['id']}")
                edited_memo = st.text_area("메모", value=selected.get("memo") or "", placeholder="추가로 기억할 내용을 적어 보세요.", key=f"memo-{selected['id']}")
                save_col, close_col = st.columns(2)
                save_clicked = save_col.form_submit_button("저장")
                close_clicked = close_col.form_submit_button("닫기")
                if save_clicked:
                    update_task(selected["id"], edited_time.strftime("%H:%M"), edited_text.strip(), edited_memo)
                    st.session_state.memo_task_id = None
                    st.success("메모를 저장했어요.")
                    st.rerun()
                if close_clicked:
                    st.session_state.memo_task_id = None
                    st.rerun()

    st.markdown("### Gemini 도우미")
    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        if st.button("오늘 일정 정리", use_container_width=True):
            fresh_tasks = load_tasks(day_string)
            task_text = "\n".join(f"{t['task_time']} - {t['task_text']}" for t in fresh_tasks) or "등록된 일정 없음"
            result = ai_text(f"다음은 {day_string} 일정이야.\n{task_text}\n한국어로 일정을 간단하고 명확하게 정리해 줘. 새로운 일정이나 사실을 지어내지 마.")
            if result:
                st.session_state.ai_plan = result
    with ai_col2:
        if st.button("메모 요약", use_container_width=True):
            fresh_tasks = load_tasks(day_string)
            memo_text = "\n".join(f"{t['task_time']} {t['task_text']}: {t.get('memo') or '(메모 없음)'}" for t in fresh_tasks)
            day_memo = load_day(day_string).get("memo") or ""
            result = ai_text(f"{day_string}의 일정과 메모야.\n날짜 메모: {day_memo}\n{memo_text}\n한국어로 메모 내용을 짧게 요약해 줘. 정보가 없으면 없다고 알려 줘.")
            if result:
                st.session_state.ai_summary = result
    if st.session_state.get("ai_plan"):
        st.markdown("<div class='paper-card'><b>일정 정리</b></div>", unsafe_allow_html=True)
        st.write(st.session_state.ai_plan)
    if st.session_state.get("ai_summary"):
        st.markdown("<div class='paper-card'><b>메모 요약</b></div>", unsafe_allow_html=True)
        st.write(st.session_state.ai_summary)
