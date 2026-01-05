import streamlit as st
import time

# 1. Page Configuration (Black & Gold)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    .stButton>button { 
        background-color: #D4AF37; color: #000000; 
        border-radius: 12px; font-weight: bold; border: 2px solid #D4AF37;
        width: 100%; height: 50px;
    }
    input { background-color: #111111 !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; }
    .user-card { border: 2px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; background: #111111; margin-bottom: 10px; }
    .timer-box { font-size: 70px; font-weight: bold; text-align: center; color: #D4AF37; }
    .prayer-banner { background-color: #D4AF37; color: #000; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar with Logo
try:
    st.sidebar.image("logo.png", width=150)
except:
    st.sidebar.header("our goal study")

page = st.sidebar.radio("القائمة", ["🏠 الروم الرئيسية", "👤 الملف الشخصي", "⚙️ لوحة الإدارة"])

# 3. Session State Init
if 'members' not in st.session_state: st.session_state.members = {}
if 'room_active' not in st.session_state: st.session_state.room_active = False

# 4. Admin Panel
if page == "⚙️ لوحة الإدارة":
    st.header("🛡️ لوحة الإدارة")
    mail = st.text_input("الإيميل")
    pw = st.text_input("الباسورد", type="password")
    if mail == "ourgostudy@gmail.com" and pw == "our122122":
        name = st.text_input("أدخل الاسم الثلاثي")
        if st.button("إضافة عضو"):
            code = f"OGS-{len(st.session_state.members)+100}"
            st.session_state.members[name] = code
            st.success(f"تم تسجيل {name} بالكود {code}")
        if st.button("تشغيل الروم"): st.session_state.room_active = True
        st.write("---")
        for n in sorted(st.session_state.members.keys()):
            st.text(f"👤 {n} - الكود: {st.session_state.members[n]}")

# 5. Home Page
elif page == "🏠 الروم الرئيسية":
    st.image("logo.png", width=150)
    if not st.session_state.room_active:
        st.warning("الروم مغلقة حالياً من قبل الإدارة.")
    else:
        u_name = st.text_input("الاسم الثلاثي")
        u_code = st.text_input("الكود")
        if u_name in st.session_state.members and u_code == st.session_state.members[u_name]:
            st.markdown("<div class='timer-box'>00:00:00</div>", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, m in enumerate(st.session_state.members.keys()):
                with cols[i%4]: st.markdown(f"<div class='user-card'>👤<br>{m.split()[0]}</div>", unsafe_allow_html=True)
