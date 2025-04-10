import datetime, random, re, requests, streamlit as st
from firebase_config import db

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

        # ✅ Send via Resend
        payload = {
            "from": st.secrets["RESEND"]["sender"],
            "to": [email],
            "subject": "🗳️ Your Voting Verification Code",
            "text": f"Your code is: {code}\nIt expires in 10 minutes."
        }

        headers = {
            "Authorization": f"Bearer {st.secrets['RESEND']['api_key']}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.resend.com/emails", json=payload, headers=headers)

        if response.status_code == 200:
            st.success(f"📨 Code sent to {email} via Resend")
        else:
            st.error(f"❌ Resend error: {response.status_code}")
            st.write(response.json())

    except Exception as e:
        st.error("❌ Failed to send verification code")
        st.exception(e)

def verify_code(email, input_code):
    key = sanitize_key(email)

    try:
        record = db.reference(f"/auth_codes/{key}").get()
        if not record:
            return False

        expected = record.get("code")
        expiry = record.get("expiry")

        if not expected or not expiry:
            return False

        now = datetime.datetime.now()
        expiry_time = datetime.datetime.fromisoformat(expiry)

        if now > expiry_time:
            db.reference(f"/auth_codes/{key}").delete()
            return False

        if input_code == expected:
            db.reference(f"/auth_codes/{key}").delete()
            return True

        return False

    except Exception as e:
        print(f"❌ Verification failed for {email}: {e}")
        return False
