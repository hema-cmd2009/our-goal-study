import streamlit as st
import time

# 1. إعدادات التصميم المتطور
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: white !important; font-size: 18px; }
    
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 20px; text-align: center; border-bottom: 4px solid #D4AF37;
    }
    .study-subject { color: #000; font-size: 13px; background: #D4AF37; padding: 3px 10px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 8px; }

    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .countdown-text { font-size: 150px; text-align: center; color: #fff; font-weight: bold; }
    .status-msg { font-size: 50px; text-align: center; color: #fff; font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; height: 45px; }
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
st.image("logo.png", width=80)

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if db["schedule"]:
        with st.expander("📅 جدول رومات اليوم"):
            for item in db["schedule"]:
                st.write(f"⏰ {item['time']} | ⏳ {item['duration']} دقيقة")

    if not st.session_state.get('joined', False):
        st.subheader("سجل دخولك")
        c_code = st.text_input("كود الروم")
        c_name = st.text_input("اسمك")
        c_subject = st.text_input("هتذاكر إيه النهاردة؟")
        
        if st.button("انضمام الآن"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({"name": c_name, "subject": c_subject, "avatar": "👤"})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("تأكد من الكود والبيانات")
    else:
        # 1. منطق عرض الحالة (العد التنازلي، التايمر، الراحة)
        if db["status"] == "ready":
            st.markdown("<div class='status-msg'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        
        elif db["status"] == "counting":
            # عد تنازلي 3 ثواني
            for i in range(3, 0, -1):
                st.markdown(f"<div class='countdown-text'>{i}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            db["status"] = "running"
            db["last_update"] = time.time()
            st.rerun()

        elif db["status"] == "running":
            now = time.time()
            elapsed = now - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = now
            
            if db["remaining_seconds"] > 0:
                st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                db["status"] = "finished"
                st.balloons()
        
        elif db["status"] == "break":
            st.markdown("<div class='status-msg'>☕ وقت راحة..</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timer-display' style='color:#555'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
        
        elif db["status"] == "finished":
            st.success("🎉 انتهت الجلسة! خذ قسطاً من الراحة.")

        # 2. عرض المربعات (الزملاء)
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span style='font-size:50px;'>{m['avatar']}</span><br>
                        <b style='color:white;'>{m['name']}</b><br>
                        <span class='study-subject'>📖 {m['subject']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة السر", type="password")
    if admin_pass == "our122122":
        st.subheader("👥 الحاضرون الآن")
        st.table(db["members"])
        
        st.write("---")
        # التحكم بالروم
        if not db["room_id"]:
            mins = st.number_input("المدة (دقيقة)", 5, 120, 45)
            if st.button("🚀 إنشاء روم جديدة"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = mins * 60
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"كود الروم: {db['room_id']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🔔 استعدوا"): 
                    db["status"] = "ready"
                    st.rerun()
            with c2:
                if db["status"] != "running":
                    if st.button("▶️ بدء (3 ثواني)"):
                        db["status"] = "counting"
                        st.rerun()
            with c3:
                if db["status"] == "running":
                    if st.button("⏸️ راحة (إيقاف)"):
                        db["status"] = "break"
                        st.rerun()
            with c4:
                if st.button("🛑 إنهاء الروم"):
                    db.update({"room_id": None, "members": [], "status": "off"})
                    st.rerun()
                    
        # إضافة جدول المواعيد
        st.write("---")
        st.subheader("📅 إضافة للجدول")
        col1, col2 = st.columns(2)
        t_val = col1.text_input("الوقت")
        d_val = col2.number_input("المدة", 5, 120, 60, key="admin_dur")
        if st.button("نشر الموعد"):
            db["schedule"].append({"time": t_val, "duration": d_val})
            st.success("تم النشر")

# تحديث تلقائي للطلاب
if db["room_id"] and db["status"] in ["waiting", "ready", "break"]:
    time.sleep(3)
    st.rerun()
