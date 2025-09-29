# -------------------------- udp_client.py --------------------------
import socket
import threading

class UDPClient:
    def __init__(self, server_host, server_port, username):
        self.server_host = server_host
        self.server_port = int(server_port)
        self.username = username
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        self.running = True

    def start(self):
        server = (self.server_host, self.server_port)
        self.sock.sendto(f"__register__:{self.username}".encode('utf-8'), server)
        print(f"[UDP Client] Registered with server {server} as {self.username}")
        threading.Thread(target=self.recv_loop, daemon=True).start()
        try:
            while self.running:
                line = input()
                if line.strip() == '/quit':
                    self.sock.sendto(b'/quit', server)
                    break
                self.sock.sendto(line.encode('utf-8'), server)
        finally:
            self.running = False
            self.sock.close()

    def recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                print('\r' + data.decode('utf-8') + '\n', end='')
            except socket.timeout:
                continue
            except Exception:
                break

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python udp_client.py host port username")
    else:
        UDPClient(sys.argv[1], sys.argv[2], sys.argv[3]).start()
