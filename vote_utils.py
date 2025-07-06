# vote_utils.py
import re
import pandas as pd

# All functions now expect db to be passed in from app.py

def record_vote(data, db):
    email = data.get("email", "anonymous")
    key = re.sub(r'[.#$\[\]/]', '_', email)
    db.collection("votes").document(key).set(data)

def has_already_voted(device_id, db):
    votes = db.collection("votes").where("device_id", "==", device_id).stream()
    return any(True for _ in votes)

def has_email_already_voted(email, db):
    safe_email = re.sub(r'[.#$\[\]/]', '_', email)
    doc_ref = db.collection("votes").document(safe_email)
    return doc_ref.get().exists

def get_vote_stats(db):
    votes = get_vote_sheet(db)
    return {
        "total_votes": len(votes)
    }

def get_vote_sheet(db):
    votes_ref = db.collection("votes")
    docs = votes_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

def filter_votes_by_date(df, start_date, end_date):
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df[(df["timestamp"] >= pd.to_datetime(start_date)) & (df["timestamp"] <= pd.to_datetime(end_date))]

def get_field_distribution(df, field):
    return df[field].value_counts()
