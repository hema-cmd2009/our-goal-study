import streamlit as st
import time

# 1. تصميم الواجهة الاحترافية (Teams Style - Black & Gold)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    /* ستايل الأزرار */
    .stButton>button { 
        background-color: #D4AF37; color: #000; border-radius: 8px; 
        font-weight: bold; border: none; width: 100%; height: 45px;
    }
    /* ستايل كروت الأعضاء (زي تيمز) */
    .member-card { 
        background: #111111; border: 1px solid #D4AF37; border-radius: 10px;
        padding: 20px; text-align: center; margin-bottom: 10px;
    }
    .status-online { color: #00FF00; font-size: 12px; }
    /* التايمر */
    .timer-display { font-size: 60px; font-weight: bold; text-align: center; color: #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 2. إدارة "الغرفة" والبيانات
if 'users' not in st.session_state: st.session_state.users = {}
if 'is_live' not in st.session_state: st.session_state.is_live = False

# القائمة الجانبية (Sidebar) مع اللوجو
with st.sidebar:
    try: st.image("logo.png", width=120)
    except: st.title("OGS")
    menu = st.radio("الذهاب إلى:", ["🏠 ساحة المذاكرة", "⚙️ الإدارة", "👤 حسابي"])

# ----------------- ⚙️ لوحة الإدارة -----------------
if menu == "⚙️ الإدارة":
    st.header("🛡️ التحكم بالاجتماع")
    admin_pw = st.text_input("كلمة مرور المسؤول", type="password")
    if admin_pw == "our122122":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 بدء جلسة مذاكرة"): st.session_state.is_live = True
        with col2:
            if st.button("🛑 إنهاء الجلسة"): st.session_state.is_live = False
        
        st.write("---")
        st.subheader("👥 الأعضاء المسجلين")
        for user in st.session_state.users.keys():
            st.text(f"• {user}")

# ----------------- 🏠 ساحة المذاكرة (Like Teams) -----------------
elif menu == "🏠 ساحة المذاكرة":
    if not st.session_state.is_live:
        st.warning("⚠️ لا توجد جلسة مذاكرة جارية الآن. يرجى انتظار المسؤول.")
    else:
        st.markdown("<h1 style='text-align: center;'>Our Goal Study Room</h1>", unsafe_allow_html=True)
        
        # تسجيل الدخول السريع
        name = st.text_input("ادخل اسمك للانضمام للاجتماع")
        if name:
            st.session_state.users[name] = "Online"
            
            # عرض التايمر في المنتصف
            st.markdown("<div class='timer-display'>01:45:00</div>", unsafe_allow_html=True)
            
            # شبكة الأعضاء (Grid Like Teams)
            st.subheader(f"المشاركون ({len(st.session_state.users)})")
            cols = st.columns(4)
            for i, (user, status) in enumerate(st.session_state.users.items()):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class='member-card'>
                        <div style='font-size: 40px;'>👤</div>
                        <div style='font-weight: bold;'>{user}</div>
                        <div class='status-online'>● {status}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ----------------- 👤 حسابي -----------------
else:
    st.header("👤 ملفك الشخصي")
    st.info("قريباً: سيتم ربط حساب جوجل مباشرة هنا.")
