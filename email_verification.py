import requests

def send_verification_code(email):
    import datetime, random, re

    code = str(random.randint(100000, 999999))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    key = sanitize_key(email)

    try:
        # Save to Firebase
        db.reference(f"/auth_codes/{key}").set({
            "code": code,
            "expiry": expiry
        })

        # Send with Resend API
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
