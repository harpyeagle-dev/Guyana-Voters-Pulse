import datetime
import pandas as pd
from firebase_config import db

# ✅ Record a vote with metadata
def record_vote(email, vote_option, device_id):
    key = email.replace(".", "_")
    db.reference(f"/votes/{key}").set({
        "vote": vote_option,
        "timestamp": datetime.datetime.now().isoformat(),
        "device_id": device_id
    })

# ✅ Check if a device ID has already voted
def has_already_voted(device_id):
    all_votes = db.reference("/votes").get() or {}
    return any(v.get("device_id") == device_id for v in all_votes.values())

# ✅ Check if an email has already voted
def has_email_already_voted(email):
    key = email.replace(".", "_")
    return db.reference(f"/votes/{key}").get() is not None

# ✅ Summarize votes by option
def get_vote_stats():
    all_votes = db.reference("/votes").get() or {}
    stats = {}
    for _, data in all_votes.items():
        vote = data.get("vote")
        if vote:
            stats[vote] = stats.get(vote, 0) + 1
    return stats

# ✅ Admin view of all votes
def get_vote_sheet():
    all_votes = db.reference("/votes").get() or {}
    rows = []
    for voter_key, data in all_votes.items():
        row = {
            "Voter": voter_key.replace("_", "."),
            "Vote": data.get("vote", ""),
            "Device ID": data.get("device_id", ""),
            "Timestamp": data.get("timestamp", "")
        }
        rows.append(row)
    return pd.DataFrame(rows)

# ✅ Filter votes between start and end dates
def filter_votes_by_date(start_date, end_date):
    df = get_vote_sheet()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    mask = (df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)
    return df[mask]

# ✅ Field distribution count (e.g., for Vote column)
def get_field_distribution(field_name):
    df = get_vote_sheet()
    if field_name in df.columns:
        return df[field_name].value_counts().to_dict()
    return {}
