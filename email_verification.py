# email_verification.py
import random
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta
from firebase_config import db
import streamlit as st

def send_verification_code(email):
    code = f"{random.randint(100000, 999999)}"
    expiry = datetime.utcnow() + timedelta(minutes=10)
    db.collection("auth_codes").document(email).set({"code": code, "expiry": expiry})

    msg = EmailMessage()
    msg["Subject"] = "Your Secure Voting Code"
    msg["From"] = st.secrets["email"]["username"]
    msg["To"] = email
    msg.set_content(f"Your 6-digit verification code is: {code}\nThis code expires in 10 minutes.")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(st.secrets["email"]["username"], st.secrets["email"]["password"])
        server.send_message(msg)

def verify_code(email, code):
    doc = db.collection("auth_codes").document(email).get()
    if doc.exists:
        data = doc.to_dict()
        if data["code"] == code and datetime.utcnow() < data["expiry"].replace(tzinfo=None):
            return True
    return False
