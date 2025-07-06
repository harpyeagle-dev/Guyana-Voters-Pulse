# app.py
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials, firestore
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

st.set_page_config(page_title="Guyana Voters Pulse", layout="centered")

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Replace with your actual path
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = "email"
if "email" not in st.session_state:
    st.session_state.email = ""
if "vote_submitted" not in st.session_state:
    st.session_state.vote_submitted = False

# Admin Dashboard
st.sidebar.success("Access granted")

st.title("📊 Admin Dashboard")
st.subheader("Filter Responses")

# Filters
start_date = st.date_input("Start Date", datetime.date(2025, 1, 1))
end_date = st.date_input("End Date", datetime.date.today())
df = get_vote_sheet(db)

if df.empty:
    st.warning("⚠️ No votes found.")
else:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    filtered_df = df[
        (df["timestamp"] >= pd.to_datetime(start_date)) &
        (df["timestamp"] <= pd.to_datetime(end_date))
    ]

    age_filter = st.selectbox("Filter by Age", ["All"] + sorted(df["age"].dropna().unique().tolist()))
    region_filter = st.selectbox("Filter by Region", ["All"] + sorted(df["region"].dropna().unique().tolist()))
    trust_filter = st.selectbox("Trust in GECOM", ["All", "Yes", "No", "Not sure"])

    if age_filter != "All":
        filtered_df = filtered_df[filtered_df["age"] == age_filter]
    if region_filter != "All":
        filtered_df = filtered_df[filtered_df["region"] == region_filter]
    if trust_filter != "All":
        filtered_df = filtered_df[filtered_df["trust_gecom"] == trust_filter]

    st.write("Filtered Responses:", len(filtered_df))
    st.dataframe(filtered_df)

    # Download
    st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_votes.csv")

    # Charts
    st.subheader("📈 Visual Summaries")

    def plot_bar(series, title):
        st.write(title)
        st.bar_chart(series.dropna().value_counts())

    def plot_pie(series, title):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        series = series.dropna()
        ax.pie(series.value_counts(), labels=series.value_counts().index, autopct='%1.1f%%')
        ax.set_title(title)
        st.pyplot(fig)

    def plot_line(df, title):
        st.write(title)
        timeline = df["timestamp"].dt.date.value_counts().sort_index()
        st.line_chart(timeline)

    plot_line(filtered_df, "🗓️ Vote Submissions Over Time")
    plot_pie(filtered_df["party"], "🧑 Party Preference")
    plot_pie(filtered_df["gender"], "⚖️ Gender Distribution")
    plot_bar(filtered_df["region"], "🌍 Regional Distribution")
    plot_bar(filtered_df["age"], "🎂 Age Distribution")
    plot_bar(filtered_df["trust_gecom"], "✅ Trust in GECOM")

    if "issues" in filtered_df.columns:
        st.write("📌 Top Issues")
        all_issues = filtered_df["issues"].dropna().str.split(", ").explode()
        plot_bar(all_issues, "Most Common Issues")

    st.write("🧾 Candidate Reasons")
    if "candidate" in filtered_df.columns and "candidate_reason" in filtered_df.columns:
        st.dataframe(filtered_df[["candidate", "candidate_reason"]].dropna())

    # PR System Opinions
    st.subheader("🗳️ PR System Opinions")
    pr_questions = [
        "pr_understand_system",
        "pr_understand_allocation",
        "prefer_individual_candidate",
        "satisfied_representation",
        "allow_coalition_negotiation",
        "require_majority_to_govern",
        "qualified_majority_to_govern"
    ]

    for q in pr_questions:
        if q in filtered_df.columns:
            plot_bar(filtered_df[q], q.replace('_', ' ').capitalize())

# Main Voting Page
if st.session_state.step == "email":
    st.title("Guyana Voters Pulse 🗳️")
    st.write("Enter your email to receive a one-time code to vote:")
    email = st.text_input("Email")
    if st.button("Send Code"):
        if has_email_already_voted(email, db):
            st.error("This email has already voted.")
        else:
            send_verification_code(email)
            st.session_state.email = email
            st.session_state.step = "verify"

elif st.session_state.step == "verify":
    st.write("Enter the code sent to your email:")
    code = st.text_input("Verification Code")
    if st.button("Verify"):
        if verify_code(st.session_state.email, code):
            st.session_state.step = "vote"
        else:
            st.error("Invalid code. Please try again.")

elif st.session_state.step == "vote":
    st.header("Your Vote")
    party = st.selectbox("Preferred Political Party", [
    "All America Alliance for Guyana (AAA4G)",
    "A Guyana National Service Party (AGNSP)",
    "A Partnership for National Unity (APNU)",
    "Assembly for Liberty and Prosperity (ALP)",
    "A New and United Guyana (ANUG)",
    "Citizen United (CU)",
    "Democratic Peoples Party (DPR)",
    "Destiny To Oneness (DTO)",
    "Guyanese for Accouuntability, Meritocracy, Equality, Reform, Inclusion and Collaboration with America (GAMERICA)",
    "Guyana Unity Party (GUP)",
    "Horizon and Star (HAS)",
    "Justice for All Party (JFAP)",
    "People's Progressive Party/Civic (PPP/C)",
    "The Citizenship Initiative (TCI)",
    "The New Movement (TNM)",
    "The Republic Party of Guyana (PRG)",
    "United Workers Party (UWP)",
    "Unity Guyana Democratic Party (UGDP)",
    "United Republican Party (URP)",
    "Unity Movement (UM)",
    "Unity One (UO)",
    "United Peoples Party (UPP)",
    "We Invest In Nationhood (WIN)",
    "Working People's Alliance (WPA)"
])
    candidate = st.text_input("Preferred Candidate (if any)")
    candidate_reason = st.text_area("Why did you choose this candidate?", placeholder="Explain your reason...")
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
        "Environment",
        "Political Stability",
        "Constitutional Reform",
        "Regional (rural/hinterland) Development",
        "Improved Utility Services (Electricity, Water)",
        "Improved Infrastructure",
        "Agriculture Development",
        "Sports Policy",
        "Cultural Policy",
        "Health Care"
    ]
)
    trust_gecom = st.radio("Do you trust GECOM to run a free and fair election?", ["Yes", "No", "Not sure"])
    age = st.selectbox("Age Group", ["18-24", "25-34", "35-44", "45-54", "55+"])
    gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
    region = st.selectbox("Region", ["Region 1", "Region 2", "Region 3", "Region 4", "Region 5", "Region 6", "Region 7", "Region 8", "Region 9", "Region 10"])

    st.header("🗳️ The List PR System")
    q1 = st.radio("Do you understand how the system works?", ["Yes", "No", "Not sure"])
    q2 = st.radio("Do you understand how seats are allocated?", ["Yes", "No", "Not sure"])
    q3 = st.radio("Would you prefer to vote for an individual candidate instead of a list?", ["Yes", "No", "Not sure"])
    q4 = st.radio("Are you satisfied with how your interests are represented in Parliament?", ["Yes", "No", "Not sure"])
    q5 = st.radio("Should parties be allowed to negotiate coalitions to form the government after elections (as happens everywhere else where PR is practised)?", ["Yes", "No", "Not sure"])
    q6 = st.radio("Should the achievement of a majority be a requirement to form the government (as is typical of List PR systems worldwide)?", ["Yes", "No", "Not sure"])
    q7 = st.radio("Should a qualified majority (support of 60+ percent of representatives) be required to form the government (as in Suriname where it is 67 percent)?", ["Yes", "No", "Not sure"])

    if st.button("Submit Vote"):
        device_id = get_device_id()
        if has_already_voted(device_id, db):
            st.error("This device has already voted.")
        else:
            vote = {
                "email": st.session_state.email,
                "party": party,
                "candidate": candidate,
                "candidate_reason": candidate_reason,
                "issues": ", ".join(issues),
                "trust_gecom": trust_gecom,
                "age": age,
                "gender": gender,
                "region": region,
                "pr_understand_system": q1,
                "pr_understand_allocation": q2,
                "prefer_individual_candidate": q3,
                "satisfied_representation": q4,
                "allow_coalition_negotiation": q5,
                "require_majority_to_govern": q6,
                "qualified_majority_to_govern": q7,
                "timestamp": datetime.datetime.now().isoformat(),
                "device_id": device_id
            }
            record_vote(vote, db)
            st.write("📤 Vote sent to Firebase:", vote)
            st.session_state.vote_submitted = True
            st.success("Thank you! Your vote has been recorded.")
            st.session_state.step = "done"

elif st.session_state.step == "done":
    st.header("🎉 Vote Submitted")
    st.write("Thank you for participating in the Guyana Voters Pulse!")
    st.balloons()
