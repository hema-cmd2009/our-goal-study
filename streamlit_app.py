import streamlit as st
import time

# 1. إعدادات التصميم (إصلاح ألوان الخطوط والمربعات)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* جعل الخط أبيض في خانات الإدخال */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: white !important; font-size: 18px !important; }
    
    /* تصميم مربعات الأعضاء المحترف */
    .member-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 20px; text-align: center; border-bottom: 4px solid #D4AF37;
    }
    .avatar-img { font-size: 50px; margin-bottom: 10px; display: block; }
    .study-subject { color: #000; font-size: 13px; background: #D4AF37; padding: 3px 10px; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 8px; }

    /* شاشة الاستعداد والتايمر */
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .ready-msg { font-size: 60px; text-align: center; color: #fff; font-weight: bold; animation: pulse 1s infinite; margin: 20px; }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    
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
    mins, secs = divmod(int(seconds), 60)
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
        # عرض الحالة بناءً على قرار الأدمن
        if db["status"] == "ready":
            st.markdown("<div class='ready-msg'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        elif db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        elif db["status"] == "break":
            st.markdown("<h2 style='text-align:center;'>☕ وقت راحة..</h2>", unsafe_allow_html=True)
        
        # عرض المربعات للأعضاء
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span class='avatar-img'>{m['avatar']}</span>
                        <b style='color:white;'>{m['name']}</b><br>
                        <span class='study-subject'>📖 {m['subject']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة السر", type="password")
    if admin_pass == "our122122":
        # عرض سجل المستخدمين للأدمن
        st.subheader("👥 الحاضرون الآن (للمسؤول)")
        if db["members"]:
            st.table(db["members"])
        
        st.write("---")
        # جدول المواعيد
        st.subheader("📅 إضافة موعد للجدول")
        col_t, col_d = st.columns(2)
        with col_t: r_time = st.text_input("الوقت (مثلاً 06:00 م)")
        with col_d: r_dur = st.number_input("المدة", 5, 120, 60)
        if st.button("نشر في الجدول"):
            db["schedule"].append({"time": r_time, "duration": r_dur})
            st.success("تم النشر")

        st.write("---")
        # أزرار التحكم بالروم
        if not db["room_id"]:
            if st.button("🚀 إنشاء روم جديدة"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = 3600 
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"الكود: {db['room_id']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1: 
                if st.button("🔔 استعدوا"): db["status"] = "ready"
            with c2: 
                if st.button("▶️ ابدأ"): 
                    db["status"] = "running"
                    db["last_update"] = time.time()
                    st.rerun()
            with c3: 
                if st.button("⏸️ راحة"): db["status"] = "break"
            with c4: 
                if st.button("🛑 إنهاء الكل"):
                    db["room_id"] = None
                    db["members"] = []
                    db["status"] = "off"
                    st.rerun()

# تحديث تلقائي
if db["room_id"]:
    time.sleep(2)
    st.rerun()
