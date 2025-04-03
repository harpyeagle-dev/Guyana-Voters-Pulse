from firebase_admin import credentials, initialize_app, db

cred = credentials.Certificate("serviceAccountKey.json")  # local downloaded key
initialize_app(cred, {
    'databaseURL': 'https://guyana-voters-pulse-default-rtdb.firebaseio.com'
})

ref = db.reference("/test_connection")
ref.set({"status": "connected"})
print("✅ Successfully wrote to Firebase!")
