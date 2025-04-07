import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from vote_utils import get_vote_sheet, filter_votes_by_date


def show_dashboard():
    st.header("📊 Live Voter Dashboard")

    df = get_vote_sheet()

    if df.empty:
        st.warning("No votes yet.")
        return

    # 📆 Filter by date
    start = st.date_input("Start Date", value=pd.Timestamp.today().date())
    end = st.date_input("End Date", value=pd.Timestamp.today().date())
    filtered = filter_votes_by_date(start, end)

    st.markdown(f"### 📈 Showing {len(filtered)} responses from {start} to {end}")

    # 🟢 Preferred Party
    if "Vote" in filtered.columns:
        st.subheader("Preferred Party")
        st.bar_chart(filtered["Vote"].value_counts())

    # 👤 Candidate
    if "Candidate" in filtered.columns:
        st.subheader("Preferred Candidate")
        st.bar_chart(filtered["Candidate"].value_counts())
    else:
        st.info("No candidate data available yet.")

    # 🎯 Reason (shown as a table)
    if "Reason" in filtered.columns:
        st.subheader("Reasons Given")
        st.dataframe(filtered["Reason"].dropna(), use_container_width=True)

    # 🔥 Issues (multi-select support)
    if "Issues" in filtered.columns:
        issues_flat = filtered.explode("Issues")
        st.subheader("Top Issues")
        st.bar_chart(issues_flat["Issues"].value_counts())

    # 👥 Demographics
    if "Age" in filtered.columns:
        st.subheader("Age Distribution")
        st.bar_chart(filtered["Age"].value_counts())

    if "Gender" in filtered.columns:
        st.subheader("Gender Distribution")
        st.bar_chart(filtered["Gender"].value_counts())

    if "Region" in filtered.columns:
        st.subheader("Region Breakdown")
        st.bar_chart(filtered["Region"].value_counts())

    # ✅ Trust in GECOM
    if "Trust in GECOM" in filtered.columns:
        st.subheader("Trust in GECOM")
        st.bar_chart(filtered["Trust in GECOM"].value_counts())

    # 📥 Download option
    st.download_button("📥 Download Data as CSV", filtered.to_csv(index=False), "votes.csv", "text/csv")
