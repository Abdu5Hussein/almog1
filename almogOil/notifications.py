# notifications.py (or you can place this in views.py if preferred)

from firebase_admin import messaging

def send_order_tracking_notification(user_fcm_token, title, body):
    """
    Send an FCM notification to the client with the given title and body.
    """
    if not user_fcm_token:
        raise ValueError("User does not have a valid FCM token")

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user_fcm_token
    )
    
    try:
        response = messaging.send(message)
        return response
    except Exception as e:
        raise ValueError(f"Error sending notification: {str(e)}")
