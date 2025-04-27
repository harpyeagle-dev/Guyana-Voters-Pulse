import datetime
import pandas as pd
import re
from firebase_config import db

def record_vote(email, data, device_id=None):
    key = re.sub(r'[.#$\[\]/]', '_', email)
    db.reference(f"/votes/{key}").set(data)

def has_already_voted(device_id):
    votes = db.reference("/votes").get() or {}
    for vote in votes.values():
        if vote.get("device_id") == device_id:
            return True
    return False

def has_email_already_voted(email):
    key = re.sub(r'[.#$\[\]/]', '_', email)
    return db.reference(f"/votes/{key}").get() is not None

def get_vote_stats():
    votes = db.reference("/votes").get() or {}
    vote_counts = {}
    for data in votes.values():
        option = data.get("Vote", "Unknown")
        vote_counts[option] = vote_counts.get(option, 0) + 1
    return vote_counts

def get_vote_sheet():
    all_votes = db.reference("/votes").get() or {}
    rows = []
    for voter_key, data in all_votes.items():
        row = {
            "Voter": voter_key.replace("_", "."),
            "Device ID": data.get("device_id", ""),
            "Timestamp": data.get("timestamp", "")
        }
        row.update({k: v for k, v in data.items() if k not in row})
        rows.append(row)
    return pd.DataFrame(rows)

def filter_votes_by_date(start_date, end_date):
    df = get_vote_sheet()
    if "Timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        return df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]
    return df

def get_field_distribution(field_name):
    df = get_vote_sheet()
    if field_name in df:
        return df[field_name].value_counts()
    return {}
