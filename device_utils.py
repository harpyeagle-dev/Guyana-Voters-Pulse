import hashlib
import uuid
import streamlit as st
import requests

def get_ip_address():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "unknown"

def get_device_id():
    ip = get_ip_address()
    session_id = st.session_state.get("session_id", str(uuid.uuid4()))
    st.session_state["session_id"] = session_id
    raw_id = f"{ip}-{session_id}"
    return hashlib.sha256(raw_id.encode()).hexdigest()
