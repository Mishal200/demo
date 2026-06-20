import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        action = data.get("action")

        # Typing Indicator
        if action == "typing":

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "username": data["username"],
                    "typing": data["typing"],
                }
            )
            return

        # Chat Message
        message = data["message"]
        sender_id = data["sender_id"]
        receiver_id = data["receiver_id"]

        # Save message in database
        await self.save_message(
            sender_id,
            receiver_id,
            message
        )

        username = await self.get_username(sender_id)

        # Send to everyone in room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "username": event["username"],
        }))

    async def typing_status(self, event):

        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "typing": event["typing"],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )

    @database_sync_to_async
    def get_username(self, user_id):

        return User.objects.get(id=user_id).username