# vote_utils.py
import re

def record_vote(data, db):
    email = data.get("email", "anonymous")
    key = re.sub(r'[.#$\[\]/]', '_', email)
    db.collection("votes").document(key).set(data)

# Stub functions (you likely have these defined elsewhere in full)
def has_already_voted(device_id):
    return False

def has_email_already_voted(email):
    return False

def get_vote_stats():
    return {}

def get_vote_sheet():
    from firebase_admin import firestore
    db = firestore.client()
    votes_ref = db.collection("votes")
    docs = votes_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)[]

def filter_votes_by_date(df, start_date, end_date):
    return df

def get_field_distribution(df, field):
    return df[field].value_counts()
