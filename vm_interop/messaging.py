"""
Messaging Console module for real-time chat between VMs using sockets.
"""

import socket
import threading

class MessagingConsole:
    def __init__(self):
        """Initialize MessagingConsole."""
        pass

    def start_server(self, port):
        """Start the messaging server on a given port."""
        pass

    def connect_client(self, vm_id, server_ip, port):
        """Connect a VM client to the messaging server."""
        pass

    def send_message(self, vm_id, message):
        """Send a message from a VM to the chat."""
        pass

    def receive_message(self, vm_id):
        """Receive a message for a VM from the chat."""
        pass 

class TCPServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=12345, on_message=None):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.on_message = on_message
        self._stop_event = threading.Event()
        self.server_socket = None

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            while not self._stop_event.is_set():
                self.server_socket.settimeout(1.0)
                try:
                    client_sock, addr = self.server_socket.accept()
                except socket.timeout:
                    continue
                except Exception:
                    break
                try:
                    data = client_sock.recv(4096)
                    if data and self.on_message:
                        self.on_message(addr, data.decode(errors='replace'))
                except Exception:
                    pass
                finally:
                    client_sock.close()
        except Exception as e:
            if self.on_message:
                self.on_message(('server', 'error'), f"Server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self):
        self._stop_event.set()
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

def send_message(ip, port, message, timeout=5):
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.sendall(message.encode())
        sock.close()
        return True, "Message sent"
    except socket.timeout:
        return False, "Connection timed out"
    except ConnectionRefusedError:
        return False, "Connection refused by remote host"
    except Exception as e:
        return False, f"Messaging failed: {e}"

def send_message_threaded(ip, port, message, callback, timeout=5):
    def worker():
        success, msg = send_message(ip, port, message, timeout)
        callback(success, msg)
    t = threading.Thread(target=worker, daemon=True)
    t.start() 