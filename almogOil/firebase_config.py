import firebase_admin
from firebase_admin import credentials, messaging
from Almog1 import settings

cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

def send_firebase_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
    )
    response = messaging.send(message)
    print("Notification sent:", response)
