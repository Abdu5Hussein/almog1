import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Function to send WhatsApp messages using Green API
def send_whatsapp_message_via_green_api(to, message):
    # Green API URL
    url = "https://7105.api.greenapi.com/waInstance7105234156/sendMessage/66b95676d3344f3dbbbe3f6bcaa8faa3e5464f6109414ea990"
    
    # Prepare the payload
    payload = {
        "chatId": f"{to}@c.us",  # The recipient's chatId in the format: phoneNumber@c.us
        "message": message,      # The message you want to send
    }

    headers = {
        'Content-Type': 'application/json',  # Content type is JSON
    }

    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check for success or failure
    if response.status_code == 200:
        # Print the response if the request is successful
        print(response.text.encode('utf8'))
        return response.json()  # Return the response JSON if needed
    else:
        # Handle failure (optional)
        print(f"Error: {response.text}")
        return None
    
def send_excel_file_greenapi_upload(phone, filename, file_stream):
    url = "https://7105.media.greenapi.com/waInstance7105234156/sendFileByUpload/66b95676d3344f3dbbbe3f6bcaa8faa3e5464f6109414ea990"
    
    payload = {
        'chatId': f'{phone}@c.us'
    }

    files = {
        'file': (filename, file_stream, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }

    try:
        response = requests.post(url, data=payload, files=files)
        print(response.status_code, response.text)
        return response.status_code == 200
    except Exception as e:
        print(f"[❌ Upload Error] {e}")
        return False
