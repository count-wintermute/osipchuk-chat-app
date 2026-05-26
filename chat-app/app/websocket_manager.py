class WebSocketManager:
    def __init__(self):
        self.connections = {}
    
    def add_connection(self, websocket, room_id):
        self.connections[room_id] = websocket
    
    def remove_connection(self, room_id):
        if room_id in self.connections:
            del self.connections[room_id]
    
    def broadcast(self, room_id, message):
        if room_id in self.connections:
            self.connections[room_id].send_json(message)
