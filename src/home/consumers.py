import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LogEntryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("log_entries", self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("log_entries", self.channel_name)

    async def send_log_entry(self, event):
        log_message = event['message']
        await self.send(text_data=json.dumps(log_message))
