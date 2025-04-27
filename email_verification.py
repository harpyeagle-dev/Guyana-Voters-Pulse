import smtplib
from email.message import EmailMessage
import random
import datetime
import re
from firebase_config import db
import streamlit as st

def sanitize_key(email):
    return re.sub(r'[.#$\[\]/]', '_', email.split('@')[0])

def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    try:
        # Save code and expiry to Firebase
        db.reference(f"/auth_codes/{key}").set({
            "code": code,
            "expiry": expiry
        })

        # Send email
        msg = EmailMessage()
        msg["Subject"] = "Your Verification Code"
        msg["From"] = st.secrets["EMAIL"]["sender"]
        msg["To"] = email
        msg.set_content(f"Your verification code is: {code}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["EMAIL"]["sender"], st.secrets["EMAIL"]["app_password"])
            smtp.send_message(msg)

    except Exception as e:
        raise e

def verify_code(email, code_input):
    key = sanitize_key(email)
    record = db.reference(f"/auth_codes/{key}").get()

    if not record:
        return False

    saved_code = record.get("code")
    expiry = record.get("expiry")

    if saved_code == code_input and datetime.datetime.fromisoformat(expiry) > datetime.datetime.now():
        return True
    return False
