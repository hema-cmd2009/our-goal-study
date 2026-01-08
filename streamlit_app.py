import streamlit as st
import requests
import random
import time

# 1. إعدادات الهوية والتصميم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #000; color: #ffffff !important; font-family: 'Cairo', sans-serif; }
    .logo-text { font-size: 3.5rem; color: #D4AF37; text-align: center; font-weight: bold; margin-bottom: 0; }
    .stButton>button { background: linear-gradient(90deg, #D4AF37, #F2D472) !important; color: #000 !important; border-radius: 50px !important; font-weight: bold !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات (Shared DB)
@st.cache_resource
def get_db():
    return {"members": [], "status": "off", "room_id": None}

db = get_db()
TOKEN = "8562331908:AAFVuGeKhct_rV2lQvxVWJSUfQ1HB8TNhK4" # توكن بوتك

# دالة إرسال تنبيه تليجرام
def send_alert(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# 3. منطق الصفحات
if 'page' not in st.session_state: st.session_state.page = "login"

# --- صفحة الدخول ---
if st.session_state.page == "login":
    st.markdown("<p class='logo-text'>our goal study</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>سجل دخولك عبر التليجرام لتبدأ رحلة النجاح 🚀</p>", unsafe_allow_html=True)
    
    # التقاط بيانات التليجرام من الرابط
    params = st.query_params
    if "id" in params:
        u_id = params["id"]
        u_name = params.get("first_name", "بطل")
        st.session_state.user_id = u_id
        st.session_state.user_name = u_name
        
        # حفظ المستخدم لإرسال إشعارات له لاحقاً
        if not any(m['id'] == u_id for m in db["members"]):
            db["members"].append({"id": u_id, "name": u_name})
            
        st.session_state.page = "room"
        st.rerun()

    # ويدجت التليجرام
    telegram_widget = """
    <div style="text-align: center; padding: 20px;">
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="our_goal_study_bot" 
                data-size="large" 
                data-auth-url="https://our-goal-study-6mvlf8k8xt6zndhf77zhep.streamlit.app/" 
                data-request-access="write"></script>
    </div>
    """
    st.components.v1.html(telegram_widget, height=150)

# --- صفحة الروم ---
elif st.session_state.page == "room":
    st.markdown(f"## نورت يا {st.session_state.user_name} 👋")
    
    # لوحة التحكم (لصاحب الموقع)
    with st.expander("🛠️ لوحة تحكم الإدارة"):
        if st.text_input("كلمة السر", type="password") == "our122122":
            if st.button("🚀 فتح روم وإرسال تنبيهات"):
                db["status"] = "active"
                db["room_id"] = str(random.randint(1000, 9999))
                
                # إرسال الرسالة التلقائية لكل اللي سجلوا
                msg = "📢 يا بطل! في روم مذاكرة بدأت الآن في our goal study.. مستنيينك تحصلنا! 🚀"
                for member in db["members"]:
                    send_alert(member["id"], msg)
                st.success("تم فتح الروم وإرسال التنبيهات بنجاح!")

    if db["status"] == "active":
        st.success(f"✅ الروم شغالة دلوقتي! كود الانضمام: {db['room_id']}")
    else:
        st.info("مفيش رومات شغالة حالياً.. خليك قريب هيوصلك إشعار أول ما تبدأ.")
