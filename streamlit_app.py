import streamlit as st
import requests
import random

# إعدادات الصفحة
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

# التصميم (Dark Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #000; color: #ffffff !important; font-family: 'Cairo', sans-serif; }
    .logo-text { font-size: 3rem; color: #D4AF37; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# البيانات والتوكن
TOKEN = "8562331908:AAFVuGeKhct_rV2lQvxVWJSUfQ1HB8TNhK4"
if 'members' not in st.session_state: st.session_state.members = []

# صفحة الدخول
if 'logged_in' not in st.session_state:
    st.markdown("<p class='logo-text'>our goal study</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>سجل دخولك عبر التليجرام لتبدأ رحلة النجاح 🚀</p>", unsafe_allow_html=True)

    # الرابط الرسمي المسجل في BotFather
    AUTH_URL = "https://our-goal-study-6mvlf8k8xt6zndhf77zhep.streamlit.app/"

    # الكود المحدث لضمان الظهور (استخدام iframe)
    telegram_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="our_goal_study_bot" 
                data-size="large" 
                data-userpic="true" 
                data-auth-url="{AUTH_URL}" 
                data-request-access="write"></script>
    </div>
    """
    st.components.v1.html(telegram_html, height=120)

    # استقبال البيانات بعد الضغط
    params = st.query_params
    if "id" in params:
        st.session_state.logged_in = True
        st.session_state.u_name = params.get("first_name", "بطل")
        if params["id"] not in st.session_state.members:
            st.session_state.members.append(params["id"])
            # رسالة ترحيبية
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={{"chat_id": params["id"], "text": f"نورت our goal study يا {st.session_state.u_name}! 🎓"}})
        st.rerun()

else:
    st.success(f"مرحباً بك يا {st.session_state.u_name}!")
    if st.button("🚀 إرسال تنبيه للجميع"):
        for m_id in st.session_state.members:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={{"chat_id": m_id, "text": "🚀 بدأت روم المذاكرة الآن!"}})
        st.toast("تم إرسال التنبيهات!")
