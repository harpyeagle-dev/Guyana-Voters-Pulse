import streamlit as st
import datetime
from vote_utils import (
    record_vote,
    has_already_voted,
    has_email_already_voted,
    get_vote_stats,
    get_vote_sheet,
    filter_votes_by_date,
    get_field_distribution
)
from device_utils import get_device_id
from email_verification import send_verification_code, verify_code

# ✅ Set page config FIRST
st.set_page_config(page_title="Secure Voting App", layout="centered")

# ✅ Initialize session state
if "step" not in st.session_state:
    st.session_state.step = "email"

# ✅ Step 1: Enter Email
if st.session_state.step == "email":
    st.subheader("🔐 Voter Email Verification")

    email = st.text_input("Enter your email to receive a verification code")

    send_code = st.button("Send Verification Code")

    if send_code:
        if has_email_already_voted(email):
            st.warning("⚠️ This email has already voted.")
        else:
            with st.spinner("Sending verification code..."):
                send_verification_code(email)
                st.session_state.email = email
                st.session_state.step = "verify"
                st.rerun()

# ✅ Step 2: Verify Code
elif st.session_state.step == "verify":
    st.subheader("📩 Enter Verification Code")

    code = st.text_input("Enter the 6-digit code sent to your email")

    verify_button = st.button("Verify Code")

    if verify_button:
        with st.spinner("Verifying code..."):
            if verify_code(st.session_state.email, code):
                st.success("✅ Verification successful!")
                st.session_state.step = "vote"
                st.rerun()
            else:
                st.error("❌ Invalid or expired code. Please try again.")

# ✅ Step 3: Vote (placeholder for now, we can polish next)
elif st.session_state.step == "vote":
    st.subheader("🗳️ Cast Your Vote")
    st.success("✅ Ready to vote!")
    # Voting form will come here (I'll send next!)

# ✅ Step 4: Thank You Page (after voting)
elif st.session_state.step == "completed":
    st.balloons()
    st.success("🎉 Thank you for participating in the Elections 2025 Opinion Poll!")
