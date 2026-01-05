import streamlit as st
import time

# 1. إعدادات التصميم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    .member-card { background: #111; border: 1px solid #333; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 4px solid #D4AF37; }
    .study-subject { color: #fff; font-size: 14px; background: #222; padding: 2px 8px; border-radius: 10px; margin-top: 5px; display: inline-block; }
    .admin-table { width: 100%; border-collapse: collapse; margin-top: 10px; color: #fff; }
    .admin-table th, .admin-table td { border: 1px solid #D4AF37; padding: 8px; text-align: right; }
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
        "schedule": []
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
        with st.expander("📅 جدول رومات اليوم"):
            for item in db["schedule"]:
                st.write(f"⏰ {item['time']} | ⏳ {item['duration']} دقيقة")

    if not st.session_state.get('joined', False):
        st.subheader("تسجيل الدخول للجلسة")
        c_code = st.text_input("كود الروم")
        c_name = st.text_input("اسمك")
        c_subject = st.text_input("هتذاكر إيه النهاردة؟")
        if st.button("انضمام الآن"):
            if db["room_id"] and c_code == db["room_id"] and c_name and c_subject:
                db["members"].append({"name": c_name, "subject": c_subject, "join_time": time.strftime("%H:%M:%S")})
                st.session_state.joined = True
                st.session_state.user_name = c_name
                st.rerun()
            else: st.error("بيانات ناقصة أو الكود خطأ")
    else:
        if db["status"] == "running":
            elapsed = time.time() - db["last_update"]
            db["remaining_seconds"] -= elapsed
            db["last_update"] = time.time()
            st.markdown(f"<div class='timer-display'>{format_time(db['remaining_seconds'])}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        cols = st.columns(5)
        for i, m in enumerate(db["members"]):
            with cols[i % 5]:
                st.markdown(f"<div class='member-card'>👤<br><b>{m['name']}</b><br><span class='study-subject'>📖 {m['subject']}</span></div>", unsafe_allow_html=True)

# --- تبويب الإدارة ---
with tabs[1]:
    admin_pass = st.text_input("كلمة السر للإدارة", type="password")
    if admin_pass == "our122122":
        # 1. مراقبة المستخدمين (الجديد)
        st.subheader("👥 مراقبة الحاضرين في الروم الحالية")
        if db["members"]:
            # إنشاء جدول لعرض البيانات للأدمن
            html_table = "<table class='admin-table'><tr><th>الاسم</th><th>المادة</th><th>وقت الدخول</th></tr>"
            for m in db["members"]:
                html_table += f"<tr><td>{m['name']}</td><td>{m['subject']}</td><td>{m['join_time']}</td></tr>"
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.write("لا يوجد مستخدمين داخل الروم حالياً.")
        
        st.write("---")
        
        # 2. تنظيم الجدول
        st.subheader("📅 تنظيم المواعيد")
        col_t, col_d = st.columns(2)
        with col_t: r_time = st.text_input("الموعد (مثلاً: 05:00 م)")
        with col_d: r_dur = st.number_input("المدة (دقيقة)", 5, 120, 60)
        if st.button("➕ إضافة للجدول"):
            db["schedule"].append({"time": r_time, "duration": r_dur})
            st.success("تم التحديث")

        st.write("---")
        
        # 3. التحكم بالروم
        if not db["room_id"]:
            if st.button("🚀 فتح روم جديدة"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["remaining_seconds"] = 3600 # ساعة
                db["status"] = "waiting"
                st.rerun()
        else:
            st.info(f"كود الروم الحالي: {db['room_id']}")
            c1, c2, c3 = st.columns(3)
            with c1: 
                if st.button("▶️ بدء"): 
                    db["status"] = "running"
                    db["last_update"] = time.time()
            with c2: 
                if st.button("⏸️ راحة"): db["status"] = "break"
            with c3: 
                if st.button("🛑 إنهاء وطرد الكل"):
                    db["room_id"] = None
                    db["members"] = []
                    st.rerun()
