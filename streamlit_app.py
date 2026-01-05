import streamlit as st
import time
from datetime import datetime, timedelta

# 1. إعدادات التصميم (Dark/Gold Professional Design)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* تنسيق النصوص والخانات */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; }
    
    /* الجدول الخارجي والعد التنازلي للموعد */
    .schedule-header { color: #D4AF37; text-align: center; border: 2px solid #D4AF37; padding: 10px; border-radius: 15px; margin-bottom: 20px; }
    .wait-timer { font-size: 50px; color: #fff; text-align: center; font-weight: bold; background: #111; border-radius: 10px; padding: 10px; margin: 10px 0; border: 1px dashed #D4AF37; }

    /* المربعات والتايمر الرئيسي */
    .member-card { background: #111; border: 1px solid #333; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37; }
    .study-subject { color: #000; background: #D4AF37; padding: 2px 8px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 5px; }
    .main-timer { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .countdown-10 { font-size: 180px; text-align: center; color: #D4AF37; font-weight: bold; text-shadow: 0 0 20px #D4AF37; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "remaining_seconds": 0, "last_update": None,
        "members": [], "schedule": [] # schedule items: {"time": "20:00", "duration": 60}
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- الواجهة الرئيسية -----------------
st.image("logo.png", width=100)
tabs = st.tabs(["👤 ساحة الانضمام", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    # أ. الجدول الخارجي والعد التنازلي للمواعيد (قبل تسجيل الدخول)
    if db["schedule"]:
        st.markdown("<div class='schedule-header'><h3>📅 جدول الرومات القادمة</h3></div>", unsafe_allow_html=True)
        for item in db["schedule"]:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"#### ⏰ موعد الروم: {item['time']} (المدة: {item['duration']} دقيقة)")
            with col_b:
                # حساب الوقت المتبقي للموعد
                try:
                    now = datetime.now()
                    target_time = datetime.strptime(item['time'], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
                    if target_time < now: target_time += timedelta(days=1)
                    diff = target_time - now
                    st.markdown(f"<div class='wait-timer'>{str(diff).split('.')[0]}</div>", unsafe_allow_html=True)
                except: st.write("تنسيق الوقت غير صحيح")

    st.write("---")

    # ب. تسجيل الدخول
    if not st.session_state.get('joined', False):
        st.subheader("🔑 دخول الروم الحالية")
        c1, c2, c3 = st.columns(3)
        with c1: c_code = st.text_input("كود الروم")
        with c2: c_name = st.text_input("اسمك")
        with c3: c_subject = st.text_input("هتذاكر إيه؟")
        
        if st.button("🚀 دخول الآن"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({"name": c_name, "subject": c_subject})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("الكود غير صحيح أو البيانات ناقصة")
    else:
        # ج. عرض الحالة داخل الروم
        if db["status"] == "ready":
            st.markdown("<h1 style='text-align:center; color:white;'>⚠️ استعدووووو...</h1>", unsafe_allow_html=True)
        
        elif db["status"] == "counting":
            # عد تنازلي 10 ثواني فخم
            for i in range(10, 0, -1):
                st.markdown(f"<div class='countdown-10'>{i}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            db["status"] = "running"
            db["last_update"] = time.time()
            st.rerun()

        elif db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            st.markdown(f"<div class='main-timer'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        
        elif db["status"] == "break":
            st.markdown("<h1 style='text-align:center;'>☕ وقت راحة.. ارتاح شوية</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='main-timer' style='color:#555;'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)

        # د. مربعات الزملاء
        st.write("---")
        st.subheader(f"👥 الزملاء ({len(db['members'])})")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'><span style='font-size:40px;'>👤</span><br><b style='color:white;'>{m['name']}</b><br><span class='study-subject'>📖 {m['subject']}</span></div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pass == "our122122":
        # عرض المستخدمين بجدول واضح
        st.subheader("👥 سجل الحضور")
        if db["members"]:
            st.table(db["members"]) # يعرض الأسماء بوضوح تام
        
        st.write("---")
        # إضافة المواعيد للجدول الخارجي
        st.subheader("📅 إضافة موعد للجدول الخارجي")
        col1, col2 = st.columns(2)
        with col1: t_val = st.text_input("الوقت (مثلاً 20:00)")
        with col2: d_val = st.number_input("المدة (دقيقة)", 5, 120, 45)
        if st.button("➕ نشر الموعد للطلاب"):
            db["schedule"].append({"time": t_val, "duration": d_val})
            st.success("تم النشر في الجدول الخارجي!")
        
        if st.button("🗑️ مسح الجدول"):
            db["schedule"] = []
            st.rerun()

        st.write("---")
        # أزرار التحكم بالروم
        if not db["room_id"]:
            mins_input = st.number_input("مدة الروم الحالية", 5, 120, 45)
            if st.button("🚀 فتح الروم وتوليد كود"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = mins_input * 60
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"كود الروم: {db['room_id']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1: 
                if st.button("🔔 استعدوا"): db["status"] = "ready"
            with c2: 
                if st.button("▶️ ابدأ (10 ثواني)
