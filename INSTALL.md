# 🔧 Installation Guide

This guide provides detailed installation instructions for the Wallet Scanner GUI application.

## 📋 System Requirements

### Operating System
- **Linux Distribution**: Ubuntu 20.04+, Debian 11+, Fedora 35+, or equivalent
- **Architecture**: x86_64 (64-bit)
- **Kernel**: Linux 5.4+ (for modern filesystem support)

### Hardware Requirements
- **RAM**: Minimum 2GB, Recommended 8GB+ (for large disk analysis)
- **Storage**: At least 1GB free space for application + scan output storage
- **CPU**: Multi-core processor recommended for parallel scanning

### Desktop Environment
- **Recommended**: KDE Plasma 5.20+ (native kdialog support)
- **Supported**: GNOME 3.36+, XFCE 4.16+, LXQt, i3/sway + file manager

## 🐍 Python Requirements

### Python Version
```bash
# Check current Python version
python3 --version

# Minimum required: Python 3.9+
# Recommended: Python 3.11+
```

### Install Python (if needed)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/CentOS
sudo dnf install python3 python3-pip python3-venv

# Arch Linux
sudo pacman -S python python-pip
```

## 📦 System Dependencies

### Required Packages

#### Ubuntu/Debian
```bash
# Core GUI and compression
sudo apt update
sudo apt install kdialog p7zip-full p7zip-rar

# Forensic tools
sudo apt install sleuthkit ntfs-3g

# Privilege escalation
sudo apt install policykit-1

# Development tools (if building from source)
sudo apt install build-essential python3-dev
```

#### Fedora/CentOS/RHEL
```bash
# Core packages
sudo dnf install kdialog p7zip p7zip-plugins

# Forensic tools
sudo dnf install sleuthkit ntfs-3g

# Privilege escalation
sudo dnf install polkit

# Development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel
```

#### Arch Linux
```bash
# Core packages
sudo pacman -S kdialog p7zip

# Forensic tools
sudo pacman -S sleuthkit ntfs-3g

# Privilege escalation
sudo pacman -S polkit

# Development tools
sudo pacman -S base-devel
```

### Optional Packages (Recommended)

#### Enhanced Scanning Capabilities
```bash
# Ubuntu/Debian
sudo apt install ripgrep yara exfatprogs

# Fedora
sudo dnf install ripgrep yara exfatprogs

# Arch Linux
sudo pacman -S ripgrep yara-rules exfatprogs
```

#### Additional Filesystem Support
```bash
# Ubuntu/Debian
sudo apt install fuse3 cryptsetup-bin

# Fedora
sudo dnf install fuse3 cryptsetup

# Arch Linux
sudo pacman -S fuse3 cryptsetup
```

## 🚀 Installation Methods

### Method 1: pip Install (Recommended)

#### Standard Installation
```bash
# Clone repository
git clone https://github.com/wallet-scanner/wallet-gui.git
cd wallet-gui

# Install with pip
pip install .

# Or install in editable mode for development
pip install -e .
```

#### Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv wallet-scanner-env
source wallet-scanner-env/bin/activate

# Install package
pip install -e .

# Verify installation
wallet-scanner --version
```

### Method 2: Installation Script

#### Automated Setup
```bash
# Make script executable
chmod +x install_wallet_gui.sh

# Run installer
./install_wallet_gui.sh

# Follow on-screen instructions
```

#### Script Features
- Automatic dependency checking
- Virtual environment creation
- Desktop integration setup
- Scanner script installation
- Configuration directory creation

### Method 3: Manual Setup

#### Step-by-step Installation
```bash
# 1. Install Python dependencies
pip install PyQt6>=6.4.0

# 2. Create configuration directories
mkdir -p ~/.local/share/wallet-gui/scripts
mkdir -p ~/.config/wallet-scanner
mkdir -p ~/.local/share/wallet-scanner

# 3. Copy scanner scripts
cp scripts/* ~/.local/share/wallet-gui/scripts/
chmod +x ~/.local/share/wallet-gui/scripts/*.sh

# 4. Install main application
cp wallet_gui.py ~/.local/bin/
chmod +x ~/.local/bin/wallet_gui.py

# 5. Add to PATH (add to ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Post-Installation Setup

### Initialize Configuration
```bash
# Run initial setup
wallet-scanner setup

# This creates:
# - ~/.config/wallet-scanner/ (configuration)
# - ~/.local/share/wallet-scanner/ (application data)
# - ~/.local/share/wallet-gui/scripts/ (scanner scripts)
```

### Verify Installation
```bash
# Check system requirements
wallet-scanner check

# Expected output:
# ✅ Python version OK
# ✅ All required packages are available
# ✅ Configuration directories OK
# ✅ Found X scanner script(s)
```

### Test GUI Launch
```bash
# Launch GUI application
wallet-scanner gui

# Or using direct command
wallet-scanner
```

## 🖥️ Desktop Integration

### Create Desktop Entry
```bash
# Create desktop file
cat > ~/.local/share/applications/wallet-scanner.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Wallet Scanner
Comment=Cryptocurrency Wallet Forensic Analysis Tool
Exec=wallet-scanner gui
Icon=wallet-scanner
Terminal=false
Categories=Security;System;
Keywords=wallet;cryptocurrency;forensics;scanner;blockchain;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### Add Menu Integration (KDE)
```bash
# KDE menu integration
kbuildsycoca5
```

## 🛠️ Troubleshooting Installation

### Common Issues

#### PyQt6 Installation Problems
```bash
# Issue: PyQt6 fails to install
# Solution: Install system packages first
sudo apt install python3-pyqt6  # Ubuntu/Debian
sudo dnf install python3-pyqt6  # Fedora
sudo pacman -S python-pyqt6     # Arch Linux

# Alternative: Use pip with system site packages
pip install --system PyQt6
```

#### Permission Errors
```bash
# Issue: Permission denied during installation
# Solution: Use user installation
pip install --user -e .

# Or fix permissions
sudo chown -R $USER:$USER ~/.local/
```

#### Missing System Dependencies
```bash
# Issue: Scanner scripts fail
# Solution: Install missing tools
wallet-scanner check  # Shows missing dependencies

# Install reported missing packages
sudo apt install <missing-package>
```

#### PATH Issues
```bash
# Issue: Command not found after installation
# Solution: Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
which wallet-scanner
```

### Debug Installation
```bash
# Verbose pip installation
pip install -v -e .

# Check installed packages
pip list | grep -i wallet

# Python import test
python3 -c "import wallet_scanner; print('Import successful')"
```

## 🔄 Updating

### Update from Git
```bash
# Navigate to project directory
cd wallet-gui

# Pull latest changes
git pull origin main

# Reinstall package
pip install -e .

# Update configuration if needed
wallet-scanner setup
```

### Version Management
```bash
# Check current version
wallet-scanner --version

# List available versions (if using tagged releases)
git tag -l

# Switch to specific version
git checkout v2.0.0
pip install -e .
```

## 🗑️ Uninstallation

### Complete Removal
```bash
# Uninstall Python package
pip uninstall wallet-scanner

# Remove configuration directories
rm -rf ~/.config/wallet-scanner/
rm -rf ~/.local/share/wallet-scanner/
rm -rf ~/.local/share/wallet-gui/

# Remove desktop integration
rm -f ~/.local/share/applications/wallet-scanner.desktop
update-desktop-database ~/.local/share/applications/

# Remove from PATH (edit ~/.bashrc manually)
```

### Keep Configuration
```bash
# Only uninstall package, keep settings
pip uninstall wallet-scanner

# Configuration preserved in:
# ~/.config/wallet-scanner/
# ~/.local/share/wallet-gui/scripts/
```

## 📞 Installation Support

### Get Help
- **Installation Issues**: [GitHub Issues](https://github.com/wallet-scanner/wallet-gui/issues)
- **System Compatibility**: Check our [compatibility matrix](docs/COMPATIBILITY.md)
- **Community Support**: [Discussions](https://github.com/wallet-scanner/wallet-gui/discussions)

### Report Problems
When reporting installation issues, please include:

```bash
# System information
uname -a
python3 --version
pip --version

# Package versions
pip list | grep -E "(PyQt|wallet)"

# System packages
dpkg -l | grep -E "(kdialog|p7zip|sleuthkit)"  # Ubuntu/Debian
rpm -qa | grep -E "(kdialog|p7zip|sleuthkit)"  # Fedora/RHEL

# Installation log
pip install -v -e . 2>&1 | tee install.log
```

---

**Need Help?** Check our [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or [open an issue](https://github.com/wallet-scanner/wallet-gui/issues/new).