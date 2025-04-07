import smtplib
from email.message import EmailMessage
from firebase_config import db
import datetime, random, re, streamlit as st


def sanitize_key(email):
    return re.sub(r"[.#$\\[\\]/]", "_", email.split("@")[0])


def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    try:
        # ✅ Save code to Firebase
        db.reference(f"/auth_codes/{key}").set({
            "code": code,
            "expiry": expiry
        })

        # ✅ Send email
        msg = EmailMessage()
        msg["Subject"] = "🗳️ Your Voting Verification Code"
        msg["From"] = st.secrets["EMAIL"]["sender"]
        msg["To"] = email
        msg.set_content(f"Your verification code is: {code}\n\nThis code will expire in 10 minutes.")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["EMAIL"]["sender"], st.secrets["EMAIL"]["app_password"])
            smtp.send_message(msg)

        st.success(f"📨 Verification code sent to {email}")

    except Exception as e:
        st.error("❌ Failed to send verification code")
        st.exception(e)
