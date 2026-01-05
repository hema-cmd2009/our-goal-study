import streamlit as st
import time
import random

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

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

# CSS المطور (شريط الجولات العلوي + الخط الأبيض)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #ffffff !important; font-family: 'Cairo', sans-serif; }
    
    h1, h2, h3, p, span, label, div { color: #ffffff !important; }
    
    /* شريط الجولات العلوي */
    .rounds-bar {
        display: flex; justify-content: space-around; background: #111; 
        padding: 15px; border-radius: 50px; border: 1px solid #D4AF37; margin-bottom: 30px;
    }
    .round-step { padding: 5px 20px; border-radius: 50px; font-weight: bold; border: 1px solid #333; }
    .round-active { background: #D4AF37; color: #000 !important; box-shadow: 0 0 15px #D4AF37; }
    .round-done { text-decoration: line-through; color: #555 !important; opacity: 0.5; }

    .stTextInput>div>div>input {
        background-color: #111 !important; color: #ffffff !important;
        border: 2px solid #D4AF37 !important; border-radius: 50px !important;
    }
    
    .member-card { 
        background: #1a1a1a; border: 2px solid #D4AF37; 
        border-radius: 25px; padding: 20px; text-align: center; margin: 10px;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #F2D472) !important;
        color: #000 !important; font-weight: bold !important; border-radius: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# ----------------- الواجهات -----------------

if st.session_state.page == "login":
    st.markdown("<h1 style='text-align:center;'>🎓 our goal study</h1>", unsafe_allow_html=True)
    u_name = st.text_input("اسمك المستعار")
    u_goal = st.text_input("ما هو هدفك اليوم؟")
    if st.button("🚀 دخول"):
        if u_name and u_goal:
            st.session_state.user_name, st.session_state.user_goal = u_name, u_goal
            st.session_state.page = "waiting"; st.rerun()

elif st.session_state.page == "waiting":
    st.markdown("<h2 style='text-align:center;'>📋 الجدول المعلن</h2>", unsafe_allow_html=True)
    for item in db["schedule"]:
        st.markdown(f"<div style='background:#fff9e6; color:#000 !important; padding:10px; border-radius:15px; margin:5px;'>⏰ {item['time']} | جولات: {item['rounds']} | مدة: {item['duration']}د</div>", unsafe_allow_html=True)
    st.write("---")
    code_in = st.text_input("كود الروم الذهبي")
    if st.button("🚪 انضمام"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"; st.rerun()

elif st.session_state.page == "room":
    if db["trigger_sound"]: play_audio(db["trigger_sound"]); db["trigger_sound"] = None
    if db["trigger_voice"]: play_voice_cd(db["trigger_voice"]); db["trigger_voice"] = None

    # شريط الجولات العلوي (فوق الوقت)
    if db["total_rounds"] > 0:
        bar_html = "<div class='rounds-bar'>"
        for r in range(1, db["total_rounds"] + 1):
            status_class = "round-done" if r < db["current_round"] else ("round-active" if r == db["current_round"] else "")
            bar_html += f"<div class='round-step {status_class}'>جولة {r}</div>"
        bar_html += "</div>"
        st.markdown(bar_html, unsafe_allow_html=True)

    # التنبيهات (تعمل في كل الحالات بما فيها الراحة)
    if db["admin_msg"]:
        st.markdown(f"<div style='background:rgba(212,175,55,0.2); border:1px solid #D4AF37; padding:15px; border-radius:50px; text-align:center; margin-bottom:10px;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # منطق التايمر
    if db["status"] == "counting":
        db["trigger_voice"] = str(db["countdown"])
        st.markdown(f"<h1 style='font-size:150px; text-align:center; color:#ff4b4b;'>{db['countdown']}</h1>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: db["status"] = "running"; db["last_update"] = time.time()
        st.rerun()

    elif db["status"] == "running":
        now = time.time()
        db["study_time"] -= (now - db["last_update"]); db["last_update"] = now
        st.markdown("<h2 style='text-align:center;'>📖 وقت التركيز</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center; font-size:100px; color:#D4AF37;'>{format_time(db['study_time'])}</h1>", unsafe_allow_html=True)
        if db["study_time"] <= 0:
            db["status"] = "on_break"; db["last_update"] = time.time(); db["trigger_sound"] = SOUNDS["finish_study"]
        time.sleep(1); st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_time"] -= (now - db["last_update"]); db["last_update"] = now
        if 0 < db["break_time"] <= 10: db["trigger_sound"] = SOUNDS["warning_break"]
        st.markdown("<h2 style='text-align:center;'>☕ استراحة قصيرة</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{format_time(db['break_time'])}</h1>", unsafe_allow_html=True)
        if db["break_time"] <= 0:
            if db["current_round"] < db["total_rounds"]:
                db["current_round"] += 1; db["status"] = "counting"; db["countdown"] = 10
                db["study_time"], db["break_time"] = db["study_time_orig"], db["break_time_orig"]
            else: db["status"] = "finished"; st.balloons()
        time.sleep(1); st.rerun()

    # عرض الطلاب
    st.write("---")
    if st.button("✋ رفع يد"):
        if st.session_state.user_name not in db["raised_hands"]: db["raised_hands"].append(st.session_state.user_name)
    
    cols = st.columns(5)
    for i, m in enumerate(db["members"]):
        with cols[i % 5]:
            hand = "<div style='background:#ff4b4b; border-radius:10px; padding:2px;'>✋ مرفوعة</div>" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand}<br>👤<br><b>{m['name']}</b></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة -----------------
with st.expander("🛠️ التحكم بالروم"):
    if st.text_input("كلمة السر", type="password") == "our122122":
        if not db["room_id"]:
            c1, c2, c3 = st.columns(3)
            r_num = c1.number_input("جولات", 1, 10, 3)
            s_min = c2.number_input("دراسة", 1, 120, 25)
            b_min = c3.number_input("راحة", 1, 30, 5)
            if st.button("🚀 إنشاء"):
                db.update({"room_id": str(random.randint(1000, 9999)), "total_rounds": r_num, "current_round": 1, 
                           "study_time": s_min*60, "break_time": b_min*60, "study_time_orig": s_min*60, "break_time_orig": b_min*60})
                st.rerun()
        else:
            st.write(f"الكود: {db['room_id']}")
            if st.button("▶️ بدء"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            msg = st.text_area("أرسل تنبيه")
            if st.button("📢 إرسال"): db["admin_msg"] = msg; db["trigger_sound"] = SOUNDS["notif"]; st.rerun()
            if st.button("🗑️ مسح الرفع"): db["raised_hands"] = []; st.rerun()
            if st.button("🛑 إنهاء"): db.update({"room_id": None, "members": [], "status": "off"}); st.rerun()

if db["room_id"] and st.session_state.page == "room":
    time.sleep(2); st.rerun()
