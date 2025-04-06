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

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Secure Voting App", layout="centered")

st.title("🗳️ Guyana 2025 Voter Opinion Poll")

# Session state setup
if "step" not in st.session_state:
    st.session_state.step = "email"
if "email" not in st.session_state:
    st.session_state.email = ""

# 🔐 Admin access (optional)
st.sidebar.subheader("🔑 Admin Login")
admin_key = st.sidebar.text_input("Enter admin key", type="password")
if admin_key == st.secrets["ADMIN_KEY"]["ADMIN_KEY"]:
    st.sidebar.success("Admin mode activated ✅")
    st.header("📊 Live Vote Dashboard")

    # Date filter
    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
    end_date = st.date_input("End Date", datetime.date.today())
    filtered_df = filter_votes_by_date(start_date, end_date)
    st.dataframe(filtered_df)

    st.subheader("Vote Summary")
    stats = get_field_distribution("Vote")
    st.bar_chart(stats)
    st.stop()

# 👣 Step 1: Email entry
if st.session_state.step == "email":
    email = st.text_input("Enter your email to receive a verification code")
    if st.button("Send Code"):
        if has_email_already_voted(email):
            st.warning("This email has already voted.")
        else:
            send_verification_code(email)
            st.session_state.email = email
            st.session_state.step = "verify"
            st.rerun()  # 🔁 Force rerun to move to verify step
    st.stop()

# 👣 Step 2: Verification code
elif st.session_state.step == "verify":
    st.info(f"Verification code sent to {st.session_state.email}")
    code = st.text_input("Enter the verification code")
    if st.button("Verify Code"):
        if verify_code(st.session_state.email, code):
            st.success("✅ Verified! You may now vote.")
            st.session_state.step = "vote"
            st.rerun()  # 🔁 Force rerun to show vote step
        else:
            st.error("❌ Invalid or expired code. Try again.")
    st.stop()

# 👣 Step 3: Cast vote
elif st.session_state.step == "vote":
    st.subheader("Please select your choice")
    choice = st.radio("Your Vote:", ["Option A", "Option B", "Option C"])
    if st.button("Submit Vote"):
        device_id = get_device_id()
        if has_already_voted(device_id):
            st.warning("This device has already submitted a vote.")
        else:
            record_vote(st.session_state.email, choice, device_id)
            st.success("✅ Thank you for voting!")
            st.session_state.step = "done"
            st.rerun()  # 🔁 Force rerun to show confirmation
    st.stop()

# 👣 Step 4: Confirmation
elif st.session_state.step == "done":
    st.balloons()
    st.markdown("### ✅ Your response has been recorded. Thank you!")
