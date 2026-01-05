import streamlit as st
import time

# 1. إعدادات التصميم والخطوط الواضحة
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    
    /* تصميم مربعات الأعضاء */
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 15px; text-align: center; transition: 0.3s;
    }
    .member-card:hover { border-color: #D4AF37; }
    
    /* التايمر */
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; margin: 10px 0; }
    .status-text { font-size: 50px; text-align: center; color: #fff; font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة (Database)
@st.cache_resource
def get_db():
    return {
        "room_id": None, 
        "status": "off", # off, waiting, ready, running, break
        "remaining_seconds": 0,
        "last_update": None,
        "members": []
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- الواجهة الرئيسية -----------------
st.image("logo.png", width=100)
st.title("Our Goal Study 🎓")

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة التحكم"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not st.session_state.get('joined', False):
        st.subheader("انضم للجلسة")
        c_code = st.text_input("كود الروم المكون من 6 أرقام")
        c_name = st.text_input("اسمك")
        if st.button("تأكيد الانضمام"):
            if db["room_id"] and c_code == db["room_id"] and c_name:
                if c_name not in [m['name'] for m in db["members"]]:
                    db["members"].append({"name": c_name})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("تأكد من الكود أو أن المسؤول فتح الروم")
    else:
        # عرض الحالة (استعداد، راحة، أو تايمر)
        if db["status"] == "ready":
            st.markdown("<div class='status-text'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        elif db["status"] == "break":
            st.markdown("<div class='status-text' style='color:#fff'>☕ وقت راحة..</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timer-display' style='color:#555'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
        elif db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            if db["remaining_seconds"] > 0:
                st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                db["status"] = "off"
                st.success("انتهت الجلسة!")
        
        # عرض الزملاء بمربعات
        st.write("---")
        st.subheader(f"الزملاء الحاضرون ({len(db['members'])})")
        cols = st.columns(6)
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'>👤<br>{m['name']}</div>", unsafe_allow_html=True)

# --- تبويب المسؤول ---
with tabs[1]:
    # تأكد من إدخال الباسورد أولاً
    admin_pass = st.text_input("أدخل كلمة سر المسؤول للإظهار", type="password")
    
    if admin_pass == "our122122":
        if not db["room_id"]:
            st.subheader("خطوة 1: إعداد الروم")
            mins = st.number_input("مدة المذاكرة (دقيقة)", 5, 120, 45)
            if st.button("🚀 إنشاء الروم وتوليد الكود"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = mins * 60
                db["status"] = "waiting"
                st.rerun()
        else:
            st.success(f"الروم نشطة بالكود: {db['room_id']}")
            
            # أزرار التحكم
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🔔 تنبيه استعدوا"): db["status"] = "ready"
            with c2:
                if st.button("▶️ بدء/استكمال"):
                    db["status"] = "running"
                    db["last_update"] = time.time()
            with c3:
                if st.button("⏸️ راحة (إيقاف)"): db["status"] = "break"
            with c4:
                if st.button("🛑 إنهاء الكل"):
                    db["room_id"] = None
                    db["status"] = "off"
                    db["members"] = []
                    st.rerun()
    else:
        st.warning("يرجى إدخال الباسورد الصحيح لتظهر لك أزرار التحكم.")

# تحديث تلقائي للطلاب لمتابعة التغييرات
if db["room_id"]:
    time.sleep(3)
    st.rerun()
