import datetime
import streamlit as st
from firebase_config import db
from device_utils import get_device_id  # assumes you moved it to its own file

# ✅ Record a vote with device ID and timestamp
def record_vote(email, vote_option):
    device_id = get_device_id()
    vote_data = {
        "vote": vote_option,
        "device_id": device_id,
        "timestamp": datetime.datetime.now().isoformat()
    }
    sanitized_email = email.replace('.', '_')
    db.reference(f"/votes/{sanitized_email}").set(vote_data)

# 🔐 Check if this device has already voted
def has_already_voted():
    device_id = get_device_id()
    all_votes = db.reference("/votes").get() or {}
    for vote in all_votes.values():
        if vote.get("device_id") == device_id:
            return True
    return False

# 🔐 Check if this email has already voted
def has_email_already_voted(email):
    sanitized_email = email.replace('.', '_')
    return db.reference(f"/votes/{sanitized_email}").get() is not None

# 📊 Fetch current vote counts for a live dashboard
def get_vote_stats():
    all_votes = db.reference("/votes").get() or {}
    stats = {}
    for vote in all_votes.values():
        option = vote.get("vote")
        stats[option] = stats.get(option, 0) + 1
    return stats
