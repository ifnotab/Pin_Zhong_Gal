import socket
import threading
import json

class NetworkManager:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_host = False
        self.clients = []
    
    def host_game(self, port=5555):
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen()
        self.is_host = True
        threading.Thread(target=self.accept_connections, daemon=True).start()
    
    def join_game(self, ip, port=5555):
        self.socket.connect((ip, port))
        threading.Thread(target=self.receive_data, daemon=True).start()
    
    def accept_connections(self):
        while True:
            try:
                client, addr = self.socket.accept()
                self.clients.append(client)
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except:
                break
    
    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.process_message(message)
            except:
                break
    
    def receive_data(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.process_message(message)
            except:
                break
    
    def send_message(self, message_type, content, target=None):
        message = {
            'type': message_type,
            'content': content
        }
        data = json.dumps(message).encode()
        
        if self.is_host and target:
            target.send(data)
        elif self.is_host and not target:
            for client in self.clients:
                client.send(data)
        else:
            self.socket.send(data)
    
    def process_message(self, message):
        # 由具体游戏实现
        pass
    
    def close(self):
        self.socket.close()
        if self.is_host:
            for client in self.clients:
                client.close()
