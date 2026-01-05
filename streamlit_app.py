import streamlit as st
import time
import random

# 1. إعدادات الصفحة والتصميم المتطور (UI)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# روابط الأصوات والمؤثرات
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

# CSS الشامل (التصميم البيضاوي المتطور)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* الحقول البيضاوية */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111 !important; color: #fff !important;
        border: 2px solid #D4AF37 !important; border-radius: 50px !important;
        padding: 10px 25px !important; transition: 0.3s;
    }
    .stTextInput>div>div>input:focus { box-shadow: 0 0 15px rgba(212, 175, 55, 0.5) !important; }
    
    label { color: #D4AF37 !important; font-weight: bold !important; margin-right: 15px !important; }
    
    /* الأزرار البيضاوية الذهبية */
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #F2D472) !important;
        color: #000 !important; font-weight: bold !important;
        border-radius: 50px !important; border: none !important;
        height: 45px !important; width: 100% !important; transition: 0.4s !important;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4) !important; }

    /* شريط التنبيهات */
    .notif-banner {
        background: rgba(212, 175, 55, 0.1); border: 1px solid #D4AF37;
        border-radius: 50px; padding: 10px; text-align: center; margin-bottom: 25px;
    }

    /* شريط الجولات */
    .plan-bar { background: #111; padding: 15px; border-radius: 50px; border: 1px solid #D4AF37; margin-bottom: 25px; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .round-box { padding: 5px 20px; border-radius: 50px; font-weight: bold; margin: 5px; }
    .round-done { text-decoration: line-through; color: #444; border: 1px solid #333; }
    .round-active { background: #D4AF37; color: #000; box-shadow: 0 0 15px #D4AF37; }
    
    .main-timer { font-size: 110px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات (Database)
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "current_round": 0, "total_rounds": 0,
        "study_time_orig": 0, "break_time_orig": 0, "study_time": 0, "break_time": 0,
        "last_update": None, "members": [], "countdown": 0, "admin_msg": "", 
        "trigger_sound": None, "trigger_voice": None
    }

db = get_db()

if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- واجهات التطبيق -----------------

# صفحة الدخول
if st.session_state.page == "login":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🎓 our goal study</h1>", unsafe_allow_html=True)
    st.write("##")
    u_name = st.text_input("ادخل اسمك المستعار")
    u_goal = st.text_input("ما هو هدفك اليوم؟")
    st.write("##")
    if st.button("🚀 انضمام"):
        if u_name and u_goal:
            st.session_state.user_name, st.session_state.user_goal = u_name, u_goal
            st.session_state.page = "waiting"; st.rerun()

# صفحة الانتظار
elif st.session_state.page == "waiting":
    st.markdown("<h2 style='text-align:center;'>⏳ بانتظار المدير لبدء الجولات</h2>", unsafe_allow_html=True)
    code_in = st.text_input("كود الروم الذهبي")
    if st.button("🚪 دخول"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"; st.rerun()

# صفحة الروم الأساسية
elif st.session_state.page == "room":
    if db["trigger_sound"]: play_audio(db["trigger_sound"]); db["trigger_sound"] = None
    if db["trigger_voice"]: play_voice_cd(db["trigger_voice"]); db["trigger_voice"] = None

    if db["admin_msg"]:
        st.markdown(f"<div class='notif-banner'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # شريط الجولات العلوي
    if db["total_rounds"] > 0:
        plan_html = "<div class='plan-bar'>"
        for r in range(1, db["total_rounds"] + 1):
            status_class = "round-done" if r < db["current_round"] else ("round-active" if r == db["current_round"] else "")
            plan_html += f"<div class='round-box {status_class}'>جولة {r}</div>"
        plan_html += "</div>"
        st.markdown(plan_html, unsafe_allow_html=True)

    # منطق التايمر والعد التنازلي
    if db["status"] == "counting":
        db["trigger_voice"] = str(db["countdown"])
        st.markdown(f"<div style='font-size:150px; text-align:center; color:#ff4b4b; font-weight:bold;'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: db["status"] = "running"; db["last_update"] = time.time()
        st.rerun()

    elif db["status"] == "running":
        now = time.time()
        db["study_time"] -= (now - db["last_update"]); db["last_update"] = now
        st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>📖 جولة {db['current_round']} - وقت التركيز</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer'>{format_time(db['study_time'])}</div>", unsafe_allow_html=True)
        if db["study_time"] <= 0:
            db["status"] = "on_break"; db["last_update"] = time.time(); db["trigger_sound"] = SOUNDS["finish_study"]
        time.sleep(1); st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_time"] -= (now - db["last_update"]); db["last_update"] = now
        if 0 < db["break_time"] <= 10: db["trigger_sound"] = SOUNDS["warning_break"]
        st.markdown(f"<h2 style='text-align:center;'>☕ استراحة الجولة {db['current_round']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_time'])}</div>", unsafe_allow_html=True)
        if db["break_time"] <= 0:
            if db["current_round"] < db["total_rounds"]:
                db["current_round"] += 1; db["status"] = "counting"; db["countdown"] = 10
                db["study_time"] = db["study_time_orig"]; db["break_time"] = db["break_time_orig"]
            else: db["status"] = "finished"; st.balloons()
        time.sleep(1); st.rerun()

    # عرض الطلاب
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            st.markdown(f"<div style='text-align:center; border:1px solid #D4AF37; padding:15px; border-radius:50px;'>👤<br><b>{m['name']}</b></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة -----------------
with st.expander("🛡️ لوحة التحكم الإدارية"):
    if st.text_input("كلمة السر", type="password") == "our122122":
        if not db["room_id"]:
            c1, c2, c3 = st.columns(3)
            rounds = c1.number_input("عدد الجولات", 1, 10, 3)
            s_m = c2.number_input("مذاكرة (دقيقة)", 1, 120, 25)
            b_m = c3.number_input("راحة (دقيقة)", 1, 30, 5)
            if st.button("🚀 إنشاء الغرفة الآن"):
                db.update({"room_id": str(random.randint(1000, 9999)), "total_rounds": rounds, "current_round": 1, 
                           "study_time": s_m*60, "break_time": b_m*60, "study_time_orig": s_m*60, "break_time_orig": b_m*60})
                st.rerun()
        else:
            st.success(f"كود الغرفة: {db['room_id']}")
            if st.button("▶️ ابدأ الجولة الأولى"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            msg = st.text_area("رسالة تنبيه فورية")
            if st.button("📢 إرسال"): db["admin_msg"] = msg; db["trigger_sound"] = SOUNDS["notif"]; st.rerun()
            if st.button("🛑 إنهاء الغرفة"): db.update({"room_id": None, "status": "off", "members": []}); st.rerun()

# تحديث الصفحة التلقائي
if db["room_id"] and st.session_state.page == "room":
    time.sleep(2); st.rerun()
