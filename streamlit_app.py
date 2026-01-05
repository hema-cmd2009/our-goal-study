import streamlit as st
import time
import random

# 1. إعدادات الصفحة والتصميم الصارم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# روابط الأصوات (مباشرة)
NOTIF_SOUND = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
START_SOUND = "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"
FINISH_SOUND = "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"

def play_audio(url):
    st.markdown(f'<iframe src="{url}" allow="autoplay" style="display:none"></iframe>', unsafe_allow_html=True)

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* إصلاح لون الحقول والنصوص لتكون بيضاء واضحة */
    input, textarea { color: #fff !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; }
    
    .schedule-info { background: #fff9e6; color: #444; padding: 10px; border-radius: 8px; border-right: 5px solid #D4AF37; margin-bottom: 5px; font-weight: bold; }
    .main-timer { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; margin: 10px 0; }
    .countdown-big { font-size: 120px; text-align: center; color: #ff4b4b; font-weight: bold; }
    .member-card { background: #111; border: 1px solid #D4AF37; border-radius: 12px; padding: 10px; text-align: center; }
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; width: 100%; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات (إصلاح أخطاء التعريف)
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "study_seconds": 0, "break_seconds": 0,
        "last_update": None, "members": [], "schedule": [], 
        "countdown": 0, "admin_msg": "", "raised_hands": [], "trigger_sound": None
    }

db = get_db()

# إدارة التنقل
if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- منطق الصفحات -----------------

# 1. صفحة التسجيل
if st.session_state.page == "login":
    st.title("🎓 مرحباً بك في our goal study")
    u_name = st.text_input("اسمك الكريم")
    u_goal = st.text_input("ما هو هدفك الدراسي اليوم؟")
    if st.button("🚀 تسجيل الدخول"):
        if u_name and u_goal:
            st.session_state.user_name = u_name
            st.session_state.user_goal = u_goal
            st.session_state.page = "waiting"
            st.rerun()
        else: st.warning("يرجى إكمال البيانات")

# 2. صفحة الانتظار والجدول
elif st.session_state.page == "waiting":
    st.header("⏳ قائمة الانتظار")
    if db["schedule"]:
        st.subheader("📅 جدول المواعيد")
        for item in db["schedule"]:
            st.markdown(f"<div class='schedule-info'>⏰ {item['time']} | ⏳ {item['duration']} دقيقة</div>", unsafe_allow_html=True)
    
    st.write("---")
    code_in = st.text_input("أدخل كود الروم للانضمام")
    if st.button("🚪 انضمام"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"
            st.rerun()
        else: st.error("الكود غير صحيح أو الروم لم تبدأ")

# 3. صفحة الروم المستقلة
elif st.session_state.page == "room":
    if db["trigger_sound"]:
        play_audio(db["trigger_sound"])
        db["trigger_sound"] = None

    if db["admin_msg"]:
        st.markdown(f"<div style='background:#D4AF37; color:black; padding:20px; border-radius:10px; text-align:center; font-size:30px; font-weight:bold;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # ميزة رفع اليد
    if st.button("✋ رفع اليد"):
        if st.session_state.user_name not in db["raised_hands"]:
            db["raised_hands"].append(st.session_state.user_name)
            st.toast("تم رفع يدك!")

    # منطق الحالات (المذاكرة والراحة)
    if db["status"] == "ready":
        st.markdown("<div class='countdown-big'>🔔 استعدوووووو</div>", unsafe_allow_html=True)
    
    elif db["status"] == "counting":
        if db["countdown"] == 10: db["trigger_sound"] = START_SOUND
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
        if db["study_seconds"] <= 0: 
            db["status"] = "off"; db["trigger_sound"] = FINISH_SOUND; st.balloons()
        else: time.sleep(1); st.rerun()

    elif db["status"] == "pre_break":
        st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big' style='font-size:50px;'>☕ الراحة تبدأ بعد: {db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: 
            db["status"] = "on_break"; db["last_update"] = time.time(); db["trigger_sound"] = START_SOUND
        st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown("<h2 style='text-align:center;'>☕ وقت راحة</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_seconds'])}</div>", unsafe_allow_html=True)
        if db["break_seconds"] <= 0: 
            db["status"] = "pre_resume"; db["countdown"] = 10; db["trigger_sound"] = FINISH_SOUND
        time.sleep(1); st.rerun()

    elif db["status"] == "pre_resume":
        st.markdown("<h2 style='text-align:center;'>⚠️ العودة في:</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: 
            db["status"] = "running"; db["last_update"] = time.time(); db["trigger_sound"] = START_SOUND
        st.rerun()

    # عرض الطلاب
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            hand = "✋" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand}<br>👤<br><b>{m['name']}</b><br><small>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة (مؤمنة) -----------------
st.write("---")
with st.expander("🛠️ لوحة الإدارة"):
    pwd = st.text_input("كلمة السر", type="password")
    if pwd == "our122122":
        if not db["room_id"]:
            c1, c2 = st.columns(2)
            s_m = c1.number_input("المذاكرة (دقيقة)", 5, 120, 45)
            b_m = c2.number_input("الراحة (دقيقة)", 1, 30, 5)
            if st.button("🚀 فتح الروم الآن"):
                db.update({"room_id": str(random.randint(1000, 9999)), "study_seconds": s_m*60, "break_seconds": b_m*60, "status": "waiting"})
                st.rerun()
        else:
            st.success(f"كود الروم: {db['room_id']}")
            ac1, ac2, ac3, ac4 = st.columns(4)
            with ac1:
                if st.button("🔔 استعدوا"): db["status"] = "ready"; db["trigger_sound"] = NOTIF_SOUND; st.rerun()
            with ac2:
                if st.button("▶️ ابدأ"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            with ac3:
                if st.button("⏸️ راحة"): db["status"] = "pre_break"; db["countdown"] = 10; st.rerun()
            with ac4:
                if st.button("🛑 إنهاء"): db.update({"room_id": None, "members": [], "status": "off", "raised_hands": []}); st.rerun()
            
            if st.button("✅ مسح أيدي الطلاب"): db["raised_hands"] = []; st.rerun()
            msg = st.text_area("رسالة تنبيه")
            if st.button("📢 إرسال"): db["admin_msg"] = msg; db["trigger_sound"] = NOTIF_SOUND; st.rerun()

        # الجدول
        st.write("---")
        t_val = st.text_input("الموعد (مثلاً 09:00 م)")
        d_val = st.number_input("المدة", 5, 120, 45, key="sch_dur")
        if st.button("➕ إضافة موعد"): db["schedule"].append({"time": t_val, "duration": d_val}); st.rerun()
        if st.button("🗑️ مسح الجدول"): db["schedule"] = []; st.rerun()

# تحديث تلقائي آمن
if db["room_id"] and st.session_state.page != "login" and db["status"] != "off":
    time.sleep(2); st.rerun()
