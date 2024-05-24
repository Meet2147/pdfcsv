import streamlit as st
import streamlit.components.v1 as components
from utils import check_subscription, update_user_payment, initialize_db
from datetime import datetime, timedelta
import razorpay

# Configuration for Razorpay
razorpay_key_id = st.secrets["razorpay"]["key_id"]
razorpay_key_secret = st.secrets["razorpay"]["key_secret"]
client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

def create_order(amount):
    order = client.order.create({
        "amount": amount * 100,  # Amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })
    return order

def verify_payment(payment_id):
    try:
        payment = client.payment.fetch(payment_id)
        if payment['status'] == 'captured':
            return True
        return False
    except Exception as e:
        return False

def payment():
    initialize_db()  # Ensure the database schema is created

    if 'payment_verified' not in st.session_state:
        st.session_state.payment_verified = False
    if 'subscription_option' not in st.session_state:
        st.session_state.subscription_option = None
    if 'razorpay_order_id' not in st.session_state:
        st.session_state.razorpay_order_id = None

    if st.session_state.logged_in and not st.session_state.payment_verified:
        st.sidebar.subheader("Subscribe to Continue")
        subscription_option = st.sidebar.selectbox(
            "Choose your subscription plan:",
            ["499₹ Lifetime", "299₹ 6 Months"]
        )

        if st.sidebar.button("Subscribe"):
            if subscription_option == "499₹ Lifetime":
                st.session_state.subscription_option = "Lifetime"
                amount = 1
                payment_button_id = "pl_ODwpT1Oah9kcWp"
            elif subscription_option == "299₹ 6 Months":
                st.session_state.subscription_option = "6 Months"
                amount = 1
                payment_button_id = "pl_OEGS2RsMAH9sIW"

            order = create_order(amount)
            st.session_state.razorpay_order_id = order['id']

            components.html(
                f"""
                <form>
                    <script src="https://checkout.razorpay.com/v1/checkout.js" data-key="{razorpay_key_id}" data-amount="{amount * 100}" data-currency="INR" data-order_id="{st.session_state.razorpay_order_id}" async></script>
                </form>
                """,
                height=600,
            )

        payment_id = st.sidebar.text_input("Enter Payment ID")

        if st.sidebar.button("Verify Payment"):
            if verify_payment(payment_id):
                if st.session_state.subscription_option == "6 Months":
                    subscription_end = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
                else:
                    subscription_end = "Full"  # Lifetime access

                update_user_payment(st.session_state.user_email, payment_id, subscription_end)
                st.session_state.payment_verified = True
                st.sidebar.success("Payment verified successfully! You can now access the main app.")
                st.experimental_rerun()
            else:
                st.sidebar.error("Payment verification failed. Please check the payment ID and try again.")

    return st.session_state.payment_verified
