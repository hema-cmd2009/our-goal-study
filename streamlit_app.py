import streamlit as st
import time

# 1. إعدادات التصميم الاحترافي
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    .main-timer { font-size: 120px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 20px #D4AF37; }
    .countdown-big { font-size: 150px; text-align: center; color: #ff4b4b; font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.1);} 100% {transform: scale(1);} }
    .notice-box { background: #D4AF37; color: #000; padding: 20px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; margin: 20px 0; }
    .member-card { background: #111; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; }
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "study_seconds": 0, "break_seconds": 0,
        "last_update": None, "members": [], "schedule": [], 
        "countdown": 0, "admin_msg": ""
    }

db = get_db()

if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- منطق الصفحات -----------------

# صفحة 1: التسجيل
if st.session_state.page == "login":
    st.title("🎓 تسجيل الدخول - our goal study")
    name = st.text_input("اسمك الكريم")
    goal = st.text_input("هتذاكر إيه النهاردة؟")
    if st.button("دخول القائمة"):
        if name and goal:
            st.session_state.user = {"name": name, "goal": goal}
            st.session_state.page = "waiting"
            st.rerun()

# صفحة 2: الانتظار والكود
elif st.session_state.page == "waiting":
    st.header("⏳ قائمة الانتظار")
    # عرض الجدول أولاً كما طلبت
    if db["schedule"]:
        with st.expander("📅 جدول المواعيد القادمة", expanded=True):
            for item in db["schedule"]:
                st.write(f"⏰ {item['time']} | ⏳ {item['duration']} دقيقة")
    
    code_in = st.text_input("أدخل كود الروم للانضمام")
    if st.button("انضمام للروم"):
        if db["room_id"] and code_in == db["room_id"]:
            db["members"].append(st.session_state.user)
            st.session_state.page = "room"
            st.rerun()
        else: st.error("الكود غير صحيح أو الروم مغلقة")

# صفحة 3: الروم المستقلة
elif st.session_state.page == "room":
    # التنبيهات الإدارية
    if db["admin_msg"]:
        st.markdown(f"<div class='notice-box'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # حالات الروم (استعدوا، عد تنازلي، تايمر)
    if db["status"] == "ready":
        st.markdown("<div class='countdown-big'>🔔 استعدوووووو</div>", unsafe_allow_html=True)
    
    elif db["status"] == "counting":
        if db["countdown"] > 0:
            st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
            time.sleep(1); db["countdown"] -= 1; st.rerun()
        else:
            db["status"] = "running"; db["last_update"] = time.time(); st.rerun()

    elif db["status"] == "running":
        now = time.time()
        db["study_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
        if db["study_seconds"] <= 0: db["status"] = "off"; st.balloons()
        time.sleep(1); st.rerun()

    elif db["status"] == "pre_break": # عد تنازلي قبل الراحة
        if db["countdown"] > 0:
            st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center'>الراحة تبدأ بعد: {db['countdown']}</p>", unsafe_allow_html=True)
            time.sleep(1); db["countdown"] -= 1; st.rerun()
        else:
            db["status"] = "on_break"; db["last_update"] = time.time(); st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown("<h1 style='text-align:center;'>☕ وقت راحة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#555;'>{format_time(db['break_seconds'])}</div>", unsafe_allow_html=True)
        if db["break_seconds"] <= 0:
            db["status"] = "pre_resume"; db["countdown"] = 10; st.rerun()
        time.sleep(1); st.rerun()

    elif db["status"] == "pre_resume": # عد تنازلي قبل العودة للمذاكرة
        st.markdown("<h1 style='text-align:center;'>⚠️ استعد للعودة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: db["status"] = "running"; db["last_update"] = time.time()
        st.rerun()

    # عرض مربعات الأشخاص
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            st.markdown(f"<div class='member-card'>👤 <b>{m['name']}</b><br><small>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة (مخفية بكلمة سر) -----------------
st.write("---")
with st.expander("🛠️ لوحة الإدارة"):
    if st.text_input("كلمة السر", type="password") == "our122122":
        # 1. فتح الروم
        if not db["room_id"]:
            c1, c2 = st.columns(2)
            s_m = c1.number_input("دقائق المذاكرة", 5, 120, 45)
            b_m = c2.number_input("دقائق الراحة", 1, 30, 5)
            if st.button("🚀 فتح الروم وتوليد الكود"):
                import random
                db.update({"room_id": str(random.randint(1000, 9999)), "study_seconds": s_m*60, "break_seconds": b_m*60, "status": "waiting"})
                st.rerun()
        else:
            st.success(f"كود الروم الحالي: {db['room_id']}")
            # 2. أزرار التحكم
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔔 استعدوا"): db["status"] = "ready"; st.rerun()
            with col2:
                if st.button("▶️ ابدأ الروم"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            with col3:
                if st.button("⏸️ راحة"): db["status"] = "pre_break"; db["countdown"] = 10; st.rerun()
            with col4:
                if st.button("🛑 إنهاء"): db["status"] = "off"; db["room_id"] = None; db["members"] = []; st.rerun()
            
            # 3. التنبيهات
            msg = st.text_area("اكتب تنبيه للطلاب")
            if st.button("إرسال التنبيه"): db["admin_msg"] = msg; st.rerun()
            if st.button("مسح التنبيه"): db["admin_msg"] = ""; st.rerun()

        # 4. الجدول
        st.write("---")
        if st.button("🗑️ مسح الجدول"): db["schedule"] = []; st.rerun()
        t_i = st.text_input("وقت الموعد (مثلاً 08:00 مساءً)")
        d_i = st.number_input("المدة", 5, 120, 45, key="admin_sc")
        if st.button("➕ إضافة للجدول"): db["schedule"].append({"time": t_i, "duration": d_i}); st.rerun()

# تحديث تلقائي عام للطلاب
if db["status"] != "off" and st.session_state.page != "login":
    time.sleep(2); st.rerun()
