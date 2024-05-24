import streamlit as st
from utils import send_otp, verify_otp, get_db_connection, initialize_db

def signup():
    st.sidebar.subheader("Sign up")
    email = st.sidebar.text_input("Enter your email")
    password = st.sidebar.text_input("Enter a password", type="password")
    if st.sidebar.button("Send OTP"):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT email FROM users WHERE email=?', (email,))
        if not c.fetchone():
            if send_otp(email, password):
                st.session_state.user_email = email
                st.sidebar.success("OTP and Password have been sent to your email.")
            else:
                st.sidebar.error("Failed to send OTP. Please try again.")
        else:
            st.sidebar.error("Email already registered.")
        conn.close()
    
    otp_input = st.sidebar.text_input("Enter OTP received")
    if st.sidebar.button("Verify OTP"):
        if verify_otp(st.session_state.user_email, otp_input):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('UPDATE users SET password=? WHERE email=?', (password, st.session_state.user_email))
            conn.commit()
            conn.close()
            st.session_state.logged_in = True
            st.sidebar.success("OTP verified successfully! You are now logged in.")
            st.experimental_rerun()
        else:
            st.sidebar.error("Incorrect OTP. Please try again.")

def login():
    st.sidebar.subheader("Login")
    email = st.sidebar.text_input("Enter your email", key="login_email")
    password = st.sidebar.text_input("Enter your password", type="password", key="login_password")
    if st.sidebar.button("Login"):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT email, password FROM users WHERE email=? AND password=?', (email, password))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.sidebar.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid email or password")
        conn.close()

def auth():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    initialize_db()  # Ensure the database schema is created

    if not st.session_state.logged_in:
        st.sidebar.subheader("Account")
        choice = st.sidebar.radio("Choose an option:", ["Login", "Sign up"])

        if choice == "Sign up":
            signup()
        elif choice == "Login":
            login()
