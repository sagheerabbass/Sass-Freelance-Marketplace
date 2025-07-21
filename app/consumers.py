import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Jobs, Messages, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.room_group_name = f"chat_job_{self.job_id}"
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ) 
        print("🔥 Connected to WebSocket!")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            sender_username = data.get('username')

            if message and sender_username:
                print("Received message from frontend:", message)
                await self.save_message(sender_username, self.job_id, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': sender_username,
                    }
                )
        except Exception as e:
            print("Error in receive():", str(e))

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
            }))
        except Exception as e:
            print("Error in chat_message():", str(e))

    @database_sync_to_async
    def save_message(self, sender_username, job_id, message):
        try:
            sender = User.objects.get(username=sender_username)
            job = Jobs.objects.get(id=job_id)

            # Determine receiver
            receiver = job.freelancer if sender != job.freelancer else User.objects.filter(is_superuser=True).first()

            Messages.objects.create(
                sender=sender,
                receiver=receiver,
                job=job,
                content=message,
            )
            print(f"Message saved: '{message}' from {sender} to {receiver} for job {job}")
        except Exception as e:
            print("Error saving message to DB:", str(e))
