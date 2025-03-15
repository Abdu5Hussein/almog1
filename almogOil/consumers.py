import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Use 'user_id' since that's what your URL routing provides.
        self.user_id = self.scope["url_route"]["kwargs"].get("user_id")
        if not self.user_id:
            # Close connection if no user_id provided
            await self.close()
            return

        self.room_group_name = f'user_{self.user_id}'
        # Add this connection to the user-specific group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Check if room_group_name is set before attempting to leave the group.
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        # Broadcast the message to the group.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_notification',
                'message': message
            }
        )

    async def send_notification(self, event):
        message = event['message']
        # Send the message to the WebSocket client.
        await self.send(text_data=json.dumps({
            'message': message
        }))
