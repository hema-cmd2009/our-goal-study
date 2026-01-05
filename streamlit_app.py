import streamlit as st
import time
import base64

# 1. إعدادات التصميم والأصوات
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# وظيفة لتحويل ملفات الصوت (أو روابط) لتشغيلها تلقائياً
def play_sound(sound_url):
    sound_html = f"""
    <iframe src="{sound_url}" allow="autoplay" style="display:none"></iframe>
    <audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# روابط أصوات (يمكنك استبدالها بروابط مباشرة لملفات MP3 إذا أردت)
SOUNDS = {
    "notification": "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3", # جرس قصير
    "start": "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",        # جرس تنبيه
    "finish": "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"       # جرس نهاية
}

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    input, textarea { color: #fff !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    .schedule-info { background: #fdf2d0; color: #333; padding: 10px; border-radius: 8px; border-left: 5px solid #D4AF37; margin-bottom: 5px; font-weight: bold; }
    .main-timer { font-size: 110px; text-align: center; font-weight: bold; color: #D4AF37; margin: 10px 0; }
    .countdown-big { font-size: 130px; text-align: center; color: #ff4b4b; font-weight: bold; }
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
        "countdown": 0, "admin_msg": "", "raised_hands": [], "sound_trigger": ""
    }

db = get_db()

if 'page' not in st.session_state: st.session_state.page = "login"

# ----------------- واجهة الغرفة -----------------

if st.session_state.page == "login":
    st.title("🎓 تسجيل الدخول")
    name = st.text_input("اسمك")
    goal = st.text_input("هدفك اليوم")
    if st.button("🚀 دخول"):
        if name and goal:
            st.session_state.user_name = name
            st.session_state.user_goal = goal
            st.session_state.page = "waiting"
            st.rerun()

elif st.session_state.page == "waiting":
    st.header("⏳ قائمة الانتظار")
    if db["schedule"]:
        st.markdown("<h3 style='color:#D4AF37;'>📅 الجدول الدراسي</h3>", unsafe_allow_html=True)
        for item in db["schedule"]:
            st.markdown(f"<div class='schedule-info'>⏰ {item['time']} | ⏳ {item['duration']} دقيقة</div>", unsafe_allow_html=True)
    
    st.write("---")
    code_in = st.text_input("كود الروم")
    if st.button("🚪 انضمام"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"
            st.rerun()

elif st.session_state.page == "room":
    # تشغيل الصوت عند الحاجة
    if db["sound_trigger"]:
        play_sound(SOUNDS[db["sound_trigger"]])
        db["sound_trigger"] = "" # تصفير المحفز بعد التشغيل

    if db["admin_msg"]:
        st.markdown(f"<div style='background:#D4AF37; color:black; padding:20px; border-radius:10px; text-align:center; font-size:30px; font-weight:bold;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    col_h1, col_h2 = st.columns([4, 1])
    with col_h2:
        if st.button("✋ رفع اليد"):
            if st.session_state.user_name not in db["raised_hands"]:
                db["raised_hands"].append(st.session_state.user_name)
                st.toast("تم رفع يدك!")

    # منطق الحالات مع الأصوات
    if db["status"] == "ready":
        st.markdown("<div class='countdown-big'>🔔 استعدوووووو</div>", unsafe_allow_html=True)
    
    elif db["status"] == "counting":
        if db["countdown"] == 10: db["sound_trigger"] = "start" # جرس بدء العد
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
            db["status"] = "off"
            db["sound_trigger"] = "finish" # جرس النهاية
            st.balloons()
        else:
            time.sleep(1); st.rerun()

    elif db["status"] == "pre_break":
        if db["countdown"] == 10: db["sound_trigger"] = "notification"
        st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big' style='font-size:50px;'>☕ الراحة تبدأ بعد: {db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: 
            db["status"] = "on_break"
            db["last_update"] = time.time()
            db["sound_trigger"] = "start"
        st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown("<h1 style='text-align:center;'>☕ وقت استراحة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_seconds'])}</div>", unsafe_allow_html=True)
        if db["break_seconds"] <= 0: 
            db["status"] = "pre_resume"
            db["countdown"] = 10
            db["sound_trigger"] = "finish"
        time.sleep(1); st.rerun()

    # عرض مربعات الطلاب
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            hand = "✋" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand}<br>👤<br><b>{m['name']}</b><br><small>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- الإدارة -----------------
with st.expander("🛠️ لوحة الإدارة"):
    if st.text_input("كلمة السر",
