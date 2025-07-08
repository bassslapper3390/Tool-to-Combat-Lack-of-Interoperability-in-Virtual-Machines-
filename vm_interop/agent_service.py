"""
Agent Service module to be run inside each VM for file transfer, messaging, and monitoring.
Ensures resource monitoring is lightweight and efficient.
"""

import time
import psutil

class AgentService:
    def __init__(self):
        self.running = False

    def start(self):
        """Start the agent service (file transfer, messaging, monitoring)."""
        self.running = True
        # Example: Start lightweight monitoring loop
        while self.running:
            stats = self.report_metrics()
            # Send stats to main tool (stub)
            time.sleep(5)  # Sleep to avoid busy loop

    def stop(self):
        """Stop the agent service."""
        self.running = False

    def handle_file_transfer(self):
        """Handle file transfer requests."""
        pass

    def handle_messaging(self):
        """Handle messaging requests."""
        pass

    def report_metrics(self):
        """Report monitoring metrics to the main tool. Lightweight, uses psutil."""
        stats = {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
        return stats 