import streamlit as st
from supabase import create_client
import bcrypt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Harvest Hub", page_icon="🌾")

# ---------------- SUPABASE ----------------
# Use Streamlit Secrets for cloud deployment
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox("Menu", ["Register", "Login"])

# ---------------- REGISTER ----------------
if menu == "Register":
    st.title("🌱 Harvest Hub - Create Account")

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
            # Check if user already exists
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

                st.success("Account created successfully! You can now log in.")

# ---------------- LOGIN ----------------
if menu == "Login":
    st.title("🔐 Harvest Hub - Login")

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

                st.success(f"Welcome! Logged in as {st.session_state.role}")
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

# ---------------- DASHBOARD ----------------
if st.session_state.logged_in:
    st.divider()
    st.header("📊 Dashboard")
    st.write("Logged in as:", st.session_state.email)
    st.write("Role:", st.session_state.role)

    if st.session_state.role == "Farmer":
        st.info("🌾 Farmer Dashboard (Add products, manage inventory)")
    elif st.session_state.role == "Customer":
        st.info("🛒 Customer Dashboard (Browse & order produce)")
    else:
        st.info("🏢 General Dashboard")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.email = None
        st.success("Logged out successfully")
