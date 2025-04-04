import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def initialize_firebase():
    try:
        st.write("🔄 Initializing firebase...")

        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": st.secrets["firebase"]["type"],
                "project_id": st.secrets["firebaseE"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
            })

            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase"]["database_url"]
            })

        # ✅ Test write
        db.reference("/debug_test").set({"status": "connected"})
        st.success("✅ firebase initialized and connected")
        return db

    except Exception as e:
        st.error("❌ firebase initialization failed")
        st.exception(e)
        raise

# ✅ Call it once and reuse
db = initialize_firebase()
