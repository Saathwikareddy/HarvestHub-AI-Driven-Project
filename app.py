import streamlit as st
from supabase import create_client
import bcrypt
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Harvest Hub", page_icon="🌾")

# ---------------- SUPABASE ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.email = None

# ---------------- CROP RECOMMENDATION MODEL ----------------

data = {
    "Soil": ["Clay","Loamy","Black","Clay","Loamy","Black"],
    "Season": ["Kharif","Rabi","Kharif","Rabi","Kharif","Rabi"],
    "Water": ["High","Medium","Medium","High","Low","Medium"],
    "Crop": ["Rice","Wheat","Cotton","Maize","Rice","Wheat"]
}

df = pd.DataFrame(data)

le_soil = LabelEncoder()
le_season = LabelEncoder()
le_water = LabelEncoder()
le_crop = LabelEncoder()

df["Soil"] = le_soil.fit_transform(df["Soil"])
df["Season"] = le_season.fit_transform(df["Season"])
df["Water"] = le_water.fit_transform(df["Water"])
df["Crop"] = le_crop.fit_transform(df["Crop"])

X = df[["Soil","Season","Water"]]
y = df["Crop"]

model = DecisionTreeClassifier()
model.fit(X, y)

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
        if not all([email.strip(), username.strip(), fullname.strip(), phone.strip(), password.strip(), confirm_password.strip()]):
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

# ---------------- FARMER DASHBOARD ----------------
    if st.session_state.role == "Farmer":

        tab1, tab2, tab3 = st.tabs([
            "➕ Add Product",
            "📦 View Orders",
            "🌱 Crop Recommendation"
        ])

# ---------- ADD PRODUCT ----------
        with tab1:

            st.subheader("Add Agricultural Product")

            pname = st.text_input("Product Name")
            price = st.number_input("Price", min_value=0.0)
            quantity = st.number_input("Quantity", min_value=0.0)
            category = st.text_input("Category")

            if st.button("Add Product"):

                supabase.table("products").insert({
                    "farmer_email": st.session_state.email,
                    "product_name": pname,
                    "price": price,
                    "quantity": quantity,
                    "category": category
                }).execute()

                st.success("Product Added Successfully")

# ---------- VIEW ORDERS ----------
        with tab2:

            st.subheader("Customer Orders")

            orders = supabase.table("orders").select("*").execute()

            if orders.data:

                for order in orders.data:

                    st.write("Order ID:", order["id"])
                    st.write("Product:", order["product_name"])
                    st.write("Customer:", order["customer_email"])
                    st.write("Quantity:", order["quantity"])
                    st.write("Status:", order["status"])
                    st.write("---")

            else:
                st.info("No orders yet")

# ---------- CROP RECOMMENDATION ----------
        with tab3:

            st.subheader("Crop Recommendation System")

            soil = st.selectbox(
                "Select Soil Type",
                ["Clay", "Loamy", "Black"]
            )

            season = st.selectbox(
                "Select Season",
                ["Kharif", "Rabi"]
            )

            water = st.selectbox(
                "Water Requirement",
                ["Low", "Medium", "High"]
            )

            if st.button("Predict Best Crop"):

                soil_enc = le_soil.transform([soil])[0]
                season_enc = le_season.transform([season])[0]
                water_enc = le_water.transform([water])[0]

                prediction = model.predict([[soil_enc, season_enc, water_enc]])

                crop = le_crop.inverse_transform(prediction)

                st.success(f"Recommended Crop: {crop[0]}")

# ---------------- CUSTOMER DASHBOARD ----------------
    elif st.session_state.role == "Customer":

        st.info("🛒 Customer Dashboard - Browse and order products")

# ---------------- OTHER ROLES ----------------
    else:

        st.info("🏢 General Dashboard")

# ---------------- LOGOUT ----------------
    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.email = None

        st.success("Logged out successfully")

