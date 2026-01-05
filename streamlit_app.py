import streamlit as st
import time

# 1. إعدادات التصميم (إصلاح الألوان والوميض)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* جعل الخطوط بيضاء وواضحة جداً في كل الحقول */
    input, textarea { color: #fff !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; font-size: 1.1rem; }
    
    .main-timer { font-size: clamp(60px, 10vw, 120px); text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 20px #D4AF37; margin: 20px 0; }
    .countdown-big { font-size: clamp(80px, 12vw, 150px); text-align: center; color: #ff4b4b; font-weight: bold; }
    .notice-box { background: #D4AF37; color: #000; padding: 25px; border-radius: 15px; text-align: center; font-size: clamp(20px, 5vw, 40px); font-weight: bold; margin-bottom: 30px; border: 3px solid #fff; }
    .member-card { background: #111; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; height: 100%; }
    
    /* تنسيق الأزرار */
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100%; border: none !important; }
    .stButton>button:hover { background: #fff !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة (تخزين الحالة)
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "study_seconds": 0, "break_seconds": 0,
        "last_update": None, "members": [], "schedule": [], 
        "countdown": 0, "admin_msg": ""
    }

db = get_db()

# إدارة التنقل بين الصفحات محلياً لكل مستخدم
if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- واجهات المستخدم -----------------

# الصفحة 1: تسجيل الدخول
if st.session_state.page == "login":
    st.title("🎓 مرحباً بك في our goal study")
    with st.container():
        name = st.text_input("اسمك المستعار")
        goal = st.text_input("ما هو هدفك الدراسي اليوم؟")
        if st.button("🚀 دخول"):
            if name and goal:
                st.session_state.user = {"name": name, "goal": goal}
                st.session_state.page = "waiting"
                st.rerun()
            else: st.warning("من فضلك أدخل الاسم والهدف")

# الصفحة 2: قمة الانتظار والجدول
elif st.session_state.page == "waiting":
    st.header("⏳ قائمة الانتظار")
    
    # عرض الجدول في الأعلى كما طلبت
    if db["schedule"]:
        with st.container():
            st.markdown("<h3 style='color:#D4AF37;'>📅 الجدول الدراسي</h3>", unsafe_allow_html=True)
            for item in db["schedule"]:
                st.info(f"⏰ الموعد: {item['time']} | ⏳ المدة: {item['duration']} دقيقة")
    
    st.write("---")
    code_in = st.text_input("أدخل كود الروم للانضمام")
    if st.button("🚪 انضمام الآن"):
        if db["room_id"] and code_in == db["room_id"]:
            if st.session_state.user not in db["members"]:
                db["members"].append(st.session_state.user)
            st.session_state.page = "room"
            st.rerun()
        else: st.error("الكود غير صحيح أو الروم لم تبدأ بعد")

# الصفحة 3: الروم الدراسية (المستقلة)
elif st.session_state.page == "room":
    # 1. التنبيهات الإدارية (تظهر للكل بخط كبير)
    if db["admin_msg"]:
        st.markdown(f"<div class='notice-box'>{db['admin_msg']}</div>", unsafe_allow_html=True)

    # 2. منطق الحالات (التايمر والعد التنازلي)
    if db["status"] == "ready":
        st.markdown("<div class='countdown-big'>🔔 استعدوووووو</div>", unsafe_allow_html=True)
    
    elif db["status"] == "counting":
        if db["countdown"] > 0:
            st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
            time.sleep(1)
            db["countdown"] -= 1
            st.rerun()
        else:
            db["status"] = "running"
            db["last_update"] = time.time()
            st.rerun()

    elif db["status"] == "running":
        now = time.time()
        db["study_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
        if db["study_seconds"] <= 0: 
            db["status"] = "off"
            st.balloons()
        else:
            time.sleep(1)
            st.rerun()

    elif db["status"] == "pre_break":
        if db["countdown"] > 0:
            st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:25px;'>☕ الراحة تبدأ بعد: {db['countdown']}</p>", unsafe_allow_html=True)
            time.sleep(1)
            db["countdown"] -= 1
            st.rerun()
        else:
            db["status"] = "on_break"
            db["last_update"] = time.time()
            st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>☕ وقت استراحة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_seconds'])}</div>", unsafe_allow_html=True)
        if db["break_seconds"] <= 0:
            db["status"] = "pre_resume"
            db["countdown"] = 10
        time.sleep(1)
        st.rerun()

    elif db["status"] == "pre_resume":
        st.markdown("<h1 style='text-align:center;'>⚠️ استعد للعودة للمذاكرة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1)
        db["countdown"] -= 1
        if db["countdown"] < 0:
            db["status"] = "running"
            db["last_update"] = time.time()
        st.rerun()

    # 3. عرض مربعات الأشخاص
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            st.markdown(f"<div class='member-card'>👤<br><b>{m['name']}</b><br><small style='color:#aaa;'>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة -----------------
st.write("---")
with st.expander("🛠️ لوحة تحكم الإدارة"):
    admin_pwd = st.text_input("كلمة مرور الإدارة", type="password")
    if admin_pwd == "our122122":
        if not db["room_id"]:
            c1, c2 = st.columns(2)
            s_min = c1.number_input("دقائق المذاكرة", 5, 120, 45)
            b_min = c2.number_input("دقائق الراحة", 1, 30, 5)
            if st.button("🚀 فتح الروم الآن"):
                import random
                db.update({"room_id": str(random.randint(1000, 9999)), "study_seconds": s_min*60, "break_seconds": b_min*60, "status": "waiting", "admin_msg": ""})
                st.rerun()
        else:
            st.success(f"الروم مفتوحة | الكود: {db['room_id']}")
            ac1, ac2, ac3, ac4 = st.columns(4)
            with ac1:
                if st.button("🔔 إرسال استعدوا"): db["status"] = "ready"; st.rerun()
            with ac2:
                if st.button("▶️ ابدأ الروم (10 ث)"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            with ac3:
                if st.button("⏸️ طلب راحة"): db["status"] = "pre_break"; db["countdown"] = 10; st.rerun()
            with ac4:
                if st.button("🛑 إنهاء الروم"): db.update({"room_id": None, "members": [], "status": "off"}); st.rerun()
            
            # حقل التنبيهات
            st.write("---")
            new_msg = st.text_area("ارسل تنبيه مباشر للطلاب", placeholder="اكتب هنا...")
            bc1, bc2 = st.columns(2)
            if bc1.button("📢 نشر التنبيه"): db["admin_msg"] = new_msg; st.rerun()
            if bc2.button("🗑️ مسح التنبيه"): db["admin_msg"] = ""; st.rerun()

        # إدارة الجدول
        st.write("---")
        st.subheader("📅 إدارة جدول المواعيد")
        if st.button("🗑️ تفريغ الجدول"): db["schedule"] = []; st.rerun()
        tc1, tc2 = st.columns(2)
        time_val = tc1.text_input("الوقت (مثلاً 09:00 م)")
        dur_val = tc2.number_input("المدة", 5, 120, 45, key="sch_dur")
        if st.button("➕ إضافة للجدول"):
            db["schedule"].append({"time": time_val, "duration": dur_val})
            st.rerun()

# تحديث تلقائي "ذكي" لضمان ثبات الشاشة
if db["room_id"] and st.session_state.page != "login" and db["status"] == "waiting":
    time.sleep(5)
    st.rerun()
