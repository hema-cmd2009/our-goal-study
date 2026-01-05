import streamlit as st
import time

# 1. الإعدادات والتصميم
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    .stApp { background: #000; color: #D4AF37; }
    .timer-text { font-size: 100px; text-align: center; font-weight: bold; color: #D4AF37; text-shadow: 0 0 20px #D4AF37; }
    .lobby-status { padding: 20px; border-radius: 15px; background: #111; border: 1px solid #333; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; background: #D4AF37; color: #000; font-weight: bold; border-radius: 10px; }
    .member-tag { padding: 5px 15px; background: #222; border-radius: 20px; border: 1px solid #D4AF37; display: inline-block; margin: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. المخزن المشترك (داتا الروم)
@st.cache_resource
def init_room():
    return {
        "status": "waiting", # waiting, running, break
        "members": [],
        "start_time": None,
        "duration": 60
    }

room_data = init_room()

# التحقق من وجود رابط (Parameter) في المتصفح
query_params = st.query_params
is_invited = "room" in query_params

# ----------------- 🏠 صفحة الدخول (للاعضاء عبر الرابط) -----------------
if is_invited:
    st.markdown("<h1 style='text-align: center;'>🎓 الانضمام للجلسة</h1>", unsafe_allow_html=True)
    
    if room_data["status"] == "waiting":
        st.info("أنت الآن في قاعة الانتظار.. يرجى إدخال اسمك وانتظار الأدمن لبدء التايمر.")
        name = st.text_input("اكتب اسمك ليظهر للزملاء")
        if st.button("تأكيد الانضمام"):
            if name and name not in room_data["members"]:
                room_data["members"].append(name)
                st.success(f"تم تسجيلك يا {name}! لا تغلق الصفحة.")
    
    elif room_data["status"] == "running":
        st.markdown(f"<div class='timer-text'>{room_data['duration']}:00</div>", unsafe_allow_html=True)
        st.success("الجلسة بدأت بالفعل! ركز في مذاكرتك.")
        
    # عرض الزملاء المتواجدين حالياً
    st.write("---")
    st.subheader(f"الزملاء المنتظرون ({len(room_data['members'])})")
    for m in room_data["members"]:
        st.markdown(f"<span class='member-tag'>👤 {m}</span>", unsafe_allow_html=True)

# ----------------- 🛡️ لوحة التحكم (للأدمن فقط) -----------------
else:
    st.title("🛡️ إدارة جلسات 'Our Goal Study'")
    
    tab1, tab2 = st.tabs(["إنشاء جلسة جديدة", "التحكم المباشر"])
    
    with tab1:
        st.subheader("1. جهز الرابط")
        # إنشاء رابط الروم بناءً على رابط موقعك
        base_url = "https://our-goal-study.streamlit.app/" # استبدله برابط موقعك الحقيقي
        invite_link = f"{base_url}?room=goal1"
        st.code(invite_link, language="text")
        st.info("انسخ الرابط أعلاه وأرسله لمن تريد انضمامهم.")
        
        st.subheader("2. الإعدادات")
        duration = st.number_input("مدة الجلسة (دقائق)", 5, 500, 45)
        if st.button("حفظ الإعدادات وفتح قاعة الانتظار"):
            room_data["status"] = "waiting"
            room_data["duration"] = duration
            room_data["members"] = []
            st.success("قاعة الانتظار مفتوحة الآن.. بانتظار دخول الطلاب عبر الرابط.")

    with tab2:
        st.subheader("الطلاب المتصلون حالياً:")
        if not room_data["members"]:
            st.write("لا يوجد أحد في الانتظار بعد..")
        else:
            for m in room_data["members"]:
                st.markdown(f"<span class='member-tag'>✅ {m}</span>", unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🔥 ابدأ التايمر عند الجميع الآن"):
                room_data["status"] = "running"
                st.balloons()
                st.success("بدأت الجلسة عند كل الطلاب!")
            
            if st.button("🛑 إنهاء الجلسة وطرد الجميع"):
                room_data["status"] = "waiting"
                room_data["members"] = []
                st.rerun()

# تحديث تلقائي للصفحة كل 5 ثواني لمتابعة الحالة
time.sleep(5)
st.rerun()
