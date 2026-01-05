import streamlit as st
import time

# 1. إعدادات التصميم (إصلاح ألوان الخطوط لتكون بيضاء)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* تغيير لون الخلفية العام */
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #fff; font-family: 'Cairo', sans-serif; }
    
    /* جعل الخط أبيض في خانات الإدخال والعناوين */
    input { color: white !important; background-color: #1a1a1a !important; border: 1px solid #D4AF37 !important; }
    label { color: white !important; font-size: 18px !important; font-weight: bold !important; }
    .stMarkdown p, h1, h2, h3 { color: white !important; }
    
    /* تصميم مربعات الأعضاء */
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37;
    }
    .study-subject { color: #fff; font-size: 14px; background: #D4AF37; color: #000; padding: 2px 8px; border-radius: 10px; margin-top: 5px; display: inline-block; font-weight: bold; }
    
    /* التايمر والجدول */
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; }
    .admin-table { width: 100%; border-collapse: collapse; color: white; }
    .admin-table th, .admin-table td { border: 1px solid #D4AF37; padding: 10px; text-align: center; }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, "status": "off", "remaining_seconds": 0, "last_update": None,
        "members": [], "schedule": []
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
    if db["schedule"]:
        with st.expander("📅 جدول رومات اليوم (اضغط للرؤية)"):
            for item in db["schedule"]:
                st.write(f"⏰ الموعد: {item['time']} | ⏳ المدة: {item['duration']} دقيقة")

    if not st.session_state.get('joined', False):
        st.subheader("سجل دخولك وابدأ المذاكرة")
        c_code = st.text_input("كود الروم المكون من 6 أرقام")
        c_name = st.text_input("اسمك")
        c_subject = st.text_input("هتذاكر إيه النهاردة؟")
        
        if st.button("انضمام الآن"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({
                    "name": c_name, 
                    "subject": c_subject, 
                    "join_time": time.strftime("%H:%M")
                })
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("تأكد من الكود وكمال بياناتك")
    else:
        # عرض التايمر
        if db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        elif db["status"] == "break":
            st.markdown("<h2 style='text-align:center;'>☕ وقت راحة..</h2>", unsafe_allow_html=True)
        
        # عرض الزملاء
        st.write("---")
        st.subheader(f"👥 الحاضرون الآن ({len(db['members'])})")
        cols = st.columns(5)
        for i, m in enumerate(db["members"]):
            with cols[i % 5]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span style='font-size:40px;'>👤</span><br>
                        <b style='color:#fff;'>{m['name']}</b><br>
                        <span class='study-subject'>📖 {m['subject']}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة سر المسؤول", type="password")
    if admin_pass == "our122122":
        # مراقبة المستخدمين بجدول أبيض واضح
        st.subheader("👥 سجل الحضور المباشر")
        if db["members"]:
            st.table(db["members"])
        
        st.write("---")
        # تنظيم الجدول الدراسي
        st.subheader("📅 إضافة موعد للجدول")
        col_t, col_d = st.columns(2)
        with col_t: r_time = st.text_input("وقت الروم (مثلاً 09:00 م)")
        with col_d: r_dur = st.number_input("المدة (بالدقائق)", 5, 120, 60)
        if st.button("نشر الموعد"):
            db["schedule"].append({"time": r_time, "duration": r_dur})
            st.success("تم النشر!")

        st.write("---")
        # التحكم بالروم
        if not db["room_id"]:
            if st.button("🚀 فتح روم جديدة الآن"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = 3600 
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"كود الروم الحالي: {db['room_id']}")
            c1, c2, c3 = st.columns(3)
            with c1: 
                if st.button("▶️ ابدأ"): 
                    db["status"] = "running"
                    db["last_update"] = time.time()
            with c2: 
                if st.button("⏸️ راحة"): db["status"] = "break"
            with c3: 
                if st.button("🛑 إنهاء الجلسة"):
                    db["room_id"] = None
                    db["members"] = []
                    st.rerun()
