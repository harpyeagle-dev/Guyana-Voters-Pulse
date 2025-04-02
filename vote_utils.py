import streamlit as st
from firebase_config import db
import hashlib
import socket
import uuid
import pandas as pd
import datetime

# 🔍 Get the user's IP address
def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "unknown"

# 💻 Generate a simple device fingerprint
def get_device_id():
    # Combine IP + Streamlit session ID + user agent (if available)
    ip = get_ip_address()
    session_id = st.session_state.get("session_id", str(uuid.uuid4()))
    st.session_state["session_id"] = session_id
    raw_id = f"{ip}-{session_id}"
    return hashlib.sha256(raw_id.encode()).hexdigest()

# 🛡️ Check if this device/email has already voted
def has_already_voted(identifier):
    from fireside_config import db
    votes_ref = db.reference("/votes")
    votes_ref.set({"testuser": {"vote": "Option A"}})
    all_votes = ref.get()

    if not all_votes:
        return False

    for vote in all_votes.values():
        if vote.get("voter_id") == identifier:
            return True
    return False

# ✅ Submit a vote to Firebase
def submit_vote(choice, voter_id):
    vote_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    vote_data = {
        "vote_id": vote_id,
        "choice": choice,
        "timestamp": timestamp,
        "voter_id": voter_id
    }

    db.reference(f"/votes/{vote_id}").set(vote_data)
    return True

# 📊 Count votes by candidate
def get_vote_stats():
    votes_snapshot = db.reference("/votes").get()

    if not votes_snapshot:
        return pd.DataFrame(columns=["Candidate", "Votes"])

    vote_counts = {}
    for vote_id, vote_data in votes_snapshot.items():
        choice = vote_data.get("choice")
        vote_counts[choice] = vote_counts.get(choice, 0) + 1

    stats_df = pd.DataFrame(list(vote_counts.items()), columns=["Candidate", "Votes"])
    return stats_df.sort_values("Votes", ascending=False)
