import streamlit as st
import requests
import random

# 1. إعدادات الهوية والصفحة لـ our goal study
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #000; color: #ffffff !important; font-family: 'Cairo', sans-serif; }
    .logo-text { font-size: 3.5rem; color: #D4AF37; text-align: center; font-weight: bold; margin-bottom: 0; }
    .stButton>button { 
        background: linear-gradient(90deg, #D4AF37, #F2D472) !important; 
        color: #000 !important; border-radius: 50px !important; 
        font-weight: bold !important; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. البيانات والتوكن الخاص بك
TOKEN = "8562331908:AAFVuGeKhct_rV2lQvxVWJSUfQ1HB8TNhK4"
# الرابط الدقيق كما في صورة BotFather
AUTH_URL = "https://our-goal-study-6mvlf8k8xt6zndhf77zhep.streamlit.app/"

if 'members' not in st.session_state: st.session_state.members = []
if 'status' not in st.session_state: st.session_state.status = "off"

# 3. منطق الصفحات
if 'logged_in' not in st.session_state:
    st.markdown("<p class='logo-text'>our goal study</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>سجل دخولك عبر التليجرام لتبدأ رحلة النجاح 🚀</p>", unsafe_allow_html=True)

    # ويدجت التليجرام بتصميم يجبر المتصفح على القبول
    telegram_html = f"""
    <div style="display: flex; justify-content: center; padding: 20px;">
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="our_goal_study_bot" 
                data-size="large" 
                data-userpic="true" 
                data-auth-url="{AUTH_URL}" 
                data-request-access="write"></script>
    </div>
    """
    st.components.v1.html(telegram_html, height=150)

    # التقاط البيانات بعد تسجيل الدخول
    params = st.query_params
    if "id" in params:
        st.session_state.logged_in = True
        st.session_state.u_name = params.get("first_name", "بطل")
        u_id = params["id"]
        
        if u_id not in st.session_state.members:
            st.session_state.members.append(u_id)
            # إرسال رسالة ترحيبية فورية
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": u_id, "text": f"مرحباً بك يا {st.session_state.u_name} في our goal study! 🎓\nتم تفعيل التنبيهات بنجاح."})
        st.rerun()
else:
    # صفحة الروم والمذاكرة
    st.markdown(f"<h2 style='text-align:center;'>نورت يا {st.session_state.u_name} 👋</h2>", unsafe_allow_html=True)
    
    with st.expander("🛠️ لوحة تحكم الإدارة"):
        pwd = st.text_input("كلمة السر", type="password")
        if pwd == "our122122":
            if st.button("🚀 فتح الروم وإرسال تنبيهات"):
                st.session_state.status = "active"
                room_code = str(random.randint(1000, 9999))
                # إرسال تنبيه لكل المسجلين
                for m_id in st.session_state.members:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": m_id, "text": f"📢 بدأت جلسة مذاكرة الآن! كود الدخول: {room_code}"})
                st.success("تم إرسال التنبيهات بنجاح!")

    if st.session_state.status == "active":
        st.success("✅ الروم مفتوحة الآن.. ابدأ المذاكرة!")
    else:
        st.info("انتظر تنبيه التليجرام لبدء المذاكرة.")
