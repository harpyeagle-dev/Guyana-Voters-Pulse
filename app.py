# app.py
import streamlit as st
st.set_page_config("Secure Voting App", layout="centered")

from firebase_config import db
from email_verification import send_verification_code, verify_code
from vote_utils import get_ip_address, get_device_id, has_already_voted, submit_vote, get_vote_stats
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime

# --- Set up cookies ---
cookies = EncryptedCookieManager(prefix="vote_", password="your-secret-key")
if not cookies.ready():
    st.stop()

# --- App layout ---
st.title("🗳️ Secure Voting App")

tabs = st.tabs(["✅ Vote", "📊 Dashboard", "🔐 Admin"])

# --- Vote tab ---
with tabs[0]:
    st.subheader("Step 1: Verify Email")
    email = st.text_input("Enter your email")

    if st.button("Send Code"):
        if email:
            send_verification_code(email)
            st.success("Verification code sent to your email.")

    code = st.text_input("Enter the 6-digit code")
    if st.button("Verify Code"):
        if verify_code(email, code):
            st.session_state["verified_email"] = email
            st.success("Email verified. You may now vote.")
        else:
            st.error("Invalid or expired code.")

    if "verified_email" in st.session_state:
        st.subheader("Step 2: Cast Your Vote")
        vote = st.radio("Choose your option", ["Option A", "Option B", "Option C"])
        if st.button("Submit Vote"):
            email = st.session_state["verified_email"]
            ip = get_ip_address()
            device_id = get_device_id(cookies)

            if has_already_voted(email=email, ip=ip, device_id=device_id):
                st.error("You have already voted from this device/email/IP.")
            else:
                submit_vote(email, vote, ip, device_id)
                st.success("✅ Your vote has been recorded!")

# --- Dashboard tab ---
with tabs[1]:
    st.subheader("📊 Live Vote Dashboard")
    stats_df = get_vote_stats()

    if stats_df.empty:
        st.info("No votes yet.")
    else:
        st.dataframe(stats_df)
        st.bar_chart(stats_df.set_index("option"))

# --- Admin tab ---
with tabs[2]:
    st.subheader("Admin Login")
    admin_pw = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        if admin_pw == "your_admin_password":  # Replace this securely later
            st.session_state["is_admin"] = True
        else:
            st.error("Incorrect password.")

    if st.session_state.get("is_admin"):
        st.success("Welcome, admin!")
        st.write("All Votes:")
        votes = db.collection("votes").stream()
        all_votes = [{"email": v.get("email"), "vote": v.get("vote"), "ip": v.get("ip"), "device_id": v.get("device_id"), "timestamp": v.get("timestamp")} for v in [v.to_dict() for v in votes]]
        st.dataframe(all_votes)
