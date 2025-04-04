import random
import datetime
import re
from firebase_config import db
import smtplib
from email.message import EmailMessage

def sanitize_key(email):
    return re.sub(r'[.#$\[\]/]', '_', email.split('@')[0])

def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    db.reference(f"/auth_codes/{key}").set({
        "code": code,
        "expiry": expiry
    })

def verify_code(email, input_code):
    key = sanitize_key(email)
    stored = db.reference(f"/auth_codes/{key}").get()

    if not stored:
        return False
    if stored.get("code") != input_code:
        return False

    return True
