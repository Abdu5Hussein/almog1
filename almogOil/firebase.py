import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase with the credentials file
cred = credentials.Certificate('/home/django/almog1/almogoilerpsys-firebase-adminsdk-fbsvc-703c84bd48.json')
firebase_admin.initialize_app(cred)

# Function to send push notifications via Firebase Cloud Messaging
def send_firebase_notification(token, title, body):
    # Create a message to send
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token  # The FCM token of the client device
    )
    
    try:
        # Send the notification
        response = messaging.send(message)
        print("Successfully sent message:", response)
        return response
    except Exception as e:
        print("Error sending message:", e)
        raise e
