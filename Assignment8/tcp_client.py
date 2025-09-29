# -------------------------- tcp_client.py --------------------------
import socket
import threading
from common import timestamp

class TCPClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = int(port)
        self.username = username
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def start(self):
        self.sock.connect((self.host, self.port))
        banner = self.sock.recv(1024).decode('utf-8')
        if banner.strip() == 'USERNAME?':
            self.sock.sendall(self.username.encode('utf-8'))
        print(f"[TCP Client] Connected to {self.host}:{self.port} as {self.username}")
        threading.Thread(target=self.recv_loop, daemon=True).start()
        try:
            while self.running:
                line = input()
                if line.strip() == '/quit':
                    self.sock.sendall(b'/quit')
                    break
                self.sock.sendall(line.encode('utf-8'))
        finally:
            self.running = False
            self.sock.close()

    def recv_loop(self):
        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    break
                print('\r' + data.decode('utf-8') + '\n', end='')
        finally:
            self.running = False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python tcp_client.py host port username")
    else:
        TCPClient(sys.argv[1], sys.argv[2], sys.argv[3]).start()

