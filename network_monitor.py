#!/usr/bin/env python3
"""
Network Monitor - Legitimate network traffic monitoring
Educational purposes only
"""

import socket
import time
import json
import psutil
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        self.monitor_dir = "/usr/lib/systemd/system-monitor"
        self.setup_environment()
        
    def setup_environment(self):
        """Setup monitoring environment"""
        import os
        os.makedirs(self.monitor_dir, exist_ok=True)
        
    def monitor_network_traffic(self):
        """Monitor network traffic and connections"""
        try:
            # Get network statistics
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()
            
            # Analyze connections
            listening_ports = []
            established_conns = []
            
            for conn in connections:
                if conn.status == 'LISTEN':
                    listening_ports.append({
                        'port': conn.laddr.port,
                        'family': conn.family.name
                    })
                elif conn.status == 'ESTABLISHED':
                    established_conns.append({
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                        'family': conn.family.name
                    })
            
            traffic_report = {
                'timestamp': datetime.now().isoformat(),
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'listening_ports': listening_ports,
                'established_connections': established_conns[:10],  # First 10
                'total_connections': len(connections)
            }
            
            return traffic_report
            
        except Exception as e:
            print(f"Network monitoring error: {e}")
            return None
    
    def save_network_report(self, report):
        """Save network report to file"""
        try:
            if report:
                filename = f"{self.monitor_dir}/network_report_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                return filename
        except Exception as e:
            print(f"Error saving network report: {e}")
        return None
    
    def run_monitoring(self):
        """Main monitoring loop"""
        print("Starting network traffic monitoring...")
        
        while True:
            try:
                # Monitor network
                report = self.monitor_network_traffic()
                
                if report:
                    # Save report
                    filename = self.save_network_report(report)
                    if filename:
                        print(f"Network report saved: {filename}")
                
                # Wait before next scan
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("Network monitoring stopped")
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.run_monitoring()
