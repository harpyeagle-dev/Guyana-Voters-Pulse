import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def initialize_firebase():
    try:
        st.write("🔄 Initializing Firebase...")
        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": st.secrets["FIREBASE"]["type"],
                "project_id": st.secrets["FIREBASE"]["project_id"],
                "private_key_id": st.secrets["FIREBASE"]["private_key_id"],
                "private_key": st.secrets["FIREBASE"]["private_key"].replace("\\n", "\n"),
                "client_email": st.secrets["FIREBASE"]["client_email"],
                "client_id": st.secrets["FIREBASE"]["client_id"],
                "auth_uri": st.secrets["FIREBASE"]["auth_uri"],
                "token_uri": st.secrets["FIREBASE"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["FIREBASE"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["FIREBASE"]["client_x509_cert_url"]
            })
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["FIREBASE"]["database_url"]
            })
            st.success("✅ Firebase initialized.")
        return db
    except Exception as e:
        st.error("❌ Firebase initialization failed")
        st.exception(e)
        raise

# Initialize once and reuse
db = initialize_firebase()
