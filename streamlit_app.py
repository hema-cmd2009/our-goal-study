import streamlit as st
import time
from datetime import datetime, timedelta

# 1. إعدادات التصميم المتطور (إصلاح الألوان والخطوط)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* توضيح نصوص الإدخال */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; font-size: 18px; }
    
    /* تصميم الجدول الخارجي والعد التنازلي للموعد */
    .schedule-box { border: 2px solid #D4AF37; padding: 15px; border-radius: 15px; margin-bottom: 20px; background: #111; }
    .wait-timer { font-size: 45px; color: #fff; text-align: center; font-weight: bold; text-shadow: 0 0 10px #D4AF37; }

    /* المربعات والتايمر */
    .member-card { background: #111; border: 1px solid #333; border-radius: 15px; padding: 20px; text-align: center; border-bottom: 4px solid #D4AF37; }
    .study-subject { color: #000; background: #D4AF37; padding: 3px 10px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 8px; }
    .main-timer { font-size: 110px; text-align: center; font-weight: bold; color: #D4AF37; }
    .countdown-big { font-size: 200px; text-align: center; color: #D4AF37; font-weight: bold; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "remaining_seconds": 0, "last_update": None,
        "members": [], "schedule": [] 
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- الواجهة الرئيسية -----------------
st.image("logo.png", width=100)

# أ. الجدول الخارجي (يظهر للكل بالخارج)
if db["schedule"] and not st.session_state.get('joined', False):
    st.markdown("<div class='schedule-box'><h2 style='text-align:center; color:#D4AF37;'>📅 مواعيد الرومات القادمة</h2></div>", unsafe_allow_html=True)
    for item in db["schedule"]:
        col_msg, col_clock = st.columns([2, 1])
        with col_msg:
            st.markdown(f"### ⏰ الموعد: {item['time']} \n **المدة:** {item['duration']} دقيقة")
        with col_clock:
            try:
                now = datetime.now()
                target = datetime.strptime(item['time'], "%H:%M").replace(year=now.year, month=now.month, day=now.day)
                if target < now: target += timedelta(days=1)
                diff = target - now
                st.markdown(f"<div class='wait-timer'>{str(diff).split('.')[0]}</div>", unsafe_allow_html=True)
            except: st.error("خطأ في تنسيق الوقت")
    st.write("---")

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not st.session_state.get('joined', False):
        st.subheader("🔑 انضم الآن للروم الحالية")
        c1, c2, c3 = st.columns(3)
        c_code = c1.text_input("كود الروم")
        c_name = c2.text_input("اسمك")
        c_subject = c3.text_input("هتذاكر إيه؟")
        
        if st.button("🚀 دخول القاعة"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({"name": c_name, "subject": c_subject})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("الكود خطأ أو البيانات ناقصة")
    else:
        # عرض الحالة (عد تنازلي 10 ثواني، تايمر، راحة)
        if db["status"] == "ready":
            st.markdown("<h1 style='text-align:center;'>⚠️ استعدووووو...</h1>", unsafe_allow_html=True)
        
        elif db["status"] == "counting":
            for i in range(10, 0, -1):
                st.markdown(f"<div class='countdown-big'>{i}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            db["status"] = "running"
            db["last_update"] = time.time()
            st.rerun()

        elif db["status"] == "running":
            now = time.time()
            db["remaining_seconds"] -= (now - db["last_update"])
            db["last_update"] = now
            if db["remaining_seconds"] > 0:
                st.markdown(f"<div class='main-timer'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                db["status"] = "off"
                st.balloons()
        
        elif db["status"] == "break":
            st.markdown("<h1 style='text-align:center; color:#D4AF37;'>☕ وقت راحة..</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='main-timer' style='color:#555;'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)

        # عرض مربعات الزملاء
        st.write("---")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'><span style='font-size:40px;'>👤</span><br><b style='color:white;'>{m['name']}</b><br><span class='study-subject'>📖 {m['subject']}</span></div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pw = st.text_input("كلمة السر", type="password")
    if admin_pw == "our122122":
        st.subheader("👥 الحاضرون الآن")
        if db["members"]:
            st.table(db["members"]) # الجدول أصبح واضحاً الآن
        
        st.write("---")
        # إدارة الجدول الخارجي
        st.subheader("📅 إضافة موعد للجدول")
        ca, cb = st.columns(2)
        t_input = ca.text_input("الوقت (مثلاً 22:00)")
        d_input = cb.number_input("المدة (دقيقة)", 5, 120, 45)
        if st.button("➕ نشر الموعد"):
            db["schedule"].append({"time": t_input, "duration": d_input})
            st.success("تم النشر")
        
        if st.button("🗑️ مسح الجدول"):
            db["schedule"] = []
            st.rerun()

        st.write("---")
        # أزرار التحكم بالروم
        if not db["room_id"]:
            m_input = st.number_input("مدة الروم الحالية", 5, 120, 45)
            if st.button("🚀 فتح روم جديدة"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = m_input * 60
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"الكود: {db['room_id']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🔔 استعدوا"): db["status"] = "ready"
            with c2:
                # زر البدء المعدل
                btn_label = "▶️ بدء (10 ثواني)" if db["status"] != "break" else "▶️ استكمال"
                if st.button(btn_label):
                    if db["status"] == "break":
                        db["status"] = "running"
                        db["last_update"] = time.time()
                    else:
                        db["status"] = "counting"
                    st.rerun()
            with c3:
                if db["status"] == "running":
                    if st.button("⏸️ راحة"):
                        db["status"] = "break"
                        st.rerun()
            with c4:
                if st.button("🛑 إنهاء الكل"):
                    db.update({"room_id": None, "members": [], "status": "off"})
                    st.rerun()

# تحديث تلقائي عام
if db["room_id"] or db["schedule"]:
    time.sleep(2)
    st.rerun()
