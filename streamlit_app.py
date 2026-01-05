import streamlit as st
import time

# 1. إعدادات التصميم (اللوجو، الألوان، الخطوط)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    .stButton>button { 
        background-color: #D4AF37; color: #000; border-radius: 12px; 
        font-weight: bold; border: 2px solid #D4AF37; width: 100%; height: 50px;
    }
    input { background-color: #111111 !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; }
    .timer-box { font-size: 80px; font-weight: bold; text-align: center; color: #D4AF37; margin: 20px 0; }
    .prayer-banner { background-color: #D4AF37; color: #000; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; }
    .user-card { border: 2px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; background: #111111; }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات (Session State)
if 'members' not in st.session_state: st.session_state.members = {}
if 'room_active' not in st.session_state: st.session_state.room_active = False
if 'mode' not in st.session_state: st.session_state.mode = "work"

# 3. القائمة الجانبية مع اللوجو
try:
    st.sidebar.image("logo.png", width=150)
except:
    st.sidebar.title("our goal study")

menu = st.sidebar.radio("القائمة", ["🏠 الروم الرئيسية", "👤 الملف الشخصي", "⚙️ لوحة الإدارة"])

# ----------------- ⚙️ لوحة الإدارة -----------------
if menu == "⚙️ لوحة الإدارة":
    st.header("🛡️ لوحة تحكم المسؤول")
    mail = st.text_input("البريد الإلكتروني")
    pw = st.text_input("كلمة السر", type="password")
    
    if mail == "ourgostudy@gmail.com" and pw == "our122122":
        tab1, tab2 = st.tabs(["👥 تسجيل الأعضاء", "🚀 التحكم بالروم"])
        with tab1:
            new_user = st.text_input("الاسم الثلاثي للعضو")
            if st.button("إضافة عضو وتوليد كود"):
                code = f"OGS-{len(st.session_state.members)+101}"
                st.session_state.members[new_user] = code
                st.success(f"تم التسجيل! الكود هو: {code}")
            for n, c in st.session_state.members.items():
                st.write(f"👤 {n} | الكود: {c}")
        with tab2:
            if st.button("🚀 فتح الروم الآن"): st.session_state.room_active = True
            if st.button("✨ بدء وقت الصلاة على النبي (راحة)"): st.session_state.mode = "break"
            if st.button("🛑 إغلاق الروم"): st.session_state.room_active = False

# ----------------- 🏠 الروم الرئيسية -----------------
elif menu == "🏠 الروم الرئيسية":
    if not st.session_state.room_active:
        st.info("🕒 الروم مغلق حالياً.. بانتظار المسؤول.")
    else:
        u_name = st.text_input("اسمك الثلاثي")
        u_code = st.text_input("كود الدخول", type="password")
        
        if u_name in st.session_state.members and u_code == st.session_state.members[u_name]:
            if st.session_state.mode == "break":
                st.markdown("<div class='prayer-banner'>✨ وقت راحة: صلّ على النبي محمد ﷺ ✨</div>", unsafe_allow_html=True)
            
            # عرض التايمر
            st.markdown("<div class='timer-box'>02:00:00</div>", unsafe_allow_html=True)
            
            # عرض الأعضاء المتواجدين
            st.subheader("👥 المتواجدون الآن")
            cols = st.columns(4)
            for i, m in enumerate(st.session_state.members.keys()):
                with cols[i%4]:
                    st.markdown(f"<div class='user-card'>👤<br>{m.split()[0]}</div>", unsafe_allow_html=True)
        elif u_name:
            st.error("البيانات غير صحيحة")

# ----------------- 👤 الملف الشخصي -----------------
else:
    st.header("👤 ملفك الشخصي")
    st.write("ترقب نظام النقاط والترتيب في التحديث القادم!")
