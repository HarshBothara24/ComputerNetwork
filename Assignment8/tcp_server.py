# -------------------------- tcp_server.py --------------------------
import socket
import threading
from common import timestamp

class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[TCP Server] Listening on {self.host}:{self.port}")
        try:
            while True:
                client_sock, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True).start()
        except KeyboardInterrupt:
            print('\n[TCP Server] Shutting down')
            self.server.close()

    def broadcast(self, msg, exclude_sock=None):
        with self.lock:
            for sock in list(self.clients.keys()):
                if sock is exclude_sock:
                    continue
                try:
                    sock.sendall(msg.encode('utf-8'))
                except Exception:
                    sock.close()
                    del self.clients[sock]

    def handle_client(self, client_sock, addr):
        try:
            client_sock.sendall(b'USERNAME?')
            username = client_sock.recv(1024).decode('utf-8').strip()
            if not username:
                username = f"{addr[0]}:{addr[1]}"
            with self.lock:
                self.clients[client_sock] = username
            self.broadcast(f"[Server] {username} joined the chat.")

            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8').strip()
                if text == '/quit':
                    break
                out = f"[{timestamp()}] {username}: {text}"
                print(out)
                self.broadcast(out, exclude_sock=client_sock)
        finally:
            with self.lock:
                username = self.clients.pop(client_sock, None)
            self.broadcast(f"[Server] {username or addr} left the chat.")
            client_sock.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python tcp_server.py host port")
    else:
        TCPServer(sys.argv[1], sys.argv[2]).start()

