import streamlit as st
import time

# 1. إعداد الواجهة الاحترافية (بدون قائمة جانبية)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    .timer-text { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 20px #D4AF37; margin: 20px 0; }
    .stButton>button { background: #D4AF37; color: #000; font-weight: bold; border-radius: 12px; height: 50px; border: none; width: 100%; }
    .stButton>button:hover { background: #fff; }
    .member-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 15px; text-align: center; margin: 10px; }
    .invite-box { background: #1a1a1a; padding: 20px; border-radius: 15px; border: 1px dashed #D4AF37; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الذاكرة المشتركة (Database)
@st.cache_resource
def get_session():
    return {"active": False, "mode": "waiting", "members": [], "time": 45, "start_trigger": False}

data = get_session()

# 3. التحقق من الرابط (هل المستخدم يحمل رابط دعوة؟)
query_params = st.query_params
is_student = "room" in query_params

# ----------------- 👤 واجهة الطالب (عبر الرابط) -----------------
if is_student:
    st.image("logo.png", width=150)
    st.title("🎓 الانضمام إلى الاجتماع")
    
    if not data["start_trigger"]:
        st.info("🕒 أنت في قاعة الانتظار.. يرجى إدخال اسمك وانتظار المسؤول لبدء الجلسة.")
        s_name = st.text_input("اسمك الذي سيظهر للجميع")
        if st.button("تأكيد الانضمام"):
            if s_name and s_name not in data["members"]:
                data["members"].append(s_name)
                st.success("تم الانضمام! انتظر بدء المسؤول...")
    else:
        # الجلسة بدأت
        st.markdown(f"<div class='timer-text'>{data['time']}:00</div>", unsafe_allow_html=True)
        if data["mode"] == "break":
            st.warning("✨ وقت راحة: صلّ على النبي محمد ﷺ ✨")
        st.subheader(f"👥 الزملاء الحاضرون ({len(data['members'])})")
        cols = st.columns(6)
        for i, m in enumerate(data["members"]):
            with cols[i % 6]: st.markdown(f"<div class='member-card'>👤<br>{m}</div>", unsafe_allow_html=True)

# ----------------- 🛡️ واجهة المسؤول (المنشئ) -----------------
else:
    st.image("logo.png", width=120)
    st.title("🛡️ لوحة إدارة الاجتماعات")
    
    password = st.text_input("رمز مرور المسؤول", type="password")
    if password == "our122122":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1️⃣ إنشاء الرابط")
            # استبدل هذا بالرابط الخاص بك
            my_link = "https://our-goal-study.streamlit.app/?room=live"
            st.markdown(f"<div class='invite-box'><b>رابط الدعوة:</b><br><code style='color:#D4AF37;'>{my_link}</code></div>", unsafe_allow_html=True)
            st.write("انسخ الرابط أعلاه وأرسله للطلاب.")
            
        with col2:
            st.subheader("2️⃣ التحكم")
            data["time"] = st.number_input("وقت الجلسة", 5, 500, 45)
            if st.button("🚀 ابدأ الجلسة للجميع الآن"):
                data["start_trigger"] = True
                st.balloons()
            
            if st.button("✨ وضع الصلاة على النبي"): data["mode"] = "break"
            if st.button("🛑 إنهاء وطرد الجميع"):
                data["start_trigger"] = False
                data["members"] = []
                st.rerun()

        st.write("---")
        st.subheader(f"👥 قائمة الانتظار الحالية: {len(data['members'])} طالب")
        for m in data["members"]:
            st.markdown(f"- {m}")

# تحديث تلقائي لمتابعة الحالة
time.sleep(3)
st.rerun()
