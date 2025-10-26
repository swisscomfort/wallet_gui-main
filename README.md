# 🔍 Wallet Scanner GUI

**Professional Cryptocurrency Wallet Forensic Analysis Tool**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.kernel.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/swisscomfort/wallet_gui-main)](https://github.com/swisscomfort/wallet_gui-main/releases)
[![GitHub stars](https://img.shields.io/github/stars/swisscomfort/wallet_gui-main)](https://github.com/swisscomfort/wallet_gui-main/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/swisscomfort/wallet_gui-main)](https://github.com/swisscomfort/wallet_gui-main/issues)

---

## 📦 **BONUS: Project Bundle Creator Tool**

**NEU:** Dieses Repository enthält auch ein universelles Tool zum Erstellen selbstentpackender Projekt-Bundles!

### 🚀 **Direkter Download:**
```bash
curl -O https://raw.githubusercontent.com/swisscomfort/wallet_gui-main/main/tools/pack_project.sh
chmod +x pack_project.sh
./pack_project.sh /pfad/zum/projekt
```

**Features:** 
- 📦 Self-extracting `.run` bundles
- 🔐 SHA256-Integritätsprüfung  
- 🤖 Auto-Detection für Docker/Python/Node.js/Shell
- 🧹 Smart Excludes für saubere Bundles

👉 **[📖 Vollständige Dokumentation](docs/PACK_PROJECT_GUIDE.md)**

---

A comprehensive forensic analysis tool for cryptocurrency wallets, featuring both a modern GUI interface and powerful CLI capabilities. Designed for security professionals, forensic investigators, and blockchain analysts.

## 🚀 Features

### 🖥️ Modern GUI Interface
- **PyQt6-based** professional interface with native system integration
- **Real-time monitoring** with live scanner output and progress tracking
- **Multi-target support** for simultaneous scanning of directories, files, and devices
- **Advanced filtering** with regex support for result analysis
- **Native file dialogs** with KDE integration (kdialog) and fallback support

### 🔧 Powerful Scanning Engine
- **Auto-mount capability** for disk images and block devices (read-only)
- **Multi-format support** for images (.img, .iso, .dd), archives (.zip, .7z, .tar)
- **Device scanning** with automatic detection and mounting
- **Configurable scanning** with normal and aggressive modes
- **Pattern recognition** using YARA rules and custom patterns

### 🛡️ Security & Forensics
- **Read-only operations** to preserve evidence integrity
- **Secure privilege escalation** using pkexec for required operations
- **Comprehensive logging** with detailed audit trails
- **Mnemonic phrase detection** for seed phrase recovery
- **Export capabilities** in multiple formats (TSV, clipboard)

### 📱 Cross-Interface Support
- **GUI mode** for interactive analysis and visualization
- **CLI mode** for scripting and automation
- **Terminal integration** with external terminal support
- **System integration** with desktop environment features

## 📋 Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or equivalent)
- **Python**: 3.9 or higher
- **Desktop Environment**: KDE (recommended), GNOME, XFCE, or other Qt-compatible

### Required Python Dependencies
```bash
pip install PyQt6>=6.4.0
```

### Required System Packages
```bash
# Core functionality
sudo apt install kdialog p7zip p7zip-plugins

# Forensic capabilities  
sudo apt install sleuthkit ntfs-3g

# Privilege escalation
sudo apt install policykit-1
```

### Optional Enhancements
```bash
# Enhanced scanning capabilities
sudo apt install ripgrep yara exfatprogs

# Additional filesystem support
sudo apt install fuse3 cryptsetup
```

## 🔧 Installation

### Method 1: Package Installation (Recommended)
```bash
git clone https://github.com/swisscomfort/wallet_gui-main.git
cd wallet_gui-main

# Install package
pip install -e .

# Initialize configuration
wallet-scanner setup

# Verify installation
wallet-scanner check
```

### Method 2: Direct Installation Script
```bash
# Quick install
chmod +x install_wallet_gui.sh
./install_wallet_gui.sh
```

### Method 3: Development Setup
```bash
# Development environment
git clone https://github.com/wallet-scanner/wallet-gui.git
cd wallet-gui

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## 🚀 Quick Start

### Launch GUI Application
```bash
# Simple launch
wallet-scanner

# Or explicitly
wallet-scanner gui
```

### CLI Usage Examples
```bash
# Check system requirements
wallet-scanner check

# List available scanners
wallet-scanner list-scanners

# Analyze targets
wallet-scanner analyze /path/to/target

# Get help
wallet-scanner --help
```

## 📖 Usage Guide

### Basic Workflow

1. **🎯 Configure Root Directory**
   - Set output directory for scan results
   - Ensure sufficient disk space available

2. **⚙️ Select Scanner Engine**
   - Choose from available scanner scripts
   - `hrm_swarm_scanner_wrapper.sh` recommended for modern features

3. **📁 Add Scan Targets**
   - **Directories**: Use "Ordner hinzufügen" for file system scanning
   - **Images/Files**: Use "Datei/Abbild hinzufügen" for disk images (>512MB)
   - **Block Devices**: Use "Device hinzufügen" for direct device access

4. **🔧 Configure Options**
   - **Aggressive Mode**: Enhanced scanning with larger file limits
   - **Auto-Mount**: Automatic mounting of images and devices
   - **Root Access**: Enable for device scanning and image mounting
   - **Staging**: Create symbolic links to found files

5. **▶️ Execute Scan**
   - Monitor progress in Live-Log tab
   - Review results in Hits and Mnemonics tabs

### Advanced Configuration

#### For Large Disk Images (>512MB)
```bash
✅ CORRECT: "Datei/Abbild hinzufügen" + "Mit Root" + "Auto-Mount"
❌ WRONG: "Ordner hinzufügen" (images will be skipped!)
```

#### For Block Devices
```bash
✅ REQUIRED: Enable "Mit Root (pkexec)" + "Auto-Mount"
💡 TIP: Use /dev/disk/by-label/ for readable device names
```

### Scanner Scripts

The application supports multiple scanner backends:

| Scanner | Description | Recommended Use |
|---------|-------------|-----------------|
| `wallet_harvest_any.sh` | Legacy scanner | Standard operations |
| `hrm_swarm_scanner_wrapper.sh` | Modern HRM scanner | **Recommended** for auto-mount |
| `wallet_scan_archives.sh` | Archive specialist | ZIP, 7Z, TAR files |
| `wallet_scan_images.sh` | Image specialist | Disk images only |

## 📊 Output Structure

Scan results are organized in timestamped directories:

```
<ROOT>/_logs/walletscan_2024-01-15_14-30-25/
├── hits.txt              # All discovered matches
├── mnemonic_raw.txt      # Seed phrase candidates
├── scan.log              # Complete scanner output
├── summary.json          # Scan statistics
└── _staging_wallets/     # Symbolic links (if enabled)
```

## 🖥️ GUI Components

### Live-Log Tab
- Real-time scanner output with auto-scrolling
- Elapsed time tracking and status updates
- Complete command-line output capture

### Hits Tab
- Filterable results table with regex support
- Columns: File path, Line number, Match snippet
- Export functionality (TSV format, clipboard)
- Direct file opening capability

### Mnemonics Tab
- Automatically detected seed phrase candidates
- Support for 12/24 word combinations
- Heuristic validation and scoring

### Help Tab
- Comprehensive usage instructions
- Workflow examples and best practices
- Troubleshooting guidance

## 🔒 Security Considerations

### ⚠️ Important Security Notes

**This tool is designed for legitimate forensic analysis and security research only.**

- ✅ Use only on systems you own or have explicit permission to analyze
- ✅ Root privileges used only for read-only mounting operations
- ✅ All operations preserve data integrity (no modifications)
- ✅ Comprehensive audit logging for compliance

### Legal Compliance

- 📋 Intended for lawful purposes only (forensics, security audits, personal systems)
- 📋 Users responsible for compliance with local laws and regulations
- 📋 No warranty provided - use at your own risk
- 📋 Always obtain proper authorization before analysis

## 🛠️ Troubleshooting

### Common Issues

#### Scanner Scripts Not Found
```bash
# Install scanner scripts
mkdir -p ~/.local/share/wallet-gui/scripts
cp scripts/* ~/.local/share/wallet-gui/scripts/
chmod +x ~/.local/share/wallet-gui/scripts/*.sh
```

#### Permission Issues
```bash
# Ensure pkexec is available
sudo apt install policykit-1

# Verify user permissions
groups $USER
```

#### GUI Launch Problems
```bash
# Install PyQt6
pip install PyQt6>=6.4.0

# System package alternative
sudo apt install python3-pyqt6
```

### Debug Mode

Enable verbose logging for troubleshooting:
```bash
# Enable terminal output in GUI
# Check "🖥️ Terminal-Fenster beim Scan zeigen"

# CLI debug mode
wallet-scanner --verbose gui
```

## 🏗️ Development

### Project Structure
```
src/
├── wallet_scanner/
│   ├── gui/                 # PyQt6 GUI components
│   ├── core/                # Core scanning logic
│   ├── cli/                 # Command-line interface
│   └── __init__.py
├── scripts/                 # Scanner backend scripts
├── docs/                    # Documentation
├── tests/                   # Test suite
└── examples/                # Configuration examples
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Code formatting
black src/

# Type checking
mypy src/

# Run tests
pytest

# Build documentation
sphinx-build docs/ docs/_build/
```

## 📚 Documentation

- 📖 **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- 🔧 **Installation**: [INSTALL.md](INSTALL.md)
- 🛡️ **Security**: [SECURITY.md](SECURITY.md)
- 📝 **API Reference**: [docs/API.md](docs/API.md)
- 🐛 **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/wallet-scanner/wallet-gui/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/wallet-scanner/wallet-gui/discussions)
- 📖 **Documentation**: [ReadTheDocs](https://wallet-scanner.readthedocs.io/)
- 💬 **Community**: [Gitter Chat](https://gitter.im/wallet-scanner/community)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- PyQt6 development team for the excellent GUI framework
- Sleuthkit developers for forensic analysis capabilities
- KDE project for native dialog integration
- Open source forensics community for tools and techniques

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Compatibility**: Linux (KDE/GNOME/XFCE), Python 3.9+, PyQt6 6.4+

[![GitHub stars](https://img.shields.io/github/stars/wallet-scanner/wallet-gui.svg)](https://github.com/wallet-scanner/wallet-gui/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/wallet-scanner/wallet-gui.svg)](https://github.com/wallet-scanner/wallet-gui/issues)
[![GitHub license](https://img.shields.io/github/license/wallet-scanner/wallet-gui.svg)](https://github.com/wallet-scanner/wallet-gui/blob/main/LICENSE)