import streamlit as st
import time

# 1. إعدادات الصفحة الأساسية لتطبيق "our goal study"
st.set_page_config(page_title="our goal study", page_icon="📚", layout="wide")

# 2. محاكي قاعدة البيانات لحفظ المستخدمين ونقاطهم
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "أحمد": {"pin": "1234", "points": 0, "status": "نشط"},
        "محمد": {"pin": "2222", "points": 0, "status": "نشط"},
        "سارة": {"pin": "3333", "points": 0, "status": "نشط"}
    }

if 'room_config' not in st.session_state:
    st.session_state.room_config = {"active": False, "duration": 25}

st.title("📚 تطبيق our goal study")

# 3. القائمة الجانبية للاختيار بين مستخدم أو مسؤول
st.sidebar.header("لوحة الدخول")
login_type = st.sidebar.radio("دخول بصفتي:", ["👤 مستخدم عادي", "🔑 مسؤول (Admin)"])

# --- الجزء الأول: مسؤول النظام (Admin) ---
if login_type == "🔑 مسؤول (Admin)":
    st.subheader("🛡️ لوحة تحكم المسؤول")
    admin_email = st.text_input("البريد الإلكتروني")
    admin_pass = st.text_input("كلمة السر", type="password")
    
    if admin_email == "ourgostudy@gmail.com" and admin_pass == "our122122":
        st.success("أهلاً بك يا أدمن! لديك الآن التحكم الكامل.")
        
        # تحكم الروم
        with st.expander("⚙️ إعدادات الروم"):
            new_time = st.slider("حدد وقت الجلسة (دقائق)", 5, 120, st.session_state.room_config["duration"])
            if st.button("فتح الروم للمستخدمين"):
                st.session_state.room_config["active"] = True
                st.session_state.room_config["duration"] = new_time
                st.success("تم فتح الروم!")
            if st.button("إغلاق الروم"):
                st.session_state.room_config["active"] = False
                st.warning("تم إغلاق الروم.")

        # إدارة المستخدمين والطرد
        with st.expander("👥 إدارة الأعضاء ونقاطهم"):
            for user, info in st.session_state.user_db.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"**{user}** ({info['status']})")
                col2.write(f"{info['points']} ⭐")
                if col3.button("طرد", key=user):
                    st.session_state.user_db[user]["status"] = "مطرود"
                    st.rerun()
    elif admin_email:
        st.error("بيانات المسؤول غير صحيحة!")

# --- الجزء الثاني: المستخدم العادي ---
else:
    st.subheader("👤 منطقة المذاكرة")
    user_name = st.selectbox("اختر اسمك", [""] + list(st.session_state.user_db.keys()))
    user_pin = st.text_input("الرمز السري (PIN)", type="password")

    if user_name and user_pin == st.session_state.user_db[user_name]["pin"]:
        if st.session_state.user_db[user_name]["status"] == "مطرود":
            st.error("❌ عذراً، لقد تم طردك من قبل المسؤول.")
        else:
            st.success(f"مرحباً {user_name}!")
            st.info(f"نقاطك الحالية: {st.session_state.user_db[user_name]['points']} ⭐")
            
            if not st.session_state.room_config["active"]:
                st.warning("⏳ الروم مغلق حالياً، انتظر الأدمن لفتحه.")
            else:
                st.success(f"✅ الروم مفتوح لمدة {st.session_state.room_config['duration']} دقيقة.")
                if st.button("🔥 ابدأ المذاكرة الآن"):
                    timer_ph = st.empty()
                    total_sec = st.session_state.room_config["duration"] * 60
                    for i in range(total_sec, -1, -1):
                        m, s = divmod(i, 60)
                        timer_ph.header(f"⏱️ المتبقي: {m:02d}:{s:02d}")
                        time.sleep(1)
                    # إضافة النقاط بعد انتهاء الوقت
                    st.session_state.user_db[user_name]["points"] += 10
                    st.balloons()
                    st.success("عاش! حصلت على 10 نقاط.")
                    time.sleep(2)
                    st.rerun()
    elif user_pin:
        st.error("الرمز السري خطأ!")

# عرض لوحة الشرف للجميع في الجانب
st.sidebar.markdown("---")
st.sidebar.subheader("🏆 لوحة المتصدرين")
for u, d in st.session_state.user_db.items():
    st.sidebar.text(f"{u}: {d['points']} ⭐")
