import sqlite3
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def get_db_connection():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (email TEXT PRIMARY KEY, 
               password TEXT, 
               otp INTEGER,
               payment_id TEXT,
               subscription_end TEXT)
              ''')
    conn.commit()
    conn.close()

def send_otp(email, password):
    otp = random.randint(100000, 999999)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (email, otp) VALUES (?, ?)', (email, otp))
    conn.commit()
    conn.close()
    msg = MIMEMultipart()
    msg['From'] = st.secrets["email"]["username"]
    msg['To'] = email
    msg['Subject'] = "Your OTP and Password for Signup"
    body = f"Your OTP is {otp}\nYour Password is {password}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(st.secrets["email"]["username"], st.secrets["email"]["password"])
        text = msg.as_string()
        server.sendmail(st.secrets["email"]["username"], email, text)
        server.quit()
        print(f"OTP and Password sent to {email}: {otp}")  # Debug print
        return True
    except Exception as e:
        print(e)
        return False

def verify_otp(email, otp_input):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT otp FROM users WHERE email=?', (email,))
    stored_otp = c.fetchone()
    conn.close()
    print(f"Stored OTP for {email}: {stored_otp}")  # Debug print
    if stored_otp and stored_otp[0] == int(otp_input):
        return True
    return False

def check_subscription(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT subscription_end FROM users WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    if result:
        subscription_end = result['subscription_end']
        if subscription_end == "Full" or datetime.strptime(subscription_end, '%Y-%m-%d') > datetime.now():
            return True
    return False

def update_user_payment(email, payment_id, subscription_end):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET payment_id=?, subscription_end=? WHERE email=?', (payment_id, subscription_end, email))
    conn.commit()
    conn.close()
