import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred_path = os.getenv('FIREBASE_CREDENTIAL_PATH')
            if not cred_path:
                raise Exception("Environment variable FIREBASE_CREDENTIAL_PATH not set.")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully.")
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
