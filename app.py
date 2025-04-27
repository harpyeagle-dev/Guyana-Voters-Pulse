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

# ✅ Set page config immediately
st.set_page_config(page_title="Secure Voting App", layout="centered")

# ✅ Init session state
if "step" not in st.session_state:
    st.session_state.step = "email"

if "email" not in st.session_state:
    st.session_state.email = ""

if "vote_submitted" not in st.session_state:
    st.session_state.vote_submitted = False

# ✅ Admin Panel in Sidebar
st.sidebar.title("🔧 Admin Access")
admin_key_input = st.sidebar.text_input("Admin Key", type="password")

is_admin = False
if admin_key_input == st.secrets["ADMIN_KEY"]["ADMIN_KEY"]:
    is_admin = True
    st.sidebar.success("✅ Admin Mode Activated")

# ✅ Step 1: Enter Email
if st.session_state.step == "email":
    st.title("🔐 Elections 2025 Voter Verification")
    
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
    st.title("📩 Enter Verification Code")

    code = st.text_input("Enter the 6-digit code sent to your email")

    verify_code_button = st.button("Verify Code")

    if verify_code_button:
        with st.spinner("Verifying code..."):
            if verify_code(st.session_state.email, code):
                st.success("✅ Verification successful!")
                st.session_state.step = "vote"
                st.rerun()
            else:
                st.error("❌ Invalid or expired code. Please try again.")

# ✅ Step 3: Voting Form
elif st.session_state.step == "vote":
    st.title("🗳️ Elections 2025 Opinion Poll")

    st.subheader("Please fill out your selections:")

    party = st.selectbox("Preferred Political Party", [
        "Assembly for Liberty and Prosperity (ALP)",
        "A New and United Guyana (ANUG)",
        "Justice for All Party (JFAP)",
        "People's Progressive Party/Civic (PPP/C)",
        "People's National Congress Reform (PNC/R)",
        "The New Movement (TNM)",
        "The Citizenship Initiative (TCI)",
        "United Republican Party (URP)",
        "Working People's Alliance (WPA)"
    ])

    candidate = st.text_input("Preferred Candidate and why")

    issues = st.multiselect(
        "Top Issues You Care About",
        [
            "Education",
            "Healthcare",
            "Jobs and Economy",
            "Security and Crime",
            "Oil and Gas Management",
            "Renegotiate the 2016 PSA Oil Contract",
            "Infrastructure",
            "Cost of Living",
            "Corruption",
            "Environment"
        ]
    )

    trust_gecom = st.radio(
        "How much do you trust GECOM to deliver free and fair elections?",
        ["High", "Moderate", "Low", "No Trust"]
    )

    age_group = st.selectbox(
        "Your Age Group",
        ["18-24", "25-34", "35-44", "45-54", "55+"]
    )

    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])

    region = st.selectbox(
        "Your Region",
        [
            "Region 1: Barima-Waini",
            "Region 2: Pomeroon-Supenaam",
            "Region 3: Essequibo Islands-West Demerara",
            "Region 4: Demerara-Mahaica",
            "Region 5: Mahaica-Berbice",
            "Region 6: East Berbice-Corentyne",
            "Region 7: Cuyuni-Mazaruni",
            "Region 8: Potaro-Siparuni",
            "Region 9: Upper Takutu-Upper Essequibo",
            "Region 10: Upper Demerara-Berbice"
        ]
    )

    submit_vote = st.button("Submit Vote")

    if submit_vote:
        with st.spinner("Submitting your vote..."):
            device_id = get_device_id()
            record_vote(
                st.session_state.email,
                {
                    "Vote": party,
                    "Candidate": candidate,
                    "Issues": issues,
                    "Trust in GECOM": trust_gecom,
                    "Age Group": age_group,
                    "Gender": gender,
                    "Region": region,
                    "device_id": device_id,
                    "timestamp": datetime.datetime.now().isoformat()
                },
                device_id=device_id
            )
            st.success("🎉 Your vote has been submitted successfully!")
            st.session_state.step = "completed"
            st.rerun()

# ✅ Step 4: Thank You Page
elif st.session_state.step == "completed":
    st.title("🎉 Thank You for Participating!")
    st.balloons()
    st.success("Your opinion has been recorded.")

# ✅ Admin Dashboard
if is_admin:
    st.header("📊 Live Voter Dashboard")

    tab1, tab2, tab3 = st.tabs(["Votes Summary", "Vote Sheet", "Filter by Date"])

    with tab1:
        st.subheader("Vote Counts")
        vote_counts = get_vote_stats()
        st.bar_chart(vote_counts)

    with tab2:
        st.subheader("All Votes")
        df_votes = get_vote_sheet()
        st.dataframe(df_votes)

    with tab3:
        st.subheader("Filter Votes by Date")
        start_date = st.date_input("Start Date", key="start")
        end_date = st.date_input("End Date", key="end")
        if start_date and end_date:
            filtered = filter_votes_by_date(start_date, end_date)
            st.dataframe(filtered)
