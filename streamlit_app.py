import streamlit as st
import time

# 1. إعدادات التصميم والواجهة
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #000; color: #D4AF37; font-family: 'Cairo', sans-serif; }
    
    /* تصميم مربعات الأعضاء */
    .member-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; padding: 10px; }
    .member-card { 
        background: #111; border: 1px solid #333; border-radius: 15px; 
        padding: 15px; text-align: center; transition: 0.3s;
    }
    .member-card:hover { border-color: #D4AF37; background: #1a1a1a; }
    .avatar { font-size: 40px; margin-bottom: 8px; display: block; }
    .member-name { font-weight: bold; color: #fff; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    /* شاشة الاستعداد والتايمر */
    .timer-display { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; margin: 10px 0; }
    .get-ready { font-size: 70px; text-align: center; color: #fff; font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    
    .stButton>button { background: #D4AF37 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. قاعدة البيانات المشتركة
@st.cache_resource
def get_db():
    return {
        "room_id": None, 
        "status": "off", 
        "end_timestamp": None,
        "duration_mins": 45,
        "members": [] # قائمة القواميس تحتوي على الاسم
    }

db = get_db()

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

# ----------------- 🏠 المنطق البرمجي -----------------
st.image("logo.png", width=80)

# حالة المستخدم (هل هو مسجل دخول أم لا)
if 'joined' not in st.session_state:
    st.session_state.joined = False

tabs = st.tabs(["👤 ساحة المذاكرة", "🛡️ لوحة التحكم"])

# --- تبويب الطلاب ---
with tabs[0]:
    # إذا لم ينضم الطالب بعد، تظهر له واجهة الدخول
    if not st.session_state.joined:
        st.subheader("🎓 انضم لزملائك الآن")
        c_code = st.text_input("أدخل كود الروم (6 أرقام)")
        c_name = st.text_input("اكتب اسمك")
        
        if st.button("تأكيد الانضمام والدخول"):
            if db["room_id"] and c_code == db["room_id"]:
                if c_name:
                    # إضافة العضو للداتا المشتركة
                    if c_name not in [m['name'] for m in db["members"]]:
                        db["members"].append({"name": c_name, "avatar": "👤"})
                    # تحديث حالة الجلسة للمستخدم الحالي
                    st.session_state.joined = True
                    st.session_state.user_name = c_name
                    st.rerun() # تحديث الصفحة فوراً لإخفاء الواجهة
                else: st.error("يرجى كتابة اسمك")
            else: st.error("كود الروم غير صحيح أو لا توجد روم مفتوحة")
    
    # إذا انضم الطالب بنجاح، تظهر له الروم
    else:
        # 1. عرض الحالة (استعداد أو تايمر)
        if db["status"] == "ready":
            st.markdown("<div class='get-ready'>⚠️ استعدووووو...</div>", unsafe_allow_html=True)
        elif db["status"] == "running":
            remaining = db["end_timestamp"] - time.time()
            if remaining > 0:
                st.markdown(f"<div class='timer-display'>{format_time(remaining)}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='timer-display'>00:00</div>", unsafe_allow_html=True)
                st.success("🎉 انتهت الجلسة! خذ قسطاً من الراحة.")
        else:
            st.info(f"مرحباً {st.session_state.user_name}، أنت في قاعة الانتظار الآن.")

        # 2. عرض مربعات الزملاء المتواجدين
        st.write("---")
        st.subheader(f"👥 الزملاء الحاضرون ({len(db['members'])})")
        
        # عرض المربعات في أعمدة
        cols = st.columns(6) 
        for i, member in enumerate(db["members"]):
            with cols[i % 6]:
                st.markdown(f"""
                    <div class='member-card'>
                        <span class='avatar'>👤</span>
                        <div class='member-name'>{member['name']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        if st.button("⬅️ تسجيل الخروج"):
            # إزالة الاسم من القائمة عند الخروج
            db["members"] = [m for m in db["members"] if m['name'] != st.session_state.user_name]
            st.session_state.joined = False
            st.rerun()

# --- تبويب الإدارة ---
with tabs[1]:
    pw = st.text_input("كلمة سر المسؤول", type="password")
    if pw == "our122122":
        if not db["room_id"]:
            db["duration_mins"] = st.number_input("مدة الجلسة (دقائق)", 5, 120, 45)
            if st.button("🚀 إنشاء وتوليد كود"):
                import random
                db["room_id"] = str(random.randint(100000, 999999))
                db["status"] = "waiting"
                st.rerun()
        else:
            st.success(f"الروم مفتوحة | الكود هو: {db['room_id']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔔 إرسال تنبيه (استعدوا)"):
                    db["status"] = "ready"
                    st.rerun()
            with col2:
                if st.button("🔥 بدء التايمر الآن"):
                    db["status"] = "running"
                    db["end_timestamp"] = time.time() + (db["duration_mins"] * 60)
                    st.rerun()
            with col3:
                if st.button("🛑 إنهاء الروم للكل"):
                    db["room_id"] = None
                    db["status"] = "off"
                    db["members"] = []
                    st.rerun()

# تحديث تلقائي كل ثانيتين لمتابعة حالة التايمر والزملاء الجدد
if db["room_id"]:
    time.sleep(2)
    st.rerun()
