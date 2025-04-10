import firebase_admin
from firebase_admin import credentials
from decouple import Config, RepositoryEnv
import os

# Get environment variable from .env manually
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
config = Config(RepositoryEnv(env_file))

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred_path = config('FIREBASE_CREDENTIAL_PATH')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully.")
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
