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
        padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37;
    }
    .study-subject { color: #fff; font-size: 14px; background: #222; padding: 2px 8px; border-radius: 10px; margin-top: 5px; display: inline-block; }
    
    .schedule-card { background: #1a1a1a; border: 1px dashed #D4AF37; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "remaining_seconds": 0, "last_update": None,
        "members": [],
        "schedule": [] # قائمة لتخزين جدول الرومات
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- الواجهة الرئيسية -----------------
st.image("logo.png", width=80)
tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة الإدارة"])

# --- تبويب الطلاب ---
with tabs[0]:
    # عرض جدول الرومات المخطط لها
    if db["schedule"]:
        with st.expander("📅 جدول رومات اليوم (اضغط للتفاصيل)"):
            for item in db["schedule"]:
                st.markdown(f"<div class='schedule-card'>⏰ الوقت: {item['time']} | ⏳ المدة: {item['duration']} دقيقة</div>", unsafe_allow_html=True)

    if not st.session_state.get('joined', False):
        st.subheader("تسجيل الدخول للجلسة")
        c_code = st.text_input("كود الروم")
        c_name = st.text_input("اسمك")
        c_subject = st.text_input("هتذاكر إيه النهاردة؟ (مثال: رياضيات، فيزياء)")
        
        if st.button("انضمام الآن"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({"name": c_name, "subject": c_subject})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("تأكد من الكود وكمال البيانات")
    else:
        # عرض التايمر أو الحالة
        if db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        elif db["status"] == "break":
            st.markdown("<h2 style='text-align:center;'>☕ وقت راحة..</h2>", unsafe_allow_html=True)
        
        # عرض الزملاء بالمربعات مع مادة المذاكرة
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        cols = st.columns(5)
        for i, m in enumerate(db["members"]):
            with cols[i % 5]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span style='font-size:40px;'>👤</span><br>
                        <span style='color:#D4AF37; font-weight:bold;'>{m['name']}</span><br>
                        <span class='study-subject'>📖 {m['subject']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة السر للإدارة", type="password")
    if admin_pass == "our122122":
        
        # قسم جدول المواعيد
        st.subheader("📅 تنظيم جدول الرومات")
        col_t, col_d = st.columns(2)
        with col_t: r_time = st.text_input("موعد الروم (مثلاً: 02:00 م)")
        with col_d: r_dur = st.number_input("المدة بالدقائق", 5, 120, 60)
        
        if st.button("➕ إضافة للجدول ونشر"):
            db["schedule"].append({"time": r_time, "duration": r_dur})
            st.success("تمت إضافة الموعد للجدول!")
            
        if st.button("🗑️ مسح الجدول"):
            db["schedule"] = []
            st.rerun()

        st.write("---")
        
        # قسم التحكم بالروم الحالية
        if not db["room_id"]:
            if st.button("🚀 فتح روم جديدة الآن"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = 60 * 60 # افتراضي ساعة
                db["status"] = "waiting"
                st.rerun()
        else:
            st.success(f"الروم مفتوحة بكود: {db['room_id']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("▶️ بدء"):
                    db["status"] = "running"
                    db["last_update"] = time.time()
            with c2:
                if st.button("⏸️ راحة"): db["status"] = "break"
            with c3:
                if st.button("🛑 إنهاء"):
                    db["room_id"] = None
                    db["members"] = []
                    st.rerun()

# تحديث تلقائي
if db["room_id"]:
    time.sleep(3)
    st.rerun()
