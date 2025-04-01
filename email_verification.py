import random
import datetime
from firebase_config import db

# 🔐 Send verification code to an email
def send_verification_code(email):
    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()

    key = email.replace(".", "_")  # Firebase keys can't contain dots

    db.reference(f"/auth_codes/{key}").set({
        "code": code,
        "expiry": expiry
    })

    # Placeholder: print to console (replace with email sending)
    print(f"Verification code sent to {email}: {code}")
    return code

# ✅ Verify a submitted code
def verify_code(email, submitted_code):
    key = email.replace(".", "_")
    record = db.reference(f"/auth_codes/{key}").get()

    if not record:
        return False

    code_matches = str(record.get("code")) == str(submitted_code)

    # Check expiry
    expiry_time = datetime.datetime.fromisoformat(record.get("expiry"))
    not_expired = expiry_time > datetime.datetime.now()

    return code_matches and not_expired
