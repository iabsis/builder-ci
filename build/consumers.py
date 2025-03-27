import json
from .models import BuildTask, Build
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class LogsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.build_pk = self.scope["url_route"]["kwargs"]["build_pk"]
        self.room_group_name = f"logs_{self.build_pk}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        async for task in BuildTask.objects.filter(build=self.build_pk):
            await self.send(
                text_data=json.dumps({
                    "type": "task",
                    "action": "update_task",
                    "description": task.description,
                    "task": task.order,
                    "status": task.status,
                })
            )

        # build = await Build.objects.get(pk=self.build_pk)
        # await self.send(
        #     text_data=json.dumps({
        #         "type": "task",
        #         "action": "update_build",
        #         "info": {
        #             "status": build.status,
        #             "version": build.version,
        #             "started_at": build.started_at,
        #             "finished": build.finished,
        #         },
        #     })
        # )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def task(self, event):
        await self.send(text_data=json.dumps(event))