import streamlit as st
import requests
import random

# 1. إعدادات الصفحة والهوية
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

# تصميم واجهة احترافية (Dark & Gold) لبرنامج our goal study
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

# 2. قاعدة بيانات وهمية (تخزن في الرام)
if 'members' not in st.session_state: st.session_state.members = []
if 'status' not in st.session_state: st.session_state.status = "off"
if 'room_id' not in st.session_state: st.session_state.room_id = None

# التوكن الخاص بك
TOKEN = "8562331908:AAFVuGeKhct_rV2lQvxVWJSUfQ1HB8TNhK4"

# دالة إرسال الرسائل
def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except:
        pass

# 3. منطق الصفحات
if 'page' not in st.session_state: st.session_state.page = "login"

# --- صفحة الدخول ---
if st.session_state.page == "login":
    st.markdown("<p class='logo-text'>our goal study</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>سجل دخولك عبر التليجرام لتبدأ رحلة النجاح 🚀</p>", unsafe_allow_html=True)
    
    # التقاط بيانات التليجرام من الرابط (Query Params)
    params = st.query_params
    if "id" in params:
        u_id = params["id"]
        u_name = params.get("first_name", "بطل")
        st.session_state.user_id = u_id
        st.session_state.user_name = u_name
        
        # إضافة المستخدم للقائمة لإرسال التنبيهات
        if u_id not in st.session_state.members:
            st.session_state.members.append(u_id)
            # رسالة ترحيبية فورية
            welcome_txt = f"أهلاً بك يا {u_name} في our goal study! 🎓\nتم تفعيل التنبيهات.. سأرسل لك هنا فور بدء أي جلسة مذاكرة."
            send_telegram_msg(u_id, welcome_txt)
            
        st.session_state.page = "main"
        st.rerun()

    # ويدجت التليجرام (الرابط الدقيق المربوط ببوتك)
    telegram_widget = """
    <div style="text-align: center; padding: 20px;">
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="our_goal_study_bot" 
                data-size="large" 
                data-userpic="true" 
                data-auth-url="https://our-goal-study-6mvlf8k8xt6zndhf77zhep.streamlit.app/" 
                data-request-access="write"></script>
    </div>
    """
    st.components.v1.html(telegram_widget, height=150)
    
    if st.button("🚀 دخول كضيف (بدون تنبيهات)"):
        st.session_state.user_name = "ضيف_مكافح"
        st.session_state.page = "main"; st.rerun()

# --- الصفحة الرئيسية (الروم) ---
elif st.session_state.page == "main":
    st.markdown(f"## نورت يا {st.session_state.user_name} 👋")
    
    # لوحة تحكم الإدارة (محمية بكلمة سر)
    with st.expander("🛠️ إعدادات الغرفة (للمسؤول فقط)"):
        pwd = st.text_input("كلمة السر", type="password")
        if pwd == "our122122":
            if st.button("🚀 فتح الروم وإرسال تنبيهات تليجرام"):
                st.session_state.status = "active"
                st.session_state.room_id = str(random.randint(1000, 9999))
                
                # إرسال التنبيه لكل المشتركين
                alert_text = "📢 يا بطل! بدأت الآن جلسة مذاكرة جديدة في our goal study.. انضم إلينا فوراً! 🚀"
                for m_id in st.session_state.members:
                    send_telegram_msg(m_id, alert_text)
                st.success("تم إرسال التنبيهات بنجاح! ✅")
            
            if st.button("🔴 إغلاق الروم"):
                st.session_state.status = "off"
                st.rerun()

    # عرض حالة الروم
    if st.session_state.status == "active":
        st.success(f"✅ الروم نشطة حالياً! كود الدخول: {st.session_state.room_id}")
    else:
        st.info("لا توجد رومات نشطة. انتظر تنبيهاً على التليجرام قريباً.")
