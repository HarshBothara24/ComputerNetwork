import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import socket
import time

# Helper to add timestamps
def timestamp():
    return time.strftime("%H:%M:%S")

# =============== CLIENT BASE CLASS ===============
class BaseClient:
    def __init__(self, host, port, username, text_widget):
        self.host = host
        self.port = int(port)
        self.username = username
        self.text_widget = text_widget
        self.running = True

    def display(self, msg):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.yview(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def stop(self):
        self.running = False

# =============== TCP CLIENT ===============
class TCPClient(BaseClient):
    def __init__(self, host, port, username, text_widget):
        super().__init__(host, port, username, text_widget)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            banner = self.sock.recv(1024).decode('utf-8')
            if banner.strip() == 'USERNAME?':
                self.sock.sendall(self.username.encode('utf-8'))
            threading.Thread(target=self.recv_loop, daemon=True).start()
            self.display(f"[{timestamp()}] [TCP] Connected as {self.username}")
            return True
        except Exception as e:
            self.display(f"[Error] {e}")
            return False

    def send(self, msg):
        try:
            if msg.strip() == "/quit":
                self.sock.sendall(b"/quit")
                self.stop()
            else:
                self.sock.sendall(msg.encode('utf-8'))
                # ✅ Show your own message locally
                self.display(f"[{timestamp()}] You: {msg}")
        except:
            self.display("[TCP] Connection lost.")
            self.stop()

    def recv_loop(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self.display(f"[{timestamp()}] {data.decode('utf-8')}")
            except:
                break
        self.display(f"[{timestamp()}] [TCP] Disconnected")
        self.stop()

# =============== UDP CLIENT ===============
class UDPClient(BaseClient):
    def __init__(self, host, port, username, text_widget):
        super().__init__(host, port, username, text_widget)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        self.server = (self.host, self.port)

    def connect(self):
        try:
            reg_msg = f"__register__:{self.username}"
            self.sock.sendto(reg_msg.encode('utf-8'), self.server)
            threading.Thread(target=self.recv_loop, daemon=True).start()
            self.display(f"[{timestamp()}] [UDP] Registered as {self.username}")
            return True
        except Exception as e:
            self.display(f"[Error] {e}")
            return False

    def send(self, msg):
        try:
            if msg.strip() == "/quit":
                self.sock.sendto(b"/quit", self.server)
                self.stop()
            else:
                self.sock.sendto(msg.encode('utf-8'), self.server)
                # ✅ Show your own message locally
                self.display(f"[{timestamp()}] You: {msg}")
        except:
            self.display("[UDP] Error sending message")

    def recv_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                self.display(f"[{timestamp()}] {data.decode('utf-8')}")
            except socket.timeout:
                continue
            except:
                break
        self.display(f"[{timestamp()}] [UDP] Disconnected")
        self.stop()

# =============== GUI APP ===============
class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.client = None

        root.title("TCP/UDP Chat App")

        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Connection inputs
        ttk.Label(frm, text="Mode:").grid(row=0, column=0)
        self.mode = ttk.Combobox(frm, values=["TCP Client", "UDP Client"], state="readonly")
        self.mode.current(0)
        self.mode.grid(row=0, column=1)

        ttk.Label(frm, text="Host:").grid(row=1, column=0)
        self.host = ttk.Entry(frm)
        self.host.insert(0, "127.0.0.1")
        self.host.grid(row=1, column=1)

        ttk.Label(frm, text="Port:").grid(row=2, column=0)
        self.port = ttk.Entry(frm)
        self.port.insert(0, "12345")
        self.port.grid(row=2, column=1)

        ttk.Label(frm, text="Username:").grid(row=3, column=0)
        self.username = ttk.Entry(frm)
        self.username.insert(0, "User")
        self.username.grid(row=3, column=1)

        self.connect_btn = ttk.Button(frm, text="Connect", command=self.connect)
        self.connect_btn.grid(row=4, column=0, columnspan=2, pady=5)

        # Chat window
        self.chat = scrolledtext.ScrolledText(frm, width=50, height=15, state=tk.DISABLED)
        self.chat.grid(row=5, column=0, columnspan=2, pady=5)

        # Message entry
        self.msg_entry = ttk.Entry(frm, width=40)
        self.msg_entry.grid(row=6, column=0, pady=5)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ttk.Button(frm, text="Send", command=self.send_message)
        self.send_btn.grid(row=6, column=1, pady=5)

    def connect(self):
        mode = self.mode.get()
        host = self.host.get()
        port = self.port.get()
        username = self.username.get()

        if mode == "TCP Client":
            self.client = TCPClient(host, port, username, self.chat)
        else:
            self.client = UDPClient(host, port, username, self.chat)

        if self.client.connect():
            self.connect_btn.config(state=tk.DISABLED)

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.client:
            self.client.send(msg)
            self.msg_entry.delete(0, tk.END)

# =============== RUN APP ===============
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()
