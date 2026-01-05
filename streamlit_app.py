import streamlit as st
import time

# 1. إعداد التنسيق الجمالي (CSS) - الأسود والذهبي
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    .stButton>button { 
        background-color: #D4AF37; color: #000000; 
        border-radius: 12px; font-weight: bold; border: 2px solid #D4AF37;
        width: 100%; height: 50px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffffff; color: #000000; }
    input { background-color: #111111 !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; }
    .user-card { 
        border: 2px solid #D4AF37; border-radius: 15px; 
        padding: 15px; text-align: center; background: #111111;
        box-shadow: 0px 4px 10px rgba(212, 175, 55, 0.2);
    }
    .timer-box { 
        font-size: 70px; font-weight: bold; text-align: center; 
        color: #D4AF37; font-family: 'Courier New', monospace;
    }
    .prayer-banner {
        background-color: #D4AF37; color: #000; padding: 20px;
        border-radius: 15px; text-align: center; font-size: 24px;
        font-weight: bold; margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة البيانات
if 'members_list' not in st.session_state:
    st.session_state.members_list = {} 
if 'active_room' not in st.session_state:
    st.session_state.active_room = {"status": False, "study_time": 0, "break_time": 0, "mode": "work"}

# عرض اللوجو في القائمة الجانبية (باستخدام الملف الذي رفعته)
try:
    st.sidebar.image("logo.png", width=150)
except:
    st.sidebar.title("our goal study")

page = st.sidebar.radio("انتقل إلى:", ["🏠 الروم الرئيسية", "👤 الملف الشخصي", "⚙️ لوحة الإدارة"])

# ----------------- ⚙️ لوحة الإدارة -----------------
if page == "⚙️ لوحة الإدارة":
    st.header("🛡️ لوحة تحكم المسؤول")
    adm_mail = st.text_input("البريد الإلكتروني")
    adm_pass = st.text_input("كلمة السر", type="password")
    
    if adm_mail == "ourgostudy@gmail.com" and adm_pass == "our122122":
        tab_members, tab_room = st.tabs(["👥 إضافة أعضاء", "🚀 التحكم بالروم"])
        with tab_members:
            full_name = st.text_input("أدخل الاسم الثلاثي للعضو")
            if st.button("تسجيل العضو وتوليد كود"):
                if full_name:
                    new_code = f"OGS-{len(st.session_state.members_list) + 101}"
                    st.session_state.members_list[full_name] = new_code
                    st.success(f"تم تسجيل {full_name} | الكود: {new_code}")
            st.write("---")
            st.write("### قائمة الأعضاء المسجلين")
            for name in sorted(st.session_state.members_list.keys()):
                st.text(f"👤 {name} - الكود الخاص به: {st.session_state.members_list[name]}")

        with tab_room:
            st.session_state.active_room["study_time"] = st.number_input("مدة المذاكرة (ساعات)", 1, 12, 2)
            st.session_state.active_room["break_time"] = st.number_input("مدة الراحة (دقائق)", 5, 45, 10)
            if st.button("🚀 إطلاق الروم الآن"):
                st.session_state.active_room["status"] = True
                st.session_state.active_room["mode"] = "work"
            if st.button("✨ بدء وقت الراحة (صلاة على النبي)"):
                st.session_state.active_room["mode"] = "break"
            if st.button("🛑 إغلاق الروم"):
                st.session_state.active_room["status"] = False

# ----------------- 🏠 الروم الرئيسية -----------------
elif page == "🏠 الروم الرئيسية":
    # عرض اللوجو في الواجهة الرئيسية
    try:
        st.image("logo.png", width=150)
    except:
        st.title("🎓 our goal study")
        
    if not st.session_state.active_room["status"]:
        st.info("🕒 الروم مغلق حالياً. يرجى انتظار المسؤول لفتح الجلسة.")
    else:
        u_name = st.text_input("الاسم الثلاثي")
        u_code = st.text_input("الكود الخاص بك", type="password")
            
        if u_name in st.session_state.members_list and u_code == st.session_state.members_list[u_name]:
            if st.session_state.active_room["mode"] == "break":
                st.markdown("<div class='prayer-banner'>✨ وقت راحة: صلّ على النبي محمد ﷺ ✨</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='timer-box'>00:00:00</div>", unsafe_allow_html=True)
            
            st.subheader("👥 الأعضاء المشاركون في الروم")
            cols = st.columns(4)
            for i, member in enumerate(st.session_state.members_list.keys()):
                with cols[i % 4]:
                    st.markdown(f"<div class='user-card'>👤<br><span style='font-size: 12px;'>{member}</span></div>", unsafe_allow_html=True)
        elif u_name:
            st.error("عفواً، الاسم أو الكود غير صحيح.")

# ----------------- 👤 الملف الشخصي -----------------
else:
    st.header("👤 ملفك الشخصي")
    st.write("هنا ستظهر إنجازاتك ونقاطك قريباً في تحديث القادم!")
