import streamlit as st
import time

# 1. تصميم الواجهة الاحترافية (مربعات الأعضاء وتأثيرات الاستعداد)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    
    /* تصميم مربعات الأعضاء */
    .member-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; padding: 20px; }
    .member-card { 
        background: #111; border: 2px solid #333; border-radius: 20px; 
        padding: 20px; text-align: center; transition: 0.3s;
    }
    .member-card:hover { border-color: #D4AF37; transform: translateY(-5px); }
    .avatar { font-size: 50px; margin-bottom: 10px; display: block; }
    .member-name { font-weight: bold; color: #fff; font-size: 18px; }

    /* التايمر وشاشة الاستعداد */
    .timer-display { font-size: 120px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 30px #D4AF37; }
    .get-ready { 
        font-size: 80px; text-align: center; color: #fff; 
        animation: flash 1s infinite; font-weight: bold; 
    }
    @keyframes flash { 0% {opacity: 1;} 50% {opacity: 0.4;} 100% {opacity: 1;} }
    
    .stButton>button { background: #D4AF37; color: #000; font-weight: bold; border-radius: 12px; height: 50px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, 
        "status": "off", # off, waiting, ready, running
        "end_timestamp": None,
        "duration_mins": 45,
        "members": []
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- 🏠 واجهة التطبيق -----------------
st.image("logo.png", width=100)
tabs = st.tabs(["👤 ساحة الزملاء", "🛡️ الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    if not db["room_id"]:
        st.info("بانتظار إنشاء روم جديدة من قبل المسؤول...")
        c_code = st.text_input("أدخل كود الروم")
        c_name = st.text_input("اسمك")
        if st.button("انضمام للروم"):
            if c_code == db["room_id"] and db["room_id"]:
                st.session_state.user = c_name
                if c_name not in [m['name'] for m in db["members"]]:
                    db["members"].append({"name": c_name, "avatar": "👤"})
                st.rerun()
    else:
        # حالة الاستعداد
        if db["status"] == "ready":
            st.markdown("<div class='get-ready'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        
        # حالة العمل (التايمر)
        elif db["status"] == "running":
            remaining = db["end_timestamp"] - time.time()
            if remaining > 0:
                st.markdown(f"<div class='timer-display'>{format_time(remaining)}</div>", unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                st.markdown("<div class='timer-display'>00:00</div>", unsafe_allow_html=True)
                st.balloons()
                st.success("انتهت الجلسة!")
        
        # حالة الانتظار (عرض المربعات)
        else:
            st.info("🕒 أنت في الانتظار.. سيظهر التايمر فور البدء.")
        
        # عرض الأعضاء على شكل مربعات
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        
        # إنشاء شبكة المربعات
        cols = st.columns(5) 
        for i, member in enumerate(db["members"]):
            with cols[i % 5]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span class='avatar'>{member['avatar']}</span>
                        <span class='member-name'>{member['name']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    pw = st.text_input("كلمة السر", type="password")
    if pw == "our122122":
        if not db["room_id"]:
            db["duration_mins"] = st.number_input("مدة الجلسة (دقائق)", 1, 120, 45)
            if st.button("🚀 إنشاء الروم"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["status"] = "waiting"
                st.rerun()
        else:
            st.success(f"الكود الحالي: {db['room_id']}")
            
            if st.button("🔔 ابدأ (مرحلة الاستعداد)"):
                db["status"] = "ready"
                st.rerun()
            
            if st.button("🔥 تشغيل التايمر فعلياً"):
                db["status"] = "running"
                db["end_timestamp"] = time.time() + (db["duration_mins"] * 60)
                st.rerun()
            
            if st.button("🛑 إغلاق الروم"):
                db["room_id"] = None
                db["status"] = "off"
                db["members"] = []
                st.rerun()

# تحديث تلقائي لمتابعة الحالة
if db["room_id"]:
    time.sleep(3)
    st.rerun()
