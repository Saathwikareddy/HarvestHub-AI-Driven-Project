import streamlit as st
from supabase import create_client
import bcrypt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Harvest Hub", page_icon="🌾", layout="centered")

# ---------------- BACKGROUND (CROPS) ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://static.vecteezy.com/system/resources/thumbnails/037/996/577/small_2x/ai-generated-cotton-flower-branch-on-nature-photo.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    /* Main card */
    .block-container {
        background-color: rgba(236, 247, 241, 0.92); /* soft mint green */
        padding: 2rem;
        border-radius: 18px;
        max-width: 700px;
        box-shadow: 0 10px 30px rgba(0, 60, 20, 0.25);
        border: 1px solid rgba(0, 120, 60, 0.25);
    }

    /* Headings */
    h2, h3 {
        color: #1b5e20;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- SUPABASE ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None

if "page" not in st.session_state:
    st.session_state.page = "Register"

# ---------------- TOP NAV BAR ----------------
st.markdown("<h2 style='text-align:center;'>🌾 Harvest Hub</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Register", use_container_width=True):
        st.session_state.page = "Register"

with col2:
    if st.button("🔐 Login", use_container_width=True):
        st.session_state.page = "Login"

st.divider()

# ---------------- REGISTER ----------------
if st.session_state.page == "Register" and not st.session_state.logged_in:
    st.subheader("Create Account")

    role = st.selectbox(
        "Account Type",
        ["Customer", "Farmer", "Market Owner", "Logistics"]
    )

    email = st.text_input("Email")
    username = st.text_input("Username")
    fullname = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not all([email, username, fullname, password, confirm_password]):
            st.error("Please fill all required fields")
        elif password != confirm_password:
            st.error("Passwords do not match")
        else:
            existing = supabase.table("users").select("id").eq("email", email).execute()
            if existing.data:
                st.error("Email already registered")
            else:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                supabase.table("users").insert({
                    "role": role,
                    "email": email,
                    "username": username,
                    "password": hashed_pw,
                    "fullname": fullname,
                    "phone": phone
                }).execute()

                st.success("Account created successfully! Please login.")
                st.session_state.page = "Login"

# ---------------- LOGIN ----------------
if st.session_state.page == "Login" and not st.session_state.logged_in:
    st.subheader("Login")

    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.table("users") \
            .select("password, role") \
            .eq("email", login_email) \
            .execute()

        if res.data:
            stored_pw = res.data[0]["password"]
            if bcrypt.checkpw(login_password.encode(), stored_pw.encode()):
                st.session_state.logged_in = True
                st.session_state.email = login_email
                st.session_state.role = res.data[0]["role"]
                st.success("Login successful 🎉")
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

# ---------------- DASHBOARD ----------------
if st.session_state.logged_in:
    st.divider()
    st.header("📊 Dashboard")
    st.write("👤 Email:", st.session_state.email)
    st.write("🧾 Role:", st.session_state.role)

    if st.session_state.role == "Farmer":
        st.info("🌾 Farmer Dashboard – Manage crops & inventory")
    elif st.session_state.role == "Customer":
        st.info("🛒 Customer Dashboard – Browse & order produce")
    else:
        st.info("🏢 General Dashboard")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.email = None
        st.session_state.page = "Login"
        st.success("Logged out successfully")


