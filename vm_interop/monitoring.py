"""
Monitoring Dashboard module for real-time display of VM and network statistics.
"""

import socket
import json
import time
import psutil
import threading

class MonitoringDashboard:
    def __init__(self):
        """Initialize MonitoringDashboard."""
        pass

    def get_vm_uptime(self, vm_id):
        """Get uptime for a VM."""
        pass

    def get_open_ports(self, vm_id):
        """Get list of open ports for a VM."""
        pass

    def get_data_transfer(self, vm_id):
        """Get data transferred between VMs."""
        pass

    def get_resource_usage(self, vm_id):
        """Get CPU, memory, and network usage for a VM."""
        pass 

class MonitoringAgent(threading.Thread):
    def __init__(self, interval=5, on_stats=None):
        super().__init__(daemon=True)
        self.interval = interval
        self.on_stats = on_stats
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            stats = self.collect_stats()
            if self.on_stats:
                self.on_stats(stats)
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def collect_stats():
        # All psutil calls are lightweight and safe for background threads
        return {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }

def send_stats(ip, port, stats_dict):
    try:
        sock = socket.socket()
        sock.connect((ip, port))
        sock.sendall(json.dumps(stats_dict).encode())
        sock.close()
        return True
    except Exception as e:
        print(f"Send stats failed: {e}")
        return False

def agent_loop(ip, port):
    while True:
        stats = MonitoringAgent.collect_stats()
        send_stats(ip, port, stats)
        time.sleep(5) 