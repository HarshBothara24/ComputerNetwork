# -------------------------- udp_server.py --------------------------
import socket
import threading
from common import timestamp

class UDPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        self.sock.bind((self.host, self.port))
        print(f"[UDP Server] Listening on {self.host}:{self.port}")
        try:
            while True:
                data, addr = self.sock.recvfrom(4096)
                text = data.decode('utf-8').strip()
                if text.startswith('__register__:'):
                    username = text.split(':', 1)[1]
                    with self.lock:
                        self.clients[addr] = username
                    self.relay(f"[Server] {username} joined (UDP).", exclude=addr)
                    continue
                if text == '/quit':
                    with self.lock:
                        name = self.clients.pop(addr, None)
                    self.relay(f"[Server] {name or addr} left (UDP).", exclude=addr)
                    continue
                with self.lock:
                    username = self.clients.get(addr, f"{addr[0]}:{addr[1]}")
                out = f"[{timestamp()}] {username}: {text}"
                print(out)
                self.relay(out, exclude=addr)
        finally:
            self.sock.close()

    def relay(self, msg, exclude=None):
        with self.lock:
            for addr in list(self.clients.keys()):
                if addr == exclude:
                    continue
                try:
                    self.sock.sendto(msg.encode('utf-8'), addr)
                except Exception:
                    self.clients.pop(addr, None)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python udp_server.py host port")
    else:
        UDPServer(sys.argv[1], sys.argv[2]).start()

