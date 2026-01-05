import streamlit as st
import time

# 1. إعدادات التصميم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 15px; text-align: center;
    }
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; margin: 10px 0; }
    .break-text { font-size: 60px; text-align: center; color: #fff; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
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

# ----------------- 🏠 المنطق البرمجي -----------------
st.image("logo.png", width=80)

if 'joined' not in st.session_state: st.session_state.joined = False

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة التحكم"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not st.session_state.joined:
        st.subheader("🎓 انضم لزملائك")
        c_code = st.text_input("كود الروم")
        c_name = st.text_input("اسمك")
        if st.button("انضمام"):
            if db["room_id"] and c_code == db["room_id"] and c_name:
                if c_name not in [m['name'] for m in db["members"]]:
                    db["members"].append({"name": c_name})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
    else:
        # عرض الحالة بناءً على وضع الروم
        if db["status"] == "break":
            st.markdown("<div class='break-text'>☕ وقت راحة.. استمتع بفاصل قصير</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='timer-display' style='color:#777'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
        elif db["status"] == "running":
            # تحديث الوقت المتبقي
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            
            if db["remaining_seconds"] > 0:
                st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                db["status"] = "off"
                st.balloons()
        elif db["status"] == "ready":
            st.markdown("<div class='break-text' style='color:#D4AF37'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        else:
            st.info("🕒 بانتظار إشارة البدء...")

        # عرض الزملاء
        st.write("---")
        cols = st.columns(6) 
        for i, m in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"<div class='member-card'>👤<br>{m['name']}</div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
