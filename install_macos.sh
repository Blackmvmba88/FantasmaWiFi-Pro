#!/bin/bash
# FantasmaWiFi-Pro macOS Installer Script
# This script installs FantasmaWiFi-Pro and its dependencies on macOS

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
    echo -e "${CYAN}          macOS Installer${NC}"
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

# Check if running on macOS
check_macos() {
    if [[ "$(uname)" != "Darwin" ]]; then
        print_error "This script is for macOS only"
        exit 1
    fi
    print_success "Running on macOS"
}

# Check Python installation
check_python() {
    print_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        print_info "Found Python $PYTHON_VERSION"
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
            print_success "Python version OK"
            return 0
        else
            print_warning "Python 3.7 or later is required"
            return 1
        fi
    else
        print_warning "Python 3 not found"
        return 1
    fi
}

# Install Homebrew if needed
install_homebrew() {
    if command -v brew &> /dev/null; then
        print_success "Homebrew is already installed"
        return 0
    fi
    
    print_info "Homebrew is required but not installed"
    read -p "Install Homebrew now? (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        
        print_success "Homebrew installed"
        return 0
    else
        print_info "Installation cancelled"
        exit 0
    fi
}

# Install Python via Homebrew
install_python() {
    print_info "Installing Python 3 via Homebrew..."
    
    if ! brew install python3; then
        print_error "Failed to install Python"
        exit 1
    fi
    
    print_success "Python 3 installed"
}

# Install pip packages
install_fantasma() {
    print_info "Installing FantasmaWiFi-Pro..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install FantasmaWiFi-Pro
    if python3 -m pip install fantasmawifi-pro; then
        print_success "FantasmaWiFi-Pro installed successfully"
    else
        print_error "Failed to install FantasmaWiFi-Pro"
        exit 1
    fi
}

# Create launch agent (optional)
create_launch_agent() {
    print_info ""
    read -p "Create menu bar application (launch at login)? (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        AGENT_PLIST="$HOME/Library/LaunchAgents/com.fantasmawifi.agent.plist"
        
        # Get Python and script paths
        PYTHON_PATH=$(which python3)
        FANTASMA_PATH=$(python3 -c "import sys; print(sys.prefix)")/bin/fantasma-web
        
        # Create launch agent plist
        cat > "$AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fantasmawifi.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$FANTASMA_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/FantasmaWiFi/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/FantasmaWiFi/stderr.log</string>
</dict>
</plist>
EOF
        
        # Create log directory
        mkdir -p "$HOME/Library/Logs/FantasmaWiFi"
        
        print_success "Launch agent created"
        print_info "To start: launchctl load $AGENT_PLIST"
        print_info "To stop: launchctl unload $AGENT_PLIST"
    fi
}

# Create command alias (optional)
create_alias() {
    print_info ""
    read -p "Add 'fantasma' alias to your shell? (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        SHELL_RC=""
        
        # Detect shell
        if [[ "$SHELL" == *"zsh"* ]]; then
            SHELL_RC="$HOME/.zshrc"
        elif [[ "$SHELL" == *"bash"* ]]; then
            SHELL_RC="$HOME/.bash_profile"
        fi
        
        if [ -n "$SHELL_RC" ]; then
            echo "" >> "$SHELL_RC"
            echo "# FantasmaWiFi-Pro aliases" >> "$SHELL_RC"
            echo "alias fantasma='python3 -m fantasma_cli'" >> "$SHELL_RC"
            echo "alias fantasma-web='python3 -m fantasma_web'" >> "$SHELL_RC"
            
            print_success "Aliases added to $SHELL_RC"
            print_info "Restart your terminal or run: source $SHELL_RC"
        fi
    fi
}

# Run diagnostics
run_diagnostics() {
    print_info ""
    print_info "Running diagnostics..."
    echo ""
    
    if python3 -m fantasma_cli doctor; then
        print_success ""
        print_success "Installation complete!"
        print_info ""
        print_info "Quick Start:"
        print_info "  1. Run 'fantasma doctor' to check system"
        print_info "  2. Run 'fantasma list' to see network interfaces"
        print_info "  3. Run 'fantasma-web' to start Web UI"
        print_info ""
        print_info "Documentation: https://github.com/Blackmvmba88/FantasmaWiFi-Pro"
    else
        print_warning "Diagnostics completed with warnings"
        print_info "Some features may require additional setup"
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
        python3 -m pip uninstall -y fantasmawifi-pro
        
        # Remove launch agent if exists
        AGENT_PLIST="$HOME/Library/LaunchAgents/com.fantasmawifi.agent.plist"
        if [ -f "$AGENT_PLIST" ]; then
            launchctl unload "$AGENT_PLIST" 2>/dev/null || true
            rm "$AGENT_PLIST"
            print_success "Removed launch agent"
        fi
        
        print_success "FantasmaWiFi-Pro uninstalled"
    fi
}

# Main installation
main() {
    show_banner
    
    # Check macOS
    check_macos
    print_info ""
    
    # Check/Install Python
    if ! check_python; then
        install_homebrew
        install_python
        print_info ""
    fi
    
    # Install FantasmaWiFi-Pro
    install_fantasma
    
    # Optional setup
    create_launch_agent
    create_alias
    
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
