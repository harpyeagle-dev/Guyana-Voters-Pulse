from firebase_config import db

try:
    db.reference("/connection_test").set({"status": "connected"})
    print("✅ Firebase Realtime DB connection successful!")
except Exception as e:
    print("❌ Firebase connection failed:", e)
