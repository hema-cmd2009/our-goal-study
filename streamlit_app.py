import streamlit as st
import time

# 1. إعدادات التصميم الفاخر
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    html, body, [class*="css"] { background-color: #000000; color: #D4AF37; }
    .stApp { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); }
    .timer-text { font-size: 100px; font-weight: 900; text-align: center; color: #D4AF37; text-shadow: 0 0 20px #D4AF37; }
    .prayer-notice { background: #D4AF37; color: #000; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; animation: pulse 2s infinite; }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.03);} 100% {transform: scale(1);} }
    .member-card { background: #111; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; }
    .stButton>button { background: #D4AF37; color: #000; border-radius: 10px; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إنشاء المخزن المشترك (هذا ما يجعل الروم تظهر للكل)
@st.cache_resource
def get_global_state():
    return {
        "active_room": False,
        "room_time": 0,
        "mode": "study",
        "members": []
    }

global_data = get_global_state()

if 'page' not in st.session_state: st.session_state.page = "login"

# ----------------- 🚪 شاشة تسجيل الدخول -----------------
if st.session_state.page == "login":
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        try: st.image("logo.png", width=250)
        except: st.title("OUR GOAL STUDY")
    with col_b:
        st.header("تسجيل الدخول")
        u_mail = st.text_input("البريد الإلكتروني")
        u_name = st.text_input("اسم المستخدم")
        if st.button("انضمام للروم الآن"):
            if u_mail and u_name:
                st.session_state.user = u_name
                if u_name not in global_data["members"]:
                    global_data["members"].append(u_name)
                st.session_state.page = "room"
                st.rerun()
        if st.button("🛡️ لوحة الإدارة"):
            st.session_state.page = "admin"
            st.rerun()

# ----------------- 🏠 شاشة الروم (الساحة) -----------------
elif st.session_state.page == "room":
    if not global_data["active_room"]:
        st.warning("🕒 الروم مغلقة حالياً.. بانتظار المسؤول.")
        if st.button("⬅️ خروج"): 
            st.session_state.page = "login"
            st.rerun()
    else:
        st.markdown(f"<h3>مرحباً، {st.session_state.user} 🎓</h3>", unsafe_allow_html=True)
        if global_data["mode"] == "break":
            st.markdown("<div class='prayer-notice'>✨ وقت راحة: صلّ على النبي محمد ﷺ ✨</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timer-text'>BREAK</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='timer-text'>{global_data['room_time']}:00</div>", unsafe_allow_html=True)
        
        st.write("---")
        st.subheader(f"👥 الحاضرون ({len(global_data['members'])})")
        cols = st.columns(5)
        for i, m in enumerate(global_data["members"]):
            with cols[i % 5]:
                st.markdown(f"<div class='member-card'>👤<br>{m}</div>", unsafe_allow_html=True)
        
        if st.button("تسجيل الخروج"):
            if st.session_state.user in global_data["members"]:
                global_data["members"].remove(st.session_state.user)
            st.session_state.page = "login"
            st.rerun()

# ----------------- 🛡️ لوحة الإدارة -----------------
elif st.session_state.page == "admin":
    st.header("🛡️ التحكم بالروم الجماعية")
    pw = st.text_input("باسورد الإدارة", type="password")
    if pw == "our122122":
        col1, col2 = st.columns(2)
        with col1:
            mins = st.number_input("وقت المذاكرة", 5, 500, 60)
            if st.button("🚀 نشر الروم للجميع"):
                global_data["active_room"] = True
                global_data["room_time"] = mins
                global_data["mode"] = "study"
                st.success("تم النشر!")
        with col2:
            if st.button("✨ تفعيل وضع الصلاة على النبي"):
                global_data["mode"] = "break"
            if st.button("📖 عودة للمذاكرة"):
                global_data["mode"] = "study"
            if st.button("🛑 إغلاق الروم"):
                global_data["active_room"] = False
    
    if st.button("⬅️ العودة"):
        st.session_state.page = "login"
        st.rerun()
