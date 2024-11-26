import json

from channels.generic.websocket import AsyncWebsocketConsumer


class LogsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.build_pk = self.scope["url_route"]["kwargs"]["build_pk"]
        self.room_group_name = f"logs_{self.build_pk}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        await self.send(text_data=json.dumps({"message": "Hello !"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def log_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            'message': message
        }))