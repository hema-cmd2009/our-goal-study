import streamlit as st
import time
import random

# 1. إعدادات الصفحة والتصميم (UI)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# روابط الأصوات
SOUNDS = {
    "finish_study": "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3",
    "warning_break": "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",
    "notif": "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
}

def play_voice_cd(number):
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={number}&tl=en&client=tw-ob"
    st.markdown(f'<iframe src="{url}" allow="autoplay" style="display:none"></iframe>', unsafe_allow_html=True)

def play_audio(url):
    st.markdown(f'<iframe src="{url}" allow="autoplay" style="display:none"></iframe>', unsafe_allow_html=True)

# CSS الشامل (التصميم البيضاوي + الجدول + رفع اليد)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* الحقول البيضاوية */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111 !important; color: #fff !important;
        border: 2px solid #D4AF37 !important; border-radius: 50px !important;
        padding: 10px 25px !important;
    }
    
    /* الجدول الذهبي الفاتح */
    .schedule-info { 
        background: #fff9e6; color: #444; padding: 15px; 
        border-radius: 20px; border-right: 8px solid #D4AF37; 
        margin-bottom: 10px; font-weight: bold; font-size: 1.1rem;
    }
    
    /* كارت الطالب ورفع اليد */
    .member-card { 
        background: #111; border: 1px solid #D4AF37; 
        border-radius: 40px; padding: 20px; text-align: center; position: relative;
    }
    .hand-icon { 
        background: #ff4b4b; color: white; border-radius: 50px; 
        padding: 2px 10px; font-size: 12px; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #F2D472) !important;
        color: #000 !important; font-weight: bold !important;
        border-radius: 50px !important; height: 45px !important; width: 100% !important;
    }
    .main-timer { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات (Database)
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "current_round": 0, "total_rounds": 0,
        "study_time_orig": 0, "break_time_orig": 0, "study_time": 0, "break_time": 0,
        "last_update": None, "members": [], "schedule": [], "raised_hands": [],
        "countdown": 0, "admin_msg": "", "trigger_sound": None, "trigger_voice": None
    }

db = get_db()

if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- واجهات التطبيق -----------------

if st.session_state.page == "login":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🎓 our goal study</h1>", unsafe_allow_html=True)
    u_name = st.text_input("ادخل اسمك المستعار")
    u_goal = st.text_input("ما هو هدفك اليوم؟")
    if st.button("🚀 تسجيل الدخول"):
        if u_name and u_goal:
            st.session_state.user_name, st.session_state.user_goal = u_name, u_goal
            st.session_state.page = "waiting"; st.rerun()

elif st.session_state.page == "waiting":
    st.markdown("<h2 style='text-align:center;'>⏳ الجدول والمواعيد</h2>", unsafe_allow_html=True)
    if db["schedule"]:
        for item in db["schedule"]:
            st.markdown(f"<div class='schedule-info'>📅 {item['time']} | ⏳ جولات: {item['rounds']} | مدة الجولة: {item['duration']} د</div>", unsafe_allow_html=True)
    
    st.write("---")
    code_in = st.text_input("كود الروم الذهبي")
    if st.button("🚪 انضمام الآن"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"; st.rerun()

elif st.session_state.page == "room":
    if db["trigger_sound"]: play_audio(db["trigger_sound"]); db["trigger_sound"] = None
    if db["trigger_voice"]: play_voice_cd(db["trigger_voice"]); db["trigger_voice"] = None

    if db["admin_msg"]:
        st.markdown(f"<div style='background:rgba(212,175,55,0.2); border:1px solid #D4AF37; padding:15px; border-radius:50px; text-align:center; margin-bottom:20px;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # زر رفع اليد للطالب
    col1, col2 = st.columns([5,1])
    with col2:
        if st.button("✋ رفع يد"):
            if st.session_state.user_name not in db["raised_hands"]:
                db["raised_hands"].append(st.session_state.user_name); st.toast("تم رفع يدك!")

    # منطق التايمر والجولات
    if db["status"] == "counting":
        db["trigger_voice"] = str(db["countdown"])
        st.markdown(f"<div style='font-size:150px; text-align:center; color:#ff4b4b; font-weight:bold;'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: db["status"] = "running"; db["last_update"] = time.time()
        st.rerun()

    elif db["status"] == "running":
        now = time.time()
        db["study_time"] -= (now - db["last_update"]); db["last_update"] = now
        st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>📖 جولة {db['current_round']} - مذاكرة</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer'>{format_time(db['study_time'])}</div>", unsafe_allow_html=True)
        if db["study_time"] <= 0:
            db["status"] = "on_break"; db["last_update"] = time.time(); db["trigger_sound"] = SOUNDS["finish_study"]
        time.sleep(1); st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_time"] -= (now - db["last_update"]); db["last_update"] = now
        if 0 < db["break_time"] <= 10: db["trigger_sound"] = SOUNDS["warning_break"]
        st.markdown(f"<h2 style='text-align:center; color:#fff;'>☕ راحة الجولة {db['current_round']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_time'])}</div>", unsafe_allow_html=True)
        if db["break_time"] <= 0:
            if db["current_round"] < db["total_rounds"]:
                db["current_round"] += 1; db["status"] = "counting"; db["countdown"] = 10
                db["study_time"], db["break_time"] = db["study_time_orig"], db["break_time_orig"]
            else: db["status"] = "finished"; st.balloons()
        time.sleep(1); st.rerun()

    # عرض الطلاب ورفع اليد
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            hand_html = "<div class='hand-icon'>✋ رفع يده</div>" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand_html}👤<br><b>{m['name']}</b></div>", unsafe_allow_html=True
