import streamlit as st
import time

# 1. إعدادات الواجهة (بدون Sidebar وبدون قيود)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; }
    .timer-text { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .stButton>button { background: #D4AF37; color: #000; font-weight: bold; border-radius: 10px; width: 100%; border:none; height: 50px;}
    .code-display { background: #111; border: 2px dashed #D4AF37; padding: 20px; text-align: center; font-size: 30px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة (Shared State)
@st.cache_resource
def get_db():
    return {"room_id": None, "status": "off", "members": [], "time": 45}

db = get_db()

# ----------------- 🏠 الصفحة الرئيسية -----------------
st.image("logo.png", width=120)
st.title("Our Goal Study 🎓")

menu = st.tabs(["👤 دخول الطلاب", "🛡️ لوحة الأدمن"])

# --- تبويب الطلاب ---
with menu[0]:
    c_code = st.text_input("أدخل كود الروم المكون من 6 أرقام")
    c_name = st.text_input("اسمك المستعار")
    
    if st.button("انضمام الآن"):
        if db["room_id"] and c_code == db["room_id"]:
            if c_name:
                if c_name not in db["members"]: db["members"].append(c_name)
                st.session_state.current_user = c_name
                st.success("تم الانضمام بنجاح!")
            else: st.error("اكتب اسمك")
        else: st.error("الكود غير صحيح أو الروم مغلقة")

    # شاشة العرض داخل الروم للطالب
    if "current_user" in st.session_state and db["room_id"]:
        st.write("---")
        if db["status"] == "waiting":
            st.info("🕒 قاعة الانتظار: انتظر بدء الأدمن للتايمر...")
        else:
            st.markdown(f"<div class='timer-text'>{db['time']}:00</div>", unsafe_allow_html=True)
        
        st.subheader(f"👥 الزملاء ({len(db['members'])})")
        st.write(", ".join(db["members"]))

# --- تبويب الأدمن ---
with menu[1]:
    pw = st.text_input("كلمة سر المسؤول", type="password")
    if pw == "our122122":
        if st.button("🚀 إنشاء روم جديدة (كود عشوائي)"):
            import random
            db["room_id"] = str(random.randint(100000, 999999))
            db["status"] = "waiting"
            db["members"] = []
            st.rerun()
            
        if db["room_id"]:
            st.markdown(f"<div class='code-display'>كود الروم: <b>{db['room_id']}</b></div>", unsafe_allow_html=True)
            db["time"] = st.number_input("وقت المذاكرة", 5, 500, 45)
            
            if st.button("🔥 ابدأ التايمر للجميع"):
                db["status"] = "running"
            
            if st.button("🛑 إنهاء الجلسة"):
                db["room_id"] = None
                st.rerun()

# تحديث تلقائي كل 5 ثواني
time.sleep(5)
st.rerun()
