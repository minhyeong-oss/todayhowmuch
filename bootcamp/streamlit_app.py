import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib
import requests

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="오늘얼마", page_icon="💰", layout="wide")

API_BASE = "http://localhost:8080/api"

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #F0F2F6; }
    .css-card {
        background-color: #FFFFFF; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #F1F3F5; margin-bottom: 20px;
    }
    .label { color: #6B7280; font-size: 14px; font-weight: 500; margin-bottom: 4px; }
    .value { color: #111827; font-size: 26px; font-weight: 700; }
    .sub-value { font-size: 12px; margin-top: 4px; }
    .receipt-item { display: flex; align-items: center; padding: 16px 0; border-bottom: 1px solid #F8F9FA; }
    .receipt-icon {
        width: 48px; height: 48px; border-radius: 12px; display: flex;
        align-items: center; justify-content: center; margin-right: 16px; font-size: 22px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API 호출 함수 ---
def fetch_expenses():
    try:
        res = requests.get(f"{API_BASE}/expenses", timeout=5)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def fetch_summary():
    try:
        res = requests.get(f"{API_BASE}/expenses/summary", timeout=5)
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

def fetch_monthly():
    try:
        res = requests.get(f"{API_BASE}/expenses/monthly", timeout=5)
        return res.json() if res.status_code == 200 else []
    except:
        return []

# --- 3. 카테고리 아이콘/색상 매핑 ---
CATEGORY_STYLE = {
    "식비":   {"icon": "🍴", "color": "#FEE2E2"},
    "카페":   {"icon": "☕", "color": "#FEF3C7"},
    "쇼핑":   {"icon": "🛍️", "color": "#DBEAFE"},
    "교통":   {"icon": "🚌", "color": "#DCFCE7"},
    "기타":   {"icon": "📦", "color": "#F3E8FF"},
}
CHART_COLORS = ["#FF8A8A", "#FFD384", "#84B8FF", "#A2FF86", "#C4B5FD"]

def get_style(category_name):
    return CATEGORY_STYLE.get(category_name, {"icon": "📦", "color": "#F3E8FF"})

# --- 4. DB (로컬 로그인용) ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  name TEXT)''')
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password_hash=?',
              (username, make_hashes(password)))
    user = c.fetchone()
    conn.close()
    return user

def add_user(name, email, username, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username,email,password_hash,name) VALUES (?,?,?,?)',
                  (username, email, make_hashes(password), name))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# --- 5. 화면 렌더링 ---

def render_dashboard():
    summary = fetch_summary()
    expenses = fetch_expenses()
    monthly  = fetch_monthly()

    total_amount   = summary.get("totalAmount", 0)
    total_count    = summary.get("totalCount", 0)
    category_totals = summary.get("categoryTotals", {})
    top_category   = summary.get("topCategory", "-")
    top_style      = get_style(top_category)

    name = st.session_state.get("display_name", "사용자")
    st.markdown(f"<h2 style='margin-bottom:0;'>대시보드</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#9CA3AF; margin-bottom:25px;'>{name}님의 소비 현황</p>", unsafe_allow_html=True)

    # 상단 요약 카드
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'''<div class="css-card">
            <p class="label">이번달 총 지출</p>
            <p class="value">{int(total_amount):,}원</p>
            <p class="sub-value" style="color:#9CA3AF;">총 {total_count}건</p>
        </div>''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''<div class="css-card">
            <p class="label">등록 영수증</p>
            <p class="value">{total_count}건</p>
            <p class="sub-value" style="color:#9CA3AF;">전체 기준</p>
        </div>''', unsafe_allow_html=True)
    with m3:
        top_amount = category_totals.get(top_category, 0)
        st.markdown(f'''<div class="css-card">
            <p class="label">가장 많은 카테고리</p>
            <p class="value">{top_style["icon"]} {top_category}</p>
            <p class="sub-value" style="color:#9CA3AF;">{int(top_amount):,}원</p>
        </div>''', unsafe_allow_html=True)

    # 차트 + 최근 내역
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("<p style='font-weight:600; margin-bottom:15px;'>📊 소비 패턴 분석</p>", unsafe_allow_html=True)
        if category_totals:
            cat_df = pd.DataFrame(
                list(category_totals.items()),
                columns=["카테고리", "금액"]
            )
            fig = px.pie(cat_df, values="금액", names="카테고리",
                         hole=0.5, color_discrete_sequence=CHART_COLORS)
            fig.update_layout(margin=dict(t=0,b=0,l=0,r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("아직 지출 데이터가 없습니다.")

    with col_right:
        st.markdown("<p style='font-weight:600; margin-bottom:15px;'>📝 최근 소비 내역</p>", unsafe_allow_html=True)
        recent = expenses[:5]
        if recent:
            st.markdown('<div class="css-card" style="padding-top:0;padding-bottom:0;">', unsafe_allow_html=True)
            for item in recent:
                cat_name = item.get("category", {}).get("categoryName", "기타") if item.get("category") else "기타"
                style    = get_style(cat_name)
                name_str = item.get("storeName", "-")
                amount   = int(item.get("amountKrw", 0))
                date_str = (item.get("spentOn") or "-")[:10] if item.get("spentOn") else "-"
                st.markdown(f'''
                <div class="receipt-item">
                    <div class="receipt-icon" style="background-color:{style['color']};">{style['icon']}</div>
                    <div style="flex-grow:1;">
                        <p style="margin:0;font-size:14px;font-weight:600;">{name_str}</p>
                        <p style="margin:0;font-size:12px;color:#9CA3AF;">{date_str} · {cat_name}</p>
                    </div>
                    <div style="font-weight:700;">{amount:,}원</div>
                </div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("아직 소비 내역이 없습니다.")

    # 월별 추이
    st.markdown("---")
    st.markdown("<p style='font-weight:600; margin-bottom:15px;'>📈 월별 소비 추이</p>", unsafe_allow_html=True)
    if monthly:
        m_df = pd.DataFrame(monthly)
        st.plotly_chart(
            px.bar(m_df, x="월", y="총 지출액", text_auto=",.0f",
                   color_discrete_sequence=["#4e73df"]),
            use_container_width=True
        )
    else:
        st.info("월별 데이터가 없습니다.")


def render_upload():
    st.title("📤 영수증 업로드")
    st.info("영수증 사진을 업로드하면 OCR과 LLM이 자동으로 분류합니다.")
    uploaded = st.file_uploader("이미지 선택", type=["jpg","png","jpeg"])
    if uploaded:
        st.image(uploaded, width=300)
        st.success("업로드 완료! (OCR 연동 후 자동 분류됩니다)")


def render_history():
    st.title("📜 전체 소비 내역")
    expenses = fetch_expenses()

    if not expenses:
        st.info("등록된 지출 내역이 없습니다.")
        return

    rows = []
    for e in expenses:
        cat = e.get("category", {}).get("categoryName", "기타") if e.get("category") else "기타"
        rows.append({
            "상호명":    e.get("storeName", "-"),
            "카테고리": cat,
            "금액(원)": int(e.get("amountKrw", 0)),
            "날짜":     (e.get("spentOn") or "-")[:10],
        })
    df = pd.DataFrame(rows)

    # 필터
    col1, col2 = st.columns([1, 3])
    with col1:
        cats = ["전체"] + list(df["카테고리"].unique())
        selected = st.selectbox("카테고리 필터", cats)
    if selected != "전체":
        df = df[df["카테고리"] == selected]

    st.dataframe(df, use_container_width=True)
    st.markdown(f"**총 {len(df)}건 | 합계: {df['금액(원)'].sum():,}원**")


# --- 6. 메인 ---
def main_webapp():
    init_db()
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.title("💰 오늘얼마")
            tab1, tab2 = st.tabs(["로그인", "회원가입"])
            with tab1:
                with st.form("login"):
                    u_id = st.text_input("아이디")
                    u_pw = st.text_input("비밀번호", type="password")
                    if st.form_submit_button("로그인", use_container_width=True):
                        user = check_login(u_id, u_pw)
                        if user:
                            st.session_state["logged_in"] = True
                            st.session_state["display_name"] = user[4] or u_id
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 틀렸습니다.")
            with tab2:
                with st.form("signup_form"):
                    new_name  = st.text_input("이름")
                    new_email = st.text_input("이메일")
                    new_id    = st.text_input("아이디")
                    new_pw    = st.text_input("비밀번호", type="password")
                    confirm   = st.text_input("비밀번호 확인", type="password")
                    if st.form_submit_button("가입하기", use_container_width=True):
                        if new_pw != confirm:
                            st.error("비밀번호가 일치하지 않습니다.")
                        elif not all([new_name, new_email, new_id, new_pw]):
                            st.error("모든 항목을 입력해주세요.")
                        elif add_user(new_name, new_email, new_id, new_pw):
                            st.success("가입 완료! 로그인해주세요.")
                        else:
                            st.error("이미 사용 중인 아이디 또는 이메일입니다.")
    else:
        with st.sidebar:
            st.markdown("<h2 style='color:#111827;'>💰 오늘얼마</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#6B7280;'>👤 {st.session_state.get('display_name','')}</p>", unsafe_allow_html=True)
            st.write("---")
            menu = st.radio("MENU", ["🏠 대시보드", "📤 영수증 업로드", "📜 소비 내역", "📊 통계", "✨ AI 분석"])
            st.write("---")
            if st.button("로그아웃", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        if menu == "🏠 대시보드":       render_dashboard()
        elif menu == "📤 영수증 업로드": render_upload()
        elif menu == "📜 소비 내역":    render_history()
        else:
            st.title(menu)
            st.info("준비 중인 페이지입니다.")

if __name__ == "__main__":
    main_webapp()