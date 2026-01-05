import streamlit as st
import time

# 1. إعدادات التصميم (إصلاح الألوان والوميض)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* جعل الخطوط بيضاء وواضحة جداً */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; }
    
    .schedule-box { border: 2px solid #D4AF37; padding: 15px; border-radius: 15px; background: #111; margin-bottom: 20px; }
    .member-card { background: #111; border: 1px solid #333; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37; }
    .study-subject { color: #000; background: #D4AF37; padding: 2px 8px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 5px; }
    .main-timer { font-size: 110px; text-align: center; font-weight: bold; color: #D4AF37; }
    .notice-text { font-size: 60px; text-align: center; color: #D4AF37; font-weight: bold; margin-top: 20px; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100%; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "remaining_seconds": 0, "last_update": None,
        "members": [], "schedule": [], "countdown_val": 10
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- الواجهة -----------------
st.image("logo.png", width=90)

# أ. الجدول الخارجي (يظهر قبل تسجيل الدخول)
if db["schedule"] and not st.session_state.get('joined', False):
    st.markdown("<div class='schedule-box'><h2 style='text-align:center; color:#D4AF37;'>📅 جدول المواعيد القادمة</h2></div>", unsafe_allow_html=True)
    for item in db["schedule"]:
        st.markdown(f"### ⏰ الموعد: <span style='color:#D4AF37;'>{item['time']}</span> | المدة: {item['duration']} دقيقة", unsafe_allow_html=True)
    st.write("---")

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not st.session_state.get('joined', False):
        st.subheader("🔑 دخول الروم")
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
        # نظام الحالات والإشعارات
        if db["status"] == "ready":
            st.markdown("<div class='notice-text'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        
        elif db["status"] == "break":
            st.markdown("<div class='notice-text'>☕ وقت راحة.. ارتاح شوية</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='main-timer' style='color:#555;'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            
        elif db["status"] == "counting":
            if db["countdown_val"] > 0:
                st.markdown(f"<div style='font-size:180px; text-align:center; color:#D4AF37; font-weight:bold;'>{db['countdown_val']}</div>", unsafe_allow_html=True)
                time.sleep(1); db["countdown_val"] -= 1; st.rerun()
            else:
                db["status"] = "running"; db["last_update"] = time.time(); st.rerun()
                
        elif db["status"] == "running":
            now = time.time()
            db["remaining_seconds"] -= (now - db["last_update"])
            db["last_update"] = now
            if db["remaining_seconds"] > 0:
                st.markdown(f"<div class='main-timer'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
                time.sleep(1); st.rerun()
            else: db["status"] = "off"; st.balloons()

        st.write("---")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'>👤<br><b style='color:white;'>{m['name']}</b><br><span class='study-subject'>📖 {m['subject']}</span></div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    pwd = st.text_input("كلمة السر", type="password")
    if pwd == "our122122":
        if not db["room_id"]:
            m_v = st.number_input("المدة بالدقائق", 5, 120, 45)
            if st.button("🚀 فتح روم جديدة"):
                import random
                db.update({"room_id": str(random.randint(100000, 999999)), "remaining_seconds": m_v * 60, "status": "waiting"})
                st.rerun()
        else:
            st.info(f"كود الروم: {db['room_id']}")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                if st.button("🔔 استعدوا"): db["status"] = "ready"; st.rerun()
            with c2:
                if st.button("🔟 عد 10 ثواني"): db["status"] = "counting"; db["countdown_val"] = 10; st.rerun()
            with c3:
                if st.button("▶️ بدء التايمر"): db["status"] = "running"; db["last_update"] = time.time(); st.rerun()
            with c4:
                # زر الراحة والاستكمال
                btn_label = "⏸️ خذ راحة" if db["status"] == "running" else "▶️ استكمال"
                if st.button(btn_label):
                    if db["status"] == "running": db["status"] = "break"
                    else: db["status"] = "running"; db["last_update"] = time.time()
                    st.rerun()
            with c5:
                if st.button("🛑 إنهاء الكل"): db.update({"room_id": None, "members": [], "status": "off"}); st.rerun()

        st.write("---")
        st.subheader("📅 إدارة المواعيد")
        if st.button("🗑️ مسح الجدول بالكامل", key="clear_schedule"):
            db["schedule"] = []
            st.rerun()
            
        ca, cb = st.columns(2)
        t_in = ca.text_input("الساعة (مثلاً 20:00)")
        d_in = cb.number_input("المدة", 5, 120, 45, key="sched_duration")
        if st.button("➕ إضافة موعد"):
            db["schedule"].append({"time": t_in, "duration": d_in})
            st.rerun()

if db["room_id"] and db["status"] != "off":
    time.sleep(2); st.rerun()
