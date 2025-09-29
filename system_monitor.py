#!/usr/bin/env python3
"""
System Health Monitor Daemon
Advanced system monitoring with persistence for educational purposes
"""

import os
import time
import json
import psutil
import socket
import logging
import subprocess
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
    
    def check_security_events(self):
        """Monitor security-related events"""
        try:
            # Check failed login attempts
            failed_logins = subprocess.run(
                ['grep', 'Failed password', '/var/log/auth.log'],
                capture_output=True, text=True
            )
            failed_count = len(failed_logins.stdout.splitlines()) if failed_logins.stdout else 0
            
            # Check sudo usage
            sudo_usage = subprocess.run(
                ['grep', 'sudo', '/var/log/auth.log'],
                capture_output=True, text=True
            )
            sudo_count = len(sudo_usage.stdout.splitlines()) if sudo_usage.stdout else 0
            
            security_info = {
                'failed_logins': failed_count,
                'sudo_commands': sudo_count,
                'timestamp': datetime.now().isoformat()
            }
            
            return security_info
            
        except Exception as e:
            self.logger.error(f"Error checking security events: {e}")
            return None
    
    def save_metrics_report(self, metrics, security_info):
        """Save metrics to JSON report"""
        try:
            report = {
                'system_metrics': metrics,
                'security_metrics': security_info,
                'report_time': datetime.now().isoformat()
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"{self.stealth_dir}/system_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"System report saved: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            return None
    
    def ensure_persistence(self):
        """Ensure the monitor continues running"""
        try:
            # Check if systemd service is running
            result = subprocess.run(
                ['systemctl', 'is-active', 'system-health-monitor.service'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self.logger.warning("Service not active - attempting to restart")
                subprocess.run(['systemctl', 'start', 'system-health-monitor.service'], 
                             capture_output=True)
                
        except Exception as e:
            self.logger.error(f"Error ensuring persistence: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting system health monitoring loop")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                security_info = self.check_security_events()
                
                if metrics and security_info:
                    # Save report
                    self.save_metrics_report(metrics, security_info)
                    
                    # Log summary
                    self.logger.info(
                        f"CPU: {metrics['cpu']['percent']}% | "
                        f"Memory: {metrics['memory']['percent']}% | "
                        f"Disk: {metrics['disk']['percent']}%"
                    )
                
                # Ensure persistence
                self.ensure_persistence()
                
                # Wait before next collection
                time.sleep(60)  # 1 minute
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retry

def main():
    """Main execution function"""
    # Fork to background if not already
    if os.fork() == 0:
        monitor = SystemHealthMonitor()
        monitor.ensure_directories()
        monitor.monitor_loop()

if __name__ == "__main__":
    main()
