import streamlit as st
import time

# 1. إعدادات التصميم والأصوات
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# روابط الأصوات (مباشرة وتعمل تلقائياً)
NOTIF_SOUND = "https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"
START_SOUND = "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"
FINISH_SOUND = "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"

def play_audio(url):
    st.markdown(f'<iframe src="{url}" allow="autoplay" style="display:none"></iframe>', unsafe_allow_html=True)

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* حقول بيضاء تماماً */
    input, textarea { color: #fff !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: #D4AF37 !important; font-weight: bold; }
    
    /* جدول بلون ذهبي فاتح (مريح للعين) */
    .schedule-info { background: #fff9e6; color: #444; padding: 12px; border-radius: 10px; border-right: 6px solid #D4AF37; margin-bottom: 8px; font-weight: bold; font-size: 1.1rem; }
    
    .main-timer { font-size: 115px; text-align: center; font-weight: bold; color: #D4AF37; margin: 15px 0; }
    .countdown-big { font-size: 140px; text-align: center; color: #ff4b4b; font-weight: bold; }
    
    .member-card { background: #111; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; text-align: center; position: relative; }
    .hand-label { background: #ff4b4b; color: white; border-radius: 5px; font-size: 12px; padding: 2px 5px; position: absolute; top: 10px; left: 10px; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "study_seconds": 0, "break_seconds": 0,
        "last_update": None, "members": [], "schedule": [], 
        "countdown": 0, "admin_msg": "", "raised_hands": [], "trigger_sound": None
    }

db = get_db()

if 'page' not in st.session_state: st.session_state.page = "login"

def format_time(seconds):
    mins, secs = divmod(int(max(0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- واجهة المستخدم -----------------

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
    st.header("⏳ قائمة الانتظار والجدول")
    if db["schedule"]:
        for item in db["schedule"]:
            st.markdown(f"<div class='schedule-info'>📅 الموعد: {item['time']} | ⏳ المدة: {item['duration']} دقيقة</div>", unsafe_allow_html=True)
    
    st.write("---")
    code_in = st.text_input("أدخل كود الروم")
    if st.button("🚪 انضمام"):
        if db["room_id"] and code_in == db["room_id"]:
            if not any(m['name'] == st.session_state.user_name for m in db["members"]):
                db["members"].append({"name": st.session_state.user_name, "goal": st.session_state.user_goal})
            st.session_state.page = "room"
            st.rerun()

elif st.session_state.page == "room":
    # تشغيل الجرس الصوتي بناءً على الحالة
    if db["trigger_sound"]:
        play_audio(db["trigger_sound"])
        db["trigger_sound"] = None

    if db["admin_msg"]:
        st.markdown(f"<div style='background:#D4AF37; color:black; padding:20px; border-radius:10px; text-align:center; font-size:32px; font-weight:bold;'>📢 {db['admin_msg']}</div>", unsafe_allow_html=True)

    # زر رفع اليد
    c_h1, c_h2 = st.columns([5, 1])
    with c_h2:
        if st.button("✋ رفع اليد"):
            if st.session_state.user_name not in db["raised_hands"]:
                db["raised_hands"].append(st.session_state.user_name)
                st.toast("تم رفع يدك!")

    # منطق التايمر والأصوات
    if db["status"] == "ready":
        st.markdown("<div class='countdown-big'>🔔 استعدوووووو</div>", unsafe_allow_html=True)
    
    elif db["status"] == "counting":
        if db["countdown"] == 10: db["trigger_sound"] = START_SOUND # جرس بدء العد
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
        else:
            time.sleep(1); st.rerun()

    elif db["status"] == "pre_break": # عد تنازلي للراحة
        if db["countdown"] == 10: db["trigger_sound"] = NOTIF_SOUND
        st.markdown(f"<div class='main-timer'>{format_time(db['study_seconds'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big' style='font-size:55px;'>☕ الراحة تبدأ بعد: {db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: 
            db["status"] = "on_break"; db["last_update"] = time.time(); db["trigger_sound"] = START_SOUND
        st.rerun()

    elif db["status"] == "on_break":
        now = time.time()
        db["break_seconds"] -= (now - db["last_update"])
        db["last_update"] = now
        st.markdown("<h1 style='text-align:center;'>☕ وقت استراحة</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-timer' style='color:#fff;'>{format_time(db['break_seconds'])}</div>", unsafe_allow_html=True)
        if db["break_seconds"] <= 0: 
            db["status"] = "pre_resume"; db["countdown"] = 10; db["trigger_sound"] = FINISH_SOUND
        time.sleep(1); st.rerun()

    elif db["status"] == "pre_resume": # عد تنازلي للعودة
        st.markdown("<h1 style='text-align:center;'>⚠️ العودة للمذاكرة في:</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='countdown-big'>{db['countdown']}</div>", unsafe_allow_html=True)
        time.sleep(1); db["countdown"] -= 1
        if db["countdown"] < 0: 
            db["status"] = "running"; db["last_update"] = time.time(); db["trigger_sound"] = START_SOUND
        st.rerun()

    # عرض مربعات الطلاب
    st.write("---")
    cols = st.columns(6)
    for i, m in enumerate(db["members"]):
        with cols[i % 6]:
            hand = "<div class='hand-label'>✋ مرفوعة</div>" if m['name'] in db['raised_hands'] else ""
            st.markdown(f"<div class='member-card'>{hand}👤<br><b>{m['name']}</b><br><small>{m['goal']}</small></div>", unsafe_allow_html=True)

# ----------------- الإدارة -----------------
with st.expander("🛡️ لوحة الإدارة"):
    if st.text_input("كلمة السر", type="password") == "our122122":
        if db["room_id"]:
            st.success(f"كود الروم: {db['room_id']}")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🔔 استعدوا"): 
                    db["status"] = "ready"; db["trigger_sound"] = NOTIF_SOUND; st.rerun()
            with c2:
                if st.button("▶️ ابدأ (10ث)"): 
                    db["status"] = "counting"; db["countdown"] = 10; st.rerun()
            with c3:
                if st.button("⏸️ طلب راحة"): 
                    db["status"] = "pre_break"; db["countdown"] = 10; st.rerun()
            with c4:
                if st.button("🛑 إنهاء"): 
                    db.update({"room_id": None, "members": [], "status": "off", "raised_hands": []}); st.rerun()
            
            if st.button("✅ مسح أيدي الطلاب"): db["raised_hands"] = []; st.rerun()
            
            msg = st.text_area("أرسل رسالة مع جرس")
            if st.button("📢 إرسال الآن"): 
                db["admin_msg"] = msg; db["trigger_sound"] = NOTIF_SOUND; st.rerun()
        else:
            sm = st.number_input("دقائق المذاكرة", 5, 120, 45)
            bm = st.number_input("دقائق الراحة", 1, 30, 5)
            if st.button("🚀 إنشاء غرفة"):
                import random
                db.update({"room_id": str(random.randint(1000, 9999)), "study_seconds": sm*60, "break_seconds": bm*60, "status": "waiting"})
                st.rerun()
        
        st.write("---")
        if st.button("🗑️ مسح الجدول"): db["schedule"] = []; st.rerun()
        tc1, tc2 = st.columns(2)
        if st.button("➕ إضافة موعد"): 
            db["schedule"].append({"time": tc1.text_input("الموعد", value="09:00 م"), "duration": tc2.number_input("المدة", 5, 120, 45)})
            st.rerun()

if db["room_id"] and st.session_state.page != "login" and db["status"] != "off":
    time.sleep(2); st.rerun()
