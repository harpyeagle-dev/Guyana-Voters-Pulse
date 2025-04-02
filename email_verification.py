import random
import datetime
import re
from firebase_config import db

def sanitize_key(email):
    # Firebase keys can't contain . # $ [ ] /
    return re.sub(r'[.#$\[\]/]', '_', email.split('@')[0])

def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    try:
        db.reference(f"/auth_codes/{key}").set({
            "code": code,
            "expiry": expiry
        })
        print(f"✅ Verification code {code} set for {email}")
    except Exception as e:
        print(f"❌ Failed to write verification code for {email}: {e}")
        raise
