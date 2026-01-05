import streamlit as st

# 1. طابع التطبيق (أسود وذهبي)
st.set_page_config(page_title="our goal study", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    .stButton>button { background-color: #D4AF37; color: #000; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. عرض اللوجو
try:
    st.image("logo.png", width=200)
except:
    st.title("our goal study")

# 3. لوحة التحكم
st.sidebar.title("القائمة")
mode = st.sidebar.radio("انتقل إلى", ["الروم الرئيسية", "لوحة الإدارة"])

if mode == "لوحة الإدارة":
    st.header("🛡️ دخول المسؤول")
    user = st.text_input("الإيميل")
    if user == "ourgostudy@gmail.com":
        st.success("مرحباً بك!")
else:
    st.header("🏠 منطقة المذاكرة الذهبية")
    st.write("سجل دخولك الآن")
