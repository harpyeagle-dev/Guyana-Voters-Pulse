import smtplib
from email.message import EmailMessage
from firebase_config import db
import datetime, random, re, streamlit as st

def sanitize_key(email):
    return re.sub(r'[.#$\[\]/]', '_', email.split('@')[0])

def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    try:
        # Save to firebase
        db.reference(f"/auth_codes/{key}").set({"code": code, "expiry": expiry})

        # Send the email
        msg = EmailMessage()
        msg["Subject"] = "Your Verification Code"
        msg["From"] = st.secrets["EMAIL"]["sender"]
        msg["To"] = email
        msg.set_content(f"Your verification code is: {code}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["EMAIL"]["sender"], st.secrets["EMAIL"]["app_password"])
            smtp.send_message(msg)

        st.success(f"✅ Verification code sent to {email}")

    except Exception as e:
        st.error("❌ Failed to send verification code")
        st.exception(e)

def verify_code(email, entered_code):
    key = sanitize_key(email)
    record = db.reference(f"/auth_codes/{key}").get()

    if not record:
        return False

    if record.get("code") != entered_code:
        return False

    expiry = datetime.datetime.fromisoformat(record["expiry"])
    if datetime.datetime.now() > expiry:
        return False

    return True
