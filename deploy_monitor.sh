#!/bin/bash
#
# System Monitor Deployment Script
# Deploys monitoring system to target machine
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
INSTALL_DIR="/usr/lib/systemd/system-monitor"
SERVICE_NAME="system-health-monitor"

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check root access
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for full deployment"
        exit 1
    fi
    
    log_info "Prerequisites satisfied"
}

setup_environment() {
    log_info "Setting up monitoring environment..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "/etc/system-monitor"
    mkdir -p "/var/log/system-monitor"
    
    # Set permissions
    chmod 755 "$INSTALL_DIR"
    chmod 644 "/var/log/system-monitor"
    
    log_info "Environment setup completed"
}

install_monitoring_files() {
    log_info "Installing monitoring files..."
    
    # Copy Python scripts
    cp system_monitor.py "$INSTALL_DIR/"
    cp network_monitor.py "$INSTALL_DIR/"
    cp quick_recon.py "$INSTALL_DIR/"
    
    # Set executable permissions
    chmod +x "$INSTALL_DIR/system_monitor.py"
    chmod +x "$INSTALL_DIR/network_monitor.py"
    chmod +x "$INSTALL_DIR/quick_recon.py"
    
    # Create configuration
    cat > "$INSTALL_DIR/config.json" << EOF
{
    "monitoring": {
        "interval_seconds": 60,
        "log_retention_days": 30,
        "report_directory": "$INSTALL_DIR/reports"
    },
    "alerts": {
        "cpu_threshold": 90,
        "memory_threshold": 85,
        "disk_threshold": 80
    }
}
EOF

    log_info "Monitoring files installed"
}

setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    # Create service file
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=System Health Monitoring Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_DIR/system_monitor.py
Restart=always
RestartSec=30
User=root
Group=root
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    
    log_info "Systemd service configured"
}

setup_cron_backup() {
    log_info "Setting up cron backup..."
    
    # Add cron job for redundancy
    CRON_JOB="*/5 * * * * /usr/bin/python3 $INSTALL_DIR/system_monitor.py >> /var/log/system-monitor/cron.log 2>&1"
    
    # Add to root's crontab
    (crontab -l 2>/dev/null | grep -v "$INSTALL_DIR" ; echo "$CRON_JOB") | crontab -
    
    log_info "Cron backup configured"
}

start_services() {
    log_info "Starting monitoring services..."
    
    # Start systemd service
    systemctl start "$SERVICE_NAME.service"
    
    # Verify service is running
    if systemctl is-active --quiet "$SERVICE_NAME.service"; then
        log_info "Monitoring service is now running"
    else
        log_error "Failed to start monitoring service"
        systemctl status "$SERVICE_NAME.service"
    fi
}

show_status() {
    log_info "=== Deployment Status ==="
    echo "Installation Directory: $INSTALL_DIR"
    echo "Service Name: $SERVICE_NAME"
    echo "Service Status: $(systemctl is-active $SERVICE_NAME.service)"
    echo "Log Directory: /var/log/system-monitor"
    echo ""
    echo "To view logs: journalctl -u $SERVICE_NAME.service -f"
    echo "To stop service: systemctl stop $SERVICE_NAME.service"
    echo "To disable: systemctl disable $SERVICE_NAME.service"
}

main() {
    log_info "Starting System Monitor Deployment..."
    
    check_prerequisites
    setup_environment
    install_monitoring_files
    setup_systemd_service
    setup_cron_backup
    start_services
    show_status
    
    log_info "Deployment completed successfully!"
}

# Run main function
main "$@"
