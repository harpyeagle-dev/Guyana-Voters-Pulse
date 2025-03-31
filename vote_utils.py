# vote_utils.py
import requests
from datetime import datetime
from firebase_config import db
import pandas as pd
import uuid

def get_ip_address():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "unknown"

def get_device_id(cookies):
    if cookies.get("device_id") is None:
        cookies["device_id"] = str(uuid.uuid4())
        cookies.save()
    return cookies.get("device_id")

def has_already_voted(email, ip, device_id):
    query = db.collection("votes")
    matches = query.where("email", "==", email).stream()
    for m in matches:
        return True
    matches = query.where("ip", "==", ip).stream()
    for m in matches:
        return True
    matches = query.where("device_id", "==", device_id).stream()
    for m in matches:
        return True
    return False

def submit_vote(email, vote, ip, device_id):
    db.collection("votes").add({
        "email": email,
        "vote": vote,
        "ip": ip,
        "device_id": device_id,
        "timestamp": datetime.utcnow()
    })

def get_vote_stats():
    votes = db.collection("votes").stream()
    vote_list = [v.to_dict()["vote"] for v in votes if v.exists and "vote" in v.to_dict()]
    if not vote_list:
        return pd.DataFrame()
    return pd.DataFrame(vote_list, columns=["option"]).value_counts().reset_index(name="count")
