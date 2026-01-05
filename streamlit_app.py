import streamlit as st
import time

# 1. إعدادات التصميم الفاخر (Dark/Gold Professional Design)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* إخفاء القائمة الجانبية والعناصر الافتراضية */
    [data-testid="stSidebar"] {display: none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* الخلفية والخطوط العامة */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; background-color: #000000; color: #D4AF37; }
    .stApp { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); }

    /* تحسين العناوين */
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 2px; }

    /* تصميم الحقول (Inputs) */
    .stTextInput>div>div>input {
        background-color: #111111 !important;
        color: #D4AF37 !important;
        border: 2px solid #333 !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        font-size: 18px !important;
        transition: 0.4s;
    }
    .stTextInput>div>div>input:focus { border-color: #D4AF37 !important; box-shadow: 0 0 10px #D4AF37; }

    /* تصميم الأزرار الذهبية */
    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B);
        color: #000 !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        padding: 12px 30px !important;
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        transition: 0.3s all ease-in-out;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(212, 175, 55, 0.5); background: #ffffff !important; }

    /* كروت الأعضاء (Grid Design) */
    .member-card {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: 0.4s;
    }
    .member-card:hover { border-color: #D4AF37; transform: scale(1.05); }
    .status-dot { height: 10px; width: 10px; background-color: #00ff00; border-radius: 50%; display: inline-block; margin-right: 5px; }

    /* التايمر العملاق */
    .timer-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(212, 175, 55, 0.1);
        margin: 20px 0;
    }
    .timer-text { 
        font-size: 120px !important; 
        font-weight: 900; 
        text-align: center; 
        color: #D4AF37; 
        text-shadow: 0 0 30px rgba(212, 175, 55, 0.4);
        line-height: 1;
    }

    /* إشعار الصلاة على النبي */
    .prayer-notice {
        background: linear-gradient(90deg, #D4AF37, #F7E7CE);
        color: #000;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        font-size: 28px;
        font-weight: 900;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.4);
        animation: pulse-gold 2s infinite;
    }
    @keyframes pulse-gold {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات
if 'page' not in st.session_state: st.session_state.page = "login"
if 'members_list' not in st.session_state: st.session_state.members_list = []
if 'config' not in st.session_state: 
    st.session_state.config = {"active": False, "time": 0, "mode": "study", "break": 0}

def navigate(p): st.session_state.page = p

# ----------------- 🚪 شاشة تسجيل الدخول -----------------
if st.session_state.page == "login":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.image("logo.png", width=250)
        st.markdown("<h1 style='font-size: 50px;'>OUR GOAL<br>STUDY</h1>", unsafe_allow_html=True)
        st.write("إلى القمة معاً.. سجل بياناتك للدخول إلى ساحة العلم.")

    with col_r:
        st.markdown("<div style='background: #111; padding: 40px; border-radius: 30px; border: 1px solid #333;'>", unsafe_allow_html=True)
        u_mail = st.text_input("البريد الإلكتروني")
        u_name = st.text_input("اسم العرض (يظهر للأعضاء)")
        if st.button("انضمام للروم الآن"):
            if u_mail and u_name:
                st.session_state.current_user = {"name": u_name, "email": u_mail}
                if u_name not in [m['name'] for m in st.session_state.members_list]:
                    st.session_state.members_list.append({"name": u_name, "status": "Online"})
                navigate("room")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🛡️ دخول الإدارة"): navigate("admin")

# ----------------- 🏠 شاشة الروم (الساحة) -----------------
elif st.session_state.page == "room":
    if not st.session_state.config["active"]:
        st.markdown("<div style='text-align: center; padding: 100px;'>", unsafe_allow_html=True)
        st.image("logo.png", width=150)
        st.header("الروم غير مفعلة حالياً")
        st.info("انتظر إشعار الإدارة لبدء الجلسة")
        if st.button("خروج"): navigate("login")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Header
        head_1, head_2 = st.columns([5, 1])
        with head_1: st.markdown(f"<h2>مرحباً، {st.session_state.current_user['name']} 🎓</h2>", unsafe_allow_html=True)
        with head_2: 
            if st.button("تسجيل الخروج"): navigate("login")

        # التايمر والوضع
        st.markdown("<div class='timer-container'>", unsafe_allow_html=True)
        if st.session_state.config["mode"] == "break":
            st.markdown("<div class='prayer-notice'>✨ صلّ على النبي محمد ﷺ ✨</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timer-text'>BREAK: {st.session_state.config['break']}m</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='timer-text'>{st.session_state.config['time']}:00</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("---")
        # شبكة الأعضاء
        st.subheader(f"👥 الزملاء الحاضرون ({len(st.session_state.members_list)})")
        cols = st.columns(6)
        for i, m in enumerate(st.session_state.members_list):
            with cols[i % 6]:
                st.markdown(f"""
                <div class='member-card'>
                    <div style='font-size: 50px;'>👤</div>
                    <div style='font-size: 20px; font-weight: bold; color: #fff;'>{m['name']}</div>
                    <div style='color: #00ff00;'><span class='status-dot'></span>متصل</div>
                </div>
                """, unsafe_allow_html=True)

# ----------------- 🛡️ لوحة الإدارة -----------------
elif st.session_state.page == "admin":
    st.markdown("<h1 style='text-align: center;'>لوحة التحكم بالروم</h1>", unsafe_allow_html=True)
    password = st.text_input("رمز الدخول السري", type="password")
    
    if password == "our122122":
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.subheader("إعداد الروم")
            set_t = st.number_input("وقت الجلسة (دقائق)", 1, 500, 45)
            if st.button("🚀 بدء ونشر الروم"):
                st.session_state.config = {"active": True, "time": set_t, "mode": "study", "break": 0}
                st.success("تم تشغيل الروم!")
        
        with a_col2:
            st.subheader("تحكم سريع")
            if st.button("✨ تفعيل وقت الراحة"):
                st.session_state.config["mode"] = "break"
                st.session_state.config["break"] = 10
            if st.button("📖 العودة للدراسة"):
                st.session_state.config["mode"] = "study"
            if st.button("🛑 إنهاء الجلسة تماماً"):
                st.session_state.config["active"] = False

        st.write("---")
        st.subheader("قائمة المشتركين")
        st.dataframe(st.session_state.members_list, use_container_width=True)

    if st.button("العودة للرئيسية"): navigate("login")
