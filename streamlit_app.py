import streamlit as st
import time
from datetime import datetime, timedelta

# 1. إعدادات التصميم (Dark Gold Theme)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* جعل الخط أبيض وواضح في كل الخانات */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; font-size: 18px; }
    
    /* تنسيق المربعات والتايمر */
    .schedule-box { border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; background: #111; margin-bottom: 25px; }
    .wait-timer { font-size: 50px; color: #fff; text-align: center; font-weight: bold; text-shadow: 0 0 10px #D4AF37; }
    .member-card { background: #111; border: 1px solid #333; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37; }
    .study-subject { color: #000; background: #D4AF37; padding: 2px 8px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 5px; }
    .main-timer { font-size: 110px; text-align: center; font-weight: bold; color: #D4AF37; }
    .countdown-10 { font-size: 200px; text-align: center; color: #D4AF37; font-weight: bold; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100%; height: 50px; }
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

# أ. جدول المواعيد الخارجي (يظهر قبل الدخول)
if db["schedule"] and not st.session_state.get('joined', False):
    st.markdown("<div class='schedule-box'><h2 style='text-align:center; color:#D4AF37;'>📅 مواعيد الرومات القادمة</h2></div>", unsafe_allow_html=True)
    for item in db["schedule"]:
        c_info, c_timer = st.columns([2, 1])
        with c_info:
            st.markdown(f"### ⏰ الموعد: {item['time']} \n **المدة:** {item['duration']} دقيقة")
        with c_timer:
            # ضبط التوقيت ليكون محلياً (إصلاح مشكلة الـ 4 ساعات)
            now = datetime.now()
            try:
                t_p = item['time'].split(':')
                target = now.replace(hour=int(t_p[0]), minute=int(t_p[1]), second=0, microsecond=0)
                if target < now: target += timedelta(days=1)
                diff = target - now
                st.markdown(f"<div class='wait-timer'>{str(diff).split('.')[0]}</div>", unsafe_allow_html=True)
            except: st.write("تنسيق الوقت خطأ")
    st.write("---")

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not st.session_state.get('joined', False):
        st.subheader("🔑 انضم للروم الحالية")
        c1, c2, c3 = st.columns(3)
        code_in = c1.text_input("كود الروم")
        name_in = c2.text_input("اسمك")
        subj_in = c3.text_input("هتذاكر إيه؟")
        if st.button("🚀 انضمام"):
            if db["room_id"] and code_in == db["room_id"] and name_in and subj_in:
                db["members"].append({"name": name_in, "subject": subj_in})
                st.session_state.joined = True
                st.rerun()
            else: st.error("تأكد من البيانات والكود")
    else:
        # نظام الحالات (العد التنازلي والتايمر)
        if db["status"] == "ready":
            st.markdown("<h1 style='text-align:center;'>⚠️ استعدووووو...</h1>", unsafe_allow_html=True)
        elif db["status"] == "counting":
            for i in range(10, 0, -1):
                st.markdown(f"<div class='countdown-10'>{i}</div>", unsafe_allow_html=True)
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
            st.markdown("<h1 style='text-align:center;'>☕ وقت راحة.. ارتاح شوية</h1>", unsafe_allow_html=True)
            st.markdown(f"<div class='main-timer' style='color:#555;'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)

        st.write("---")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'><span style='font-size:40px;'>👤</span><br><b style='color:white;'>{m['name']}</b><br><span class='study-subject'>📖 {m['subject']}</span></div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    pwd = st.text_input("كلمة السر", type="password")
    if pwd == "our122122":
        st.subheader("👥 الحاضرون الآن")
        if db["members"]: st.table(db["members"])
        
        st.write("---")
        if not db["room_id"]:
            m_val = st.number_input("المدة بالدقائق", 5, 120, 45)
            if st.button("🚀 فتح روم جديدة"):
                import random
                db.update({"room_id": str(random.randint(100000, 999999)), "remaining_seconds": m_val * 60, "status": "waiting"})
                st.rerun()
        else:
            st.info(f"كود الروم الحالي: {db['room_id']}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔔 استعدوا"):
                    db["status"] = "ready"
                    st.rerun()
            with col2:
                # إصلاح خطأ السنتاكس في علامات التنصيص
                label = "▶️ بدء (10 ثواني)" if db["status"] != "break" else "▶️ استكمال"
                if st.button(label):
                    if db["status"] == "break":
                        db["status"] = "running"
                        db["last_update"] = time.time()
                    else:
                        db["status"] = "counting"
                    st.rerun()
            with col3:
                if st.button("⏸️ راحة (إيقاف)"):
                    db["status"] = "break"
                    st.rerun()
            with col4:
                if st.button("🛑 إنهاء الروم"):
                    db.update({"room_id": None, "members": [], "status": "off"})
                    st.rerun()

        st.write("---")
        st.subheader("📅 إضافة للجدول الخارجي")
        c_t, c_d = st.columns(2)
        t_in = c_t.text_input("الوقت (مثلاً 20:00)")
        d_in = c_d.number_input("المدة (دقيقة)", 5, 120, 45, key="admin_d")
        if st.button("➕ نشر الموعد"):
            db["schedule"].append({"time": t_in, "duration": d_in})
            st.rerun()

# تحديث تلقائي للمتصفح
if db["room_id"] or db["schedule"]:
    time.sleep(2)
    st.rerun()
