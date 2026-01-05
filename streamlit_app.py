import streamlit as st
import time
import random

# 1. إعدادات الصفحة والتصميم الفائق
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

# CSS المتطور والشامل (يصلح كل مشاكل الرؤية والمربعات)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #ffffff !important; font-family: 'Cairo', sans-serif; }
    h1, h2, h3, p, span, label, div { color: #ffffff !important; }
    
    /* شريط الجولات البيضاوي */
    .rounds-bar {
        display: flex; justify-content: space-around; background: #111; 
        padding: 15px; border-radius: 50px; border: 1px solid #D4AF37; margin-bottom: 20px;
    }
    .round-step { padding: 5px 20px; border-radius: 50px; font-weight: bold; border: 1px solid #333; }
    .round-active { background: #D4AF37; color: #000 !important; box-shadow: 0 0 15px #D4AF37; }
    .round-done { text-decoration: line-through; color: #555 !important; opacity: 0.6; }
    
    /* الحقول البيضاوية */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #111 !important; color: #ffffff !important;
        border: 2px solid #D4AF37 !important; border-radius: 50px !important;
        padding: 10px 25px !important;
    }
    
    /* كروت الأشخاص ورفع اليد */
    .member-card { 
        background: #1a1a1a; border: 2px solid #D4AF37; 
        border-radius: 25px; padding: 20px; text-align: center; 
        margin: 10px; position: relative;
    }
    .hand-label { 
        background: #ff4b4b; color: white !important; border-radius: 10px; 
        padding: 2px 10px; font-size: 12px; position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
    }

    /* كروت الجدول */
    .schedule-card { background: #fff9e6; padding: 15px; border-radius: 20px; margin-bottom: 10px; border-right: 10px solid #D4AF37; }
    .schedule-card b, .schedule-card span { color: #000 !important; }

    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #F2D472) !important;
        color: #000 !important; font-weight: bold !important; border-radius: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
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
    if st.button("🚀 تسجيل الدخول"):
        if u_name and u_goal:
            st.session_state.user_name, st.session_state.user_goal = u_name, u_goal
            st.session_state.page = "waiting"; st.rerun()

elif st.session_state.page == "waiting":
    st.markdown("<h2 style='text-align:center;'>📅 جدول مواعيد الجلسات</h2>", unsafe_allow_html=True)
    if db["schedule"]:
        for item in db["schedule"]:
            st.markdown(f"<div class='schedule-card'><b>⏰ الوقت: {item['time']}</b> | 🔄 جولات: {item['rounds']} | ⏳ مدة: {item['duration']}د</div>", unsafe_allow_html=True)
    else: st.info("لا يوجد جدول مضاف حالياً.")
    st.write("---")
    code_in = st.text_input("كود الروم الذهبي")
    if st.button("🚪 انضمام للروم"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"; st.rerun()

elif st.session_state.page == "room":
    if db["trigger_sound"]: play_audio(db["trigger_sound"]); db["trigger_sound"] = None
    if db["trigger_voice"]: play_voice_cd(db["trigger_voice"]); db["trigger_voice"] = None

    # شريط الجولات العلوي (موجود الآن)
    if db["total_rounds"] > 0:
        bar_html = "<div class='rounds-bar'>"
        for r in range(1, db["total_rounds"] + 1):
            s_class = "round-active" if r == db["current_round"] else ("round-done" if r < db["current_round"] else "")
            bar_html += f"<div class='round-step {s_class}'>جولة {r}</div>"
        bar_html += "</div>"
        st.markdown(bar_html, unsafe_allow_html=True)

    # التنبيهات الإدارية
    if db["admin_msg"]:
        st.markdown(f"<div style='background:rgba(212,175,55,0.2); border:1px solid #D4AF37; padding:15px; border-radius:50px; text-align:center;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # التايمر
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
        st.markdown("<h2 style='text-align:center;'>☕ استراحة</h2>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align:center; font-size:100px;'>{format_time(db['break_time'])}</h1>", unsafe_allow_html=True)
        if db["break_time"] <= 0:
            if db["current_round"] < db["total_rounds"]:
                db["current_round"] += 1; db["status"] = "counting"; db["countdown"] = 10
                db["study_time"], db["break_time"] = db["study_time_orig"], db["break_time_orig"]
            else: db["status"] = "finished"; st.balloons()
        time.sleep(1); st.rerun()

    # رفع اليد (موجود الآن)
    if st.button("✋ رفع يد"):
        if st.session_state.user_name not in db["raised_hands"]: db["raised_hands"].append(st.session_state.user_name)

    # عرض مربعات الأشخاص (موجود الآن)
    st.write("---")
    st.markdown("### 👥 الزملاء في الروم")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            hand_html = "<div class='hand-label'>✋ مرفوعة</div>" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand_html}<div style='font-size:30px;'>👤</div><b>{m['name']}</b><br><small>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- لوحة الإدارة -----------------
with st.expander("🛠️ لوحة التحكم"):
    if st.text_input("كلمة السر", type="password") == "our122122":
        # قسم الجداول
        st.markdown("### 📅 إنشاء الجدول")
        t_col, r_col, d_col = st.columns(3)
        t_in = t_col.text_input("وقت الجلسة")
        r_in = r_col.number_input("جولات الجدول", 1, 10, 4)
        d_in = d_col.number_input("المدة (د)", 5, 120, 25)
        if st.button("➕ إضافة للجدول"):
            db["schedule"].append({"time": t_in, "rounds": r_in, "duration": d_in}); st.rerun()
        if st.button("🗑️ مسح الجدول"): db["schedule"] = []; st.rerun()
        st.write("---")
        # قسم الروم
        if not db["room_id"]:
            st.markdown("### 🚀 فتح الروم")
            c1, c2, c3 = st.columns(3)
            r_val = c1.number_input("جولات الروم", 1, 10, 3)
            s_val = c2.number_input("مذاكرة (د)", 1, 120, 25)
            b_val = c3.number_input("راحة (د)", 1, 30, 5)
            if st.button("فتح الروم الآن"):
                db.update({"room_id": str(random.randint(1000, 9999)), "total_rounds": r_val, "current_round": 1, 
                           "study_time": s_val*60, "break_time": b_val*60, "study_time_orig": s_val*60, "break_time_orig": b_val*60})
                st.rerun()
        else:
            st.info(f"كود الروم: {db['room_id']}")
            if st.button("▶️ ابدأ الآن"): db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            if st.button("📢 إرسال تنبيه"): db["admin_msg"] = st.text_area("الرسالة"); db["trigger_sound"] = SOUNDS["notif"]; st.rerun()
            if st.button("✅ مسح رفع اليد"): db["raised_hands"] = []; st.rerun()
            if st.button("🛑 إنهاء الروم"): db.update({"room_id": None, "members": [], "status": "off"}); st.rerun()

if db["room_id"] and st.session_state.page == "room":
    time.sleep(2); st.rerun()
