from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def websocket_connect(self, message):
        pass

    def websocket_receive(self, message):
        pass

    def websocket_disconnect(self, message):
        pass
