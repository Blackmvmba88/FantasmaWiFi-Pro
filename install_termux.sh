#!/usr/bin/env bash
# FantasmaWiFi-Pro Termux/Android Installer Script
# This script installs FantasmaWiFi-Pro and its dependencies on Termux

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo ""
    echo -e "${MAGENTA}${BOLD}"
    echo "  ███████╗ █████╗ ███╗   ██╗████████╗ █████╗ ███████╗███╗   ███╗ █████╗"
    echo "  ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝████╗ ████║██╔══██╗"
    echo "  █████╗  ███████║██╔██╗ ██║   ██║   ███████║███████╗██╔████╔██║███████║"
    echo "  ██╔══╝  ██╔══██║██║╚██╗██║   ██║   ██╔══██║╚════██║██║╚██╔╝██║██╔══██║"
    echo "  ██║     ██║  ██║██║ ╚████║   ██║   ██║  ██║███████║██║ ╚═╝ ██║██║  ██║"
    echo "  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝"
    echo -e "${NC}"
    echo -e "${CYAN}          Termux/Android Installer${NC}"
    echo ""
}

# Print functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running in Termux
check_termux() {
    if [ ! -d "/data/data/com.termux" ]; then
        print_error "This script is for Termux only"
        print_info "Please run this script inside the Termux app"
        exit 1
    fi
    print_success "Running in Termux"
}

# Check storage permissions
check_storage_permission() {
    print_info "Checking storage permissions..."
    
    if [ -d "$HOME/storage" ]; then
        print_success "Storage access configured"
    else
        print_warning "Storage access not configured"
        read -p "Setup storage access now? (recommended) (Y/n) " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            termux-setup-storage
            print_success "Storage access configured"
            print_info "You may need to grant permissions in Android settings"
        fi
    fi
}

# Check root access
check_root() {
    print_info "Checking root access..."
    
    if su -c "id" &> /dev/null; then
        print_success "Root access available"
        HAS_ROOT=true
    else
        print_warning "Root access not available"
        print_info "Some features will be limited without root"
        HAS_ROOT=false
    fi
}

# Update packages
update_packages() {
    print_info "Updating Termux packages..."
    
    if pkg update -y && pkg upgrade -y; then
        print_success "Packages updated"
    else
        print_warning "Package update had issues (may be normal)"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    local packages=("python" "python-pip" "git")
    
    # Add iptables if root is available
    if [ "$HAS_ROOT" = true ]; then
        packages+=("iptables")
    fi
    
    for package in "${packages[@]}"; do
        print_info "Installing $package..."
        if pkg install -y "$package"; then
            print_success "$package installed"
        else
            print_error "Failed to install $package"
            exit 1
        fi
    done
}

# Install Python packages
install_fantasma() {
    print_info "Installing FantasmaWiFi-Pro..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install FantasmaWiFi-Pro
    if pip install fantasmawifi-pro; then
        print_success "FantasmaWiFi-Pro installed successfully"
    else
        print_error "Failed to install FantasmaWiFi-Pro"
        print_info "Trying alternative installation method..."
        
        # Try with --user flag
        if pip install --user fantasmawifi-pro; then
            print_success "FantasmaWiFi-Pro installed successfully"
        else
            print_error "Installation failed"
            exit 1
        fi
    fi
}

# Create convenience scripts
create_scripts() {
    print_info "Creating convenience scripts..."
    
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"
    
    # Create fantasma wrapper
    cat > "$bin_dir/fantasma" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python -m fantasma_cli "$@"
EOF
    chmod +x "$bin_dir/fantasma"
    
    # Create fantasma-web wrapper
    cat > "$bin_dir/fantasma-web" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python -m fantasma_web "$@"
EOF
    chmod +x "$bin_dir/fantasma-web"
    
    # Add to PATH if not already there
    if ! echo "$PATH" | grep -q "$bin_dir"; then
        echo "" >> "$HOME/.bashrc"
        echo "# FantasmaWiFi-Pro" >> "$HOME/.bashrc"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        print_info "Added to PATH. Restart Termux or run: source ~/.bashrc"
    fi
    
    print_success "Convenience scripts created"
}

# Configure wake lock (optional)
configure_wake_lock() {
    print_info ""
    read -p "Acquire wake lock (keep device awake)? (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if command -v termux-wake-lock &> /dev/null; then
            termux-wake-lock
            print_success "Wake lock acquired"
            print_info "Device will stay awake while Termux is running"
            print_info "Release with: termux-wake-unlock"
        else
            print_warning "termux-api not installed"
            print_info "Install with: pkg install termux-api"
        fi
    fi
}

# Show Android-specific tips
show_android_tips() {
    print_info ""
    print_info "${BOLD}Android-Specific Tips:${NC}"
    echo ""
    
    print_info "1. Battery Optimization:"
    echo "   Disable battery optimization for Termux in Android settings"
    echo "   to prevent the app from being killed"
    echo ""
    
    print_info "2. Permissions:"
    echo "   Grant all requested permissions for full functionality"
    echo ""
    
    print_info "3. Root Access:"
    if [ "$HAS_ROOT" = true ]; then
        echo "   Root access detected - full features available"
    else
        echo "   No root access - some features will be limited"
        echo "   Consider rooting your device for full functionality"
    fi
    echo ""
    
    print_info "4. Keep Screen On:"
    echo "   Use 'termux-wake-lock' to keep device awake"
    echo "   Useful when running as a WiFi hotspot"
    echo ""
    
    print_info "5. Background Execution:"
    echo "   Install termux:boot app to auto-start on device boot"
    echo ""
}

# Run diagnostics
run_diagnostics() {
    print_info "Running diagnostics..."
    echo ""
    
    if python -m fantasma_cli doctor; then
        print_success ""
        print_success "Installation complete!"
        print_info ""
        print_info "Quick Start:"
        print_info "  1. Run 'fantasma doctor' to check system"
        print_info "  2. Run 'fantasma list' to see network interfaces"
        print_info "  3. Run 'fantasma-web' to start Web UI"
        if [ "$HAS_ROOT" = true ]; then
            print_info "  4. Most commands require: su -c 'fantasma ...'"
        fi
        print_info ""
        print_info "Documentation: https://github.com/Blackmvmba88/FantasmaWiFi-Pro"
    else
        print_warning "Diagnostics completed with warnings"
        print_info "Some features may require additional setup or root access"
    fi
}

# Uninstall
uninstall() {
    show_banner
    
    print_warning "This will uninstall FantasmaWiFi-Pro"
    read -p "Continue? (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Uninstalling..."
        
        # Uninstall via pip
        pip uninstall -y fantasmawifi-pro
        
        # Remove convenience scripts
        rm -f "$HOME/.local/bin/fantasma"
        rm -f "$HOME/.local/bin/fantasma-web"
        
        print_success "FantasmaWiFi-Pro uninstalled"
    fi
}

# Main installation
main() {
    show_banner
    
    # Check Termux environment
    check_termux
    print_info ""
    
    # Check permissions and root
    check_storage_permission
    check_root
    print_info ""
    
    # Update packages
    update_packages
    print_info ""
    
    # Install dependencies
    install_dependencies
    print_info ""
    
    # Install FantasmaWiFi-Pro
    install_fantasma
    print_info ""
    
    # Create convenience scripts
    create_scripts
    
    # Optional wake lock
    configure_wake_lock
    
    # Show Android tips
    show_android_tips
    
    # Run diagnostics
    run_diagnostics
}

# Parse arguments
if [ "$1" == "uninstall" ] || [ "$1" == "--uninstall" ]; then
    uninstall
else
    main
fi

echo ""
