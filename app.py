import streamlit as st
st.set_page_config(page_title="Elections 2025 Opinion Poll", layout="wide")

st.title("🔍 Streamlit Secrets Debug")

st.write("Top-level keys:", list(st.secrets.keys()))
st.write("Raw secrets:", dict(st.secrets))
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

st.title("🗳️ Elections 2025 Voter Opinion Poll")

tab1, tab2, tab3 = st.tabs(["📋 Poll", "📊 Results", "🛠️ Admin"])

with tab1:
    st.header("🗳️ Cast Your Opinion")
    email = st.text_input("Email (optional)")
    candidate = st.radio("Preferred Candidate", ["Candidate A", "Candidate B", "Undecided"])
    issue = st.selectbox("Top Issue", ["Economy", "Healthcare", "Education", "Security"])
    will_vote = st.selectbox("Will you vote in 2025?", ["Yes", "No"])
    age_group = st.selectbox("Age Range", ["18–25", "26–40", "41–60", "60+"])

    if st.button("Submit Response"):
        if has_already_voted() or (email and has_email_already_voted(email)):
            st.warning("⚠️ You've already participated in this poll.")
        else:
            response = {
                "vote": candidate,
                "issue": issue,
                "will_vote": will_vote,
                "age_group": age_group
            }
            record_vote(email or f"anonymous_{get_device_id()[:8]}", response)
            st.success("✅ Your response has been recorded!")

with tab2:
    st.header("📊 Poll Results")

    st.subheader("🧮 Vote Counts")
    vote_stats = get_vote_stats()
    if vote_stats:
        st.bar_chart(vote_stats)

    st.subheader("📌 Top Issues")
    issue_stats = get_vote_stats("issue")
    if issue_stats:
        st.bar_chart(issue_stats)

    st.subheader("👥 Age Group Breakdown")
    age_stats = get_field_distribution("age_group")
    if age_stats:
        st.bar_chart(age_stats)

    st.subheader("🗳️ Will You Vote in 2025?")
    will_vote_stats = get_field_distribution("will_vote")
    if will_vote_stats:
        st.bar_chart(will_vote_stats)

with tab3:
    st.header("🛠️ Admin View")
    admin_key = st.text_input("Admin Password", type="password")

    if admin_key == st.secrets.get("ADMIN_KEY", "changeme"):
        df = get_vote_sheet()
        st.subheader("📋 Full Poll Data")
        st.dataframe(df, use_container_width=True)

        st.subheader("📆 Filter by Date")
        start_date = st.date_input("Start Date", datetime.date.today())
        end_date = st.date_input("End Date", datetime.date.today())

        if st.button("Apply Filter"):
            filtered_df = filter_votes_by_date(start_date, end_date)
            st.dataframe(filtered_df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download All Responses", data=csv, file_name="elections_2025_poll_data.csv")
    else:
        st.warning("🔐 Enter admin password to view full results.")
