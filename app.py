import streamlit as st

# 🔐 Must be the first Streamlit command
st.set_page_config(page_title="Secure Voting App", layout="centered")

import datetime
import pandas as pd
import smtplib
from email_verification import send_verification_code, verify_code
import matplotlib.pyplot as plt
from firebase_config import db
from dashboard_utils import show_dashboard

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
    show_dashboard()  # ⬅️ displays the full admin dashboard

    # Date filter
    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
    end_date = st.date_input("End Date", datetime.date.today())

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    # Convert timestamps to dates for filtering
    all_votes = db.reference("/votes").get() or {}
    rows = []
    for key, data in all_votes.items():
        ts = pd.to_datetime(data.get("timestamp", ""), errors="coerce")
        if ts and start_date <= ts.date() <= end_date:
            data["timestamp"] = ts
            rows.append(data)
    filtered_df = pd.DataFrame(rows)

    st.metric("Total Votes", len(filtered_df))

    st.subheader("📄 Full Responses")
    st.dataframe(filtered_df)

    st.subheader("📊 Bar Charts")
    for field in ["Preferred Party", "Age Group", "Region"]:
        st.markdown(f"**{field}**")
        counts = filtered_df[field].value_counts()
        st.bar_chart(counts)

    st.subheader("🥧 Pie Charts")
    for field in ["Gender", "Trust in GECOM"]:
        st.markdown(f"**{field}**")
        data = filtered_df[field].value_counts()
        fig, ax = plt.subplots()
        ax.pie(data.values, labels=data.index, autopct="%1.1f%%")
        ax.axis("equal")
        st.pyplot(fig)

    st.subheader("📈 Votes Over Time")
    timeline = filtered_df["timestamp"].dt.date.value_counts().sort_index()
    st.line_chart(timeline)

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
            st.rerun()
    st.stop()

# 👣 Step 2: Verification code
elif st.session_state.step == "verify":
    st.info(f"Verification code sent to {st.session_state.email}")
    code = st.text_input("Enter the verification code")
    if st.button("Verify Code"):
        if verify_code(st.session_state.email, code):
            st.success("✅ Verified! You may now vote.")
            st.session_state.step = "vote"
            st.rerun()
        else:
            st.error("❌ Invalid or expired code. Try again.")
    st.stop()

# 👣 Step 3: Opinion poll form
elif st.session_state.step == "vote":
    st.subheader("🗳️ 2025 Voter Opinion Poll")

    party = st.radio("Which political party would you most likely support?", [
        "A New and United Guyana (ANUG)",
        "A Partnership for National Unity + Alliance For Change (APNU+AFC)",
        "Alliance For Change (AFC)",
        "Assembly for Liberty and Prosperity (ALP)",
        "Citizens Initiative (CI)",
        "Guyana Action Party (GAP)",
        "Justice For All Party (JFAP)",
        "Liberty and Justice Party (LJP)",
        "Organization for the Victory of the People (OVP)",
        "People’s Progressive Party/Civic (PPP/C)",
        "The New Movement (TNM)",
        "United Republican Party (URP)",
        "Working People’s Alliance (WPA)",
        "Other"
    ])

    candidates = st.text_area("Which candidate(s) do you prefer and why?")

    issues = st.multiselect("What are the top issues that matter to you in the 2025 elections?", [
        "Cost of living", "Youth employment", "Corruption", "Education",
        "Healthcare", "Security", "Climate/environment", "Renegotiate the 2016 PSA Oil Contract"
    ])

    age_group = st.selectbox("What is your age group?", [
        "Under 18", "18–24", "25–34", "35–44", "45–60", "Over 60"
    ])

    gender = st.radio("What is your gender?", [
        "Male", "Female", "Non-binary", "Prefer not to say"
    ])

    region = st.selectbox("Which region do you live in?", [
        f"Region {i}" for i in range(1, 11)
    ] + ["Prefer not to say"])

    trust = st.radio("How much do you trust GECOM to conduct free and fair elections?", [
        "Strongly trust", "Somewhat trust", "Neutral", "Somewhat distrust", "Strongly distrust"
    ])

    if st.button("Submit Vote"):
        device_id = get_device_id()
        if has_already_voted(device_id):
            st.warning("This device has already submitted a vote.")
        else:
            vote_data = {
                "Preferred Party": party,
                "Preferred Candidates": candidates,
                "Top Issues": issues,
                "Age Group": age_group,
                "Gender": gender,
                "Region": region,
                "Trust in GECOM": trust,
                "device_id": device_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            record_vote(st.session_state.email, vote_data, device_id)
            st.session_state.vote_data = vote_data
            st.session_state.step = "done"

            # 📧 Send thank-you email
            try:
                msg = EmailMessage()
                msg["Subject"] = "Thank You for Participating in the Guyana 2025 Opinion Poll"
                msg["From"] = st.secrets["EMAIL"]["sender"]
                msg["To"] = st.session_state.email
                msg.set_content("Thank you for sharing your opinion in the Guyana 2025 Voter Poll. Your input has been recorded successfully.")

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(st.secrets["EMAIL"]["sender"], st.secrets["EMAIL"]["app_password"])
                    smtp.send_message(msg)
            except Exception as e:
                st.warning("⚠️ Could not send thank-you email.")
                st.exception(e)

            st.rerun()
    st.stop()

# 👣 Step 4: Confirmation and summary
elif st.session_state.step == "done":
    st.balloons()
    st.success("✅ Your response has been recorded. Thank you!")

    with st.expander("🔍 View Your Submission"):
        for k, v in st.session_state.vote_data.items():
            st.write(f"**{k}:** {v}")
