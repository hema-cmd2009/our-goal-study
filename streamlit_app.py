import streamlit as st
import time
from datetime import datetime, timedelta

# 1. تصميم الواجهة الاحترافية
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    .timer-display { font-size: 120px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 30px rgba(212, 175, 55, 0.5); margin: 20px 0; }
    .stButton>button { background: #D4AF37; color: #000; font-weight: bold; border-radius: 12px; height: 50px; border: none; }
    .member-card { background: #111; border: 1px solid #333; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. مخزن البيانات المشترك (Database)
@st.cache_resource
def get_db():
    return {
        "room_id": None, 
        "status": "off", 
        "end_timestamp": None, # الوقت الذي سينتهي فيه التايمر
        "duration_mins": 45,
        "members": []
    }

db = get_db()

# دالة لتحويل الثواني إلى تنسيق دقيقة:ثانية
def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- 🏠 واجهة التطبيق -----------------
st.image("logo.png", width=100)
tabs = st.tabs(["👤 دخول الطلاب", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not db["room_id"]:
        st.info("لا توجد جلسة نشطة حالياً. انتظر الكود من المسؤول.")
        c_code = st.text_input("أدخل كود الروم")
        c_name = st.text_input("اسمك")
        if st.button("انضمام"):
            if c_code == db["room_id"] and db["room_id"] is not None:
                st.session_state.user = c_name
                if c_name not in db["members"]: db["members"].append(c_name)
                st.rerun()
    else:
        # عرض التايمر الحي
        if db["status"] == "running":
            remaining = db["end_timestamp"] - time.time()
            if remaining > 0:
                st.markdown(f"<div class='timer-display'>{format_time(remaining)}</div>", unsafe_allow_html=True)
                time.sleep(1) # تحديث كل ثانية
                st.rerun()
            else:
                st.markdown("<div class='timer-display'>00:00</div>", unsafe_allow_html=True)
                st.success("🎉 انتهت جلسة المذاكرة! خذ راحة.")
        else:
            st.info("🕒 أنت في قاعة الانتظار.. سيبدأ التايمر فور ضغط المسؤول على 'ابدأ'.")
        
        st.write(f"👥 الزملاء الحاضرون: {', '.join(db['members'])}")

# --- تبويب الإدارة ---
with tabs[1]:
    pw = st.text_input("كلمة السر", type="password")
    if pw == "our122122":
        if not db["room_id"]:
            db["duration_mins"] = st.number_input("مدة الجلسة بالدقائق", 1, 120, 45)
            if st.button("🚀 إنشاء روم وتوليد كود"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["status"] = "waiting"
                st.rerun()
        else:
            st.success(f"الروم نشطة! الكود: {db['room_id']}")
            if st.button("🔥 ابدأ العد التنازلي الآن"):
                db["status"] = "running"
                # تحديد وقت النهاية (الوقت الحالي + عدد الدقائق)
                db["end_timestamp"] = time.time() + (db["duration_mins"] * 60)
                st.rerun()
            
            if st.button("🛑 إنهاء الجلسة للكل"):
                db["room_id"] = None
                db["status"] = "off"
                db["members"] = []
                st.rerun()

# ميزة التحديث التلقائي للطلاب المنتظرين
if db["status"] == "waiting" or (db["status"] == "running" and db["room_id"]):
    time.sleep(2)
    st.rerun()
