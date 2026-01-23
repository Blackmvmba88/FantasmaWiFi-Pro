# FantasmaWiFi-Pro Windows Installer Script
# This script installs FantasmaWiFi-Pro and its dependencies on Windows

param(
    [switch]$Uninstall,
    [switch]$SkipPython
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Fail { Write-Host $args -ForegroundColor Red }

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "  ███████╗ █████╗ ███╗   ██╗████████╗ █████╗ ███████╗███╗   ███╗ █████╗" -ForegroundColor Magenta
    Write-Host "  ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝████╗ ████║██╔══██╗" -ForegroundColor Magenta
    Write-Host "  █████╗  ███████║██╔██╗ ██║   ██║   ███████║███████╗██╔████╔██║███████║" -ForegroundColor Magenta
    Write-Host "  ██╔══╝  ██╔══██║██║╚██╗██║   ██║   ██╔══██║╚════██║██║╚██╔╝██║██╔══██║" -ForegroundColor Magenta
    Write-Host "  ██║     ██║  ██║██║ ╚████║   ██║   ██║  ██║███████║██║ ╚═╝ ██║██║  ██║" -ForegroundColor Magenta
    Write-Host "  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "          Windows Installer" -ForegroundColor Cyan
    Write-Host ""
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Python installation
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            Write-Info "Found Python $major.$minor"
            
            if ($major -ge 3 -and $minor -ge 7) {
                return $true
            } else {
                Write-Warning "Python 3.7 or later is required. Found: $pythonVersion"
                return $false
            }
        }
    } catch {
        return $false
    }
    return $false
}

# Install Python
function Install-Python {
    Write-Info "Python 3 is required but not found."
    Write-Info "Downloading Python installer..."
    
    # Use a recent stable version - update as needed
    $pythonVersion = "3.12.1"
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    try {
        Write-Info "Downloading Python $pythonVersion..."
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
        
        Write-Info "Installing Python..."
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        
        Write-Success "✓ Python installed successfully"
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Remove-Item $installerPath -Force
    } catch {
        Write-Fail "✗ Failed to install Python: $_"
        Write-Info "Please install Python manually from https://www.python.org/"
        exit 1
    }
}

# Check WiFi adapter compatibility
function Test-WiFiCompatibility {
    Write-Info "Checking WiFi adapter compatibility..."
    
    try {
        $driverInfo = netsh wlan show drivers 2>&1
        
        if ($driverInfo -match "Hosted network supported\s*:\s*Yes") {
            Write-Success "✓ WiFi adapter supports Hosted Network"
            return $true
        } else {
            Write-Warning "⚠ WiFi adapter may not support Hosted Network"
            Write-Info "  Some features may be limited"
            return $false
        }
    } catch {
        Write-Warning "⚠ Could not check WiFi adapter compatibility"
        return $false
    }
}

# Install FantasmaWiFi-Pro
function Install-Fantasma {
    Write-Info "Installing FantasmaWiFi-Pro..."
    
    try {
        # Upgrade pip first
        python -m pip install --upgrade pip
        
        # Install FantasmaWiFi-Pro
        python -m pip install fantasmawifi-pro
        
        Write-Success "✓ FantasmaWiFi-Pro installed successfully"
        
        # Create desktop shortcut (optional)
        $createShortcut = Read-Host "Create desktop shortcut for Web UI? (Y/n)"
        if ($createShortcut -ne "n" -and $createShortcut -ne "N") {
            Create-DesktopShortcut
        }
        
    } catch {
        Write-Fail "✗ Failed to install FantasmaWiFi-Pro: $_"
        exit 1
    }
}

# Create desktop shortcut
function Create-DesktopShortcut {
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $desktop = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = "$desktop\FantasmaWiFi.lnk"
        $shortcut = $WshShell.CreateShortcut($shortcutPath)
        
        # Get Python Scripts directory
        $pythonScripts = python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts'))"
        $target = "$pythonScripts\fantasma-web.exe"
        
        $shortcut.TargetPath = $target
        $shortcut.WorkingDirectory = $desktop
        $shortcut.Description = "FantasmaWiFi-Pro Web UI"
        $shortcut.Save()
        
        Write-Success "✓ Desktop shortcut created"
    } catch {
        Write-Warning "⚠ Could not create desktop shortcut: $_"
    }
}

# Uninstall FantasmaWiFi-Pro
function Uninstall-Fantasma {
    Write-Info "Uninstalling FantasmaWiFi-Pro..."
    
    try {
        python -m pip uninstall -y fantasmawifi-pro
        
        # Remove desktop shortcut if exists
        $desktop = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = "$desktop\FantasmaWiFi.lnk"
        if (Test-Path $shortcutPath) {
            Remove-Item $shortcutPath -Force
            Write-Success "✓ Removed desktop shortcut"
        }
        
        Write-Success "✓ FantasmaWiFi-Pro uninstalled successfully"
    } catch {
        Write-Fail "✗ Failed to uninstall: $_"
        exit 1
    }
}

# Run post-installation diagnostics
function Test-Installation {
    Write-Info "Running diagnostics..."
    
    try {
        python -m fantasma_doctor
        
        Write-Success ""
        Write-Success "✓ Installation complete!"
        Write-Info ""
        Write-Info "Quick Start:"
        Write-Info "  1. Run 'fantasma doctor' to check system"
        Write-Info "  2. Run 'fantasma list' to see network interfaces"
        Write-Info "  3. Run 'fantasma-web' to start Web UI"
        Write-Info ""
        Write-Info "Documentation: https://github.com/Blackmvmba88/FantasmaWiFi-Pro"
        
    } catch {
        Write-Warning "⚠ Could not run diagnostics. Try running 'fantasma doctor' manually."
    }
}

# Main installation flow
function Install-Main {
    Show-Banner
    
    # Check administrator privileges
    if (-not (Test-Administrator)) {
        Write-Fail "✗ This script requires Administrator privileges"
        Write-Info "Please right-click and select 'Run as Administrator'"
        exit 1
    }
    
    Write-Success "✓ Running with Administrator privileges"
    Write-Info ""
    
    # Check/Install Python
    if (-not $SkipPython) {
        if (-not (Test-Python)) {
            $installPython = Read-Host "Python 3.7+ is required. Install now? (Y/n)"
            if ($installPython -eq "n" -or $installPython -eq "N") {
                Write-Info "Installation cancelled. Please install Python manually."
                exit 0
            }
            Install-Python
        } else {
            Write-Success "✓ Python version OK"
        }
    }
    
    Write-Info ""
    
    # Check WiFi compatibility
    Test-WiFiCompatibility
    
    Write-Info ""
    
    # Install FantasmaWiFi-Pro
    Install-Fantasma
    
    Write-Info ""
    
    # Run diagnostics
    Test-Installation
}

# Main entry point
if ($Uninstall) {
    Show-Banner
    
    if (-not (Test-Administrator)) {
        Write-Fail "✗ This script requires Administrator privileges"
        exit 1
    }
    
    $confirm = Read-Host "Uninstall FantasmaWiFi-Pro? (Y/n)"
    if ($confirm -ne "n" -and $confirm -ne "N") {
        Uninstall-Fantasma
    }
} else {
    Install-Main
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
