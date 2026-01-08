import streamlit as st
import requests
import random
import time

# 1. إعدادات الهوية والتصميم (Dark Mode + Golden Touch)
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

# 2. البيانات المشتركة (Database)
@st.cache_resource
def get_db():
    # بنحفظ المشتركين هنا عشان نبعت لهم تنبيهات
    return {"members": [], "status": "off", "room_id": None}

db = get_db()
# توكن بوتك اللي جبته من BotFather
TOKEN = "8562331908:AAFVuGeKhct_rV2lQvxVWJSUfQ1HB8TNhK4"

# دالة إرسال الرسائل عبر التليجرام
def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except:
        pass

# 3. منطق التنقل بين الصفحات
if 'page' not in st.session_state: st.session_state.page = "login"

# --- الواجهة 1: صفحة الدخول (Login) ---
if st.session_state.page == "login":
    st.markdown("<p class='logo-text'>our goal study</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>سجل دخولك عبر التليجرام لتبدأ رحلة النجاح 🚀</p>", unsafe_allow_html=True)
    
    # التقاط بيانات التليجرام من رابط الموقع (Query Params)
    params = st.query_params
    if "id" in params:
        u_id = params["id"]
        u_name = params.get("first_name", "بطل")
        st.session_state.user_id = u_id
        st.session_state.user_name = u_name
        
        # حفظ المستخدم في القائمة لإرسال التنبيهات لاحقاً
        if not any(m['id'] == u_id for m in db["members"]):
            db["members"].append({"id": u_id, "name": u_name})
            # إرسال رسالة ترحيبية فورية للطالب على تليجرام
            welcome_txt = f"أهلاً بك يا {u_name} في our goal study! 🎓\nتم تفعيل التنبيهات.. هبعتلك رسالة هنا أول ما أي روم مذاكرة تبدأ."
            send_telegram_msg(u_id, welcome_txt)
            
        st.session_state.page = "room"
        st.rerun()

    # ويدجت زر التليجرام المربوط برابط موقعك
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
    
    if st.button("🚀 دخول سريع (كضيف)"):
        st.session_state.user_name = "ضيف_مكافح"
        st.session_state.page = "room"; st.rerun()

# --- الواجهة 2: صفحة الروم (Room) ---
elif st.session_state.page == "room":
    st.markdown(f"## نورت يا {st.session_state.user_name} 👋")
    
    # لوحة تحكم الإدارة (محمية بكلمة سر)
    with st.expander("🛠️ لوحة تحكم الإدارة"):
        pwd = st.text_input("كلمة السر", type="password")
        if pwd == "our122122":
            if st.button("🚀 فتح روم وإرسال تنبيهات للجميع"):
                db["status"] = "active"
                db["room_id"] = str(random.randint(1000, 9999))
                
                # إرسال التنبيه التلقائي لكل المسجلين
                alert_text = "📢 يا بطل! تم فتح روم مذاكرة جديدة الآن في our goal study.. مستنيينك تحصلنا! 🚀"
                for member in db["members"]:
                    if "id" in member:
                        send_telegram_msg(member["id"], alert_text)
                st.success("تم فتح الروم وإرسال رسائل التليجرام بنجاح! ✅")

    # عرض حالة الروم للطلاب
    if db["status"] == "active":
        st.success(f"✅ الروم شغالة الآن! كود الانضمام: {db['room_id']}")
        st.info("الآن ابدأ المذاكرة بتركيز.. التوفيق حليفك.")
    else:
        st.warning("لا توجد رومات نشطة حالياً. انتظر إشعاراً على التليجرام.")
