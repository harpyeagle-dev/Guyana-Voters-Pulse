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

# ✅ Set page config at the very top
st.set_page_config(page_title="Secure Voting App", layout="centered")

# ✅ Force session to start at email step if not set
if "step" not in st.session_state:
    st.session_state.step = "email"

# The rest of your Streamlit app logic continues here...
# (Add logic for step == "email", "verify", "vote", "admin" as needed)

if st.session_state.step == "email":
    email = st.text_input("Enter your email to receive a verification code")

    if st.button("Send Code"):
        if has_email_already_voted(email):
            st.warning("This email has already voted.")
        else:
            send_verification_code(email)
            st.session_state.email = email
            st.session_state.step = "verify"

# You can add other steps like verify and vote here...
