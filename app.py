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

# ✅ Force starting step
if "step" not in st.session_state:
    st.session_state.step = "email"

st.warning(f"Current Step: {st.session_state.get('step')}")  # Debug current step

# ✅ Step 1: Email entry
if st.session_state.step == "email":
    st.subheader("🔐 Voter Email Verification")
    email = st.text_input("Enter your email to receive a verification code")

    if st.button("Send Verification Code"):
        st.warning("📤 Send Code button clicked")
        if has_email_already_voted(email):
            st.warning("⚠️ This email has already voted.")
        else:
            st.warning("📥 Attempting to send verification code...")
            send_verification_code(email)
            st.warning("✅ Verification code sent (or attempted to send)")
            st.session_state.email = email
            st.session_state.step = "verify"

# ✅ Step 2: Code verification
elif st.session_state.step == "verify":
    st.subheader("📩 Enter Verification Code")
    code = st.text_input("Enter the 6-digit code sent to your email")

    if st.button("Verify Code"):
        if verify_code(st.session_state.email, code):
            st.success("✅ Verification successful!")
            st.session_state.step = "vote"
        else:
            st.error("❌ Invalid or expired code. Please try again.")

# ✅ Step 3: Voting form
elif st.session_state.step == "vote":
    st.subheader("🗳️ Submit Your Vote")
    device_id = get_device_id()

    if has_already_voted(device_id):
        st.warning("⚠️ This device has already voted.")
    else:
        party = st.selectbox("Preferred Political Party", [
            "A Partnership for National Unity (APNU)",
            "Assembly for Liberty and Prosperity (ALJ)",
            "A New and United Guyana (ANUG)",
            "Guyana Action Party (GAP)",
            "People's Progressive Party (PPP)",
            "The Citizenship Initiative (TCI)",
            "The Justice For All Party (JFAP)",
            "The New Movement (TNM)",
            "United Republican Party (URP)",
            "Working People's Alliance (WPA)"
        ])

        candidate = st.text_input("Preferred Candidate (Optional)")
        reason = st.text_area("Why do you prefer this candidate?", height=100)
        issue = st.selectbox("Top National Issue", [
            "Jobs and Wages",
            "Education Quality",
            "Crime and Security",
            "Healthcare Access",
            "Oil Revenues Management",
            "Renegotiate the 2016 PSA Oil Contract",
            "Corruption Control",
            "Cost of Living",
            "Other"
        ])

        age_group = st.selectbox("Your Age Group", ["18-25", "26-35", "36-45", "46-60", "60+"])
        gender = st.selectbox("Your Gender", ["Male", "Female", "Other", "Prefer not to say"])
        region = st.selectbox("Your Region", [
            "Region 1 - Barima-Waini",
            "Region 2 - Pomeroon-Supenaam",
            "Region 3 - Essequibo Islands-West Demerara",
            "Region 4 - Demerara-Mahaica",
            "Region 5 - Mahaica-Berbice",
            "Region 6 - East Berbice-Corentyne",
            "Region 7 - Cuyuni-Mazaruni",
            "Region 8 - Potaro-Siparuni",
            "Region 9 - Upper Takutu-Upper Essequibo",
            "Region 10 - Upper Demerara-Berbice"
        ])

        trust = st.radio("Trust in GECOM?", ["Yes", "No", "Unsure"])

        if st.button("Submit Vote"):
            vote_data = {
                "Vote": party,
                "Candidate": candidate,
                "Reason": reason,
                "Issue": issue,
                "Age Group": age_group,
                "Gender": gender,
                "Region": region,
                "Trust in GECOM": trust,
                "device_id": device_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            record_vote(st.session_state.email, vote_data, device_id)
            st.success("🎉 Your vote has been recorded! Thank you for participating.")
            st.session_state.step = "completed"

# ✅ Step 4: Confirmation screen
elif st.session_state.step == "completed":
    st.header("🎉 Thank you for voting!")
    st.write("Your response has been recorded successfully.")

# ✅ Admin dashboard (sidebar)
st.sidebar.subheader("🔑 Admin Login")
admin_key = st.sidebar.text_input("Enter admin key", type="password")
if admin_key == st.secrets["ADMIN_KEY"]["ADMIN_KEY"]:
    st.sidebar.success("Admin mode activated ✅")
    st.header("📊 Live Vote Dashboard")

    all_votes = get_vote_sheet()
    st.dataframe(all_votes)

    # Distribution by Party
    st.subheader("🗳️ Vote Distribution by Party")
    party_dist = get_field_distribution("Vote")
    st.bar_chart(party_dist)

    # Distribution by Issue
    st.subheader("🔥 Top National Issues")
    issue_dist = get_field_distribution("Issue")
    st.bar_chart(issue_dist)

    # Trust in GECOM
    st.subheader("⚖️ Trust in GECOM?")
    trust_dist = get_field_distribution("Trust in GECOM")
    st.bar_chart(trust_dist)

    # Optional: Filter by Date
    st.subheader("📅 Filter Votes by Date Range")
    start = st.date_input("Start Date", key="start_date")
    end = st.date_input("End Date", key="end_date")

    if st.button("Filter Results"):
        filtered = filter_votes_by_date(start, end)
        st.dataframe(filtered)
