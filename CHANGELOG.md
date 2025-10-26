# Changelog

All notable changes to the Wallet Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-15

### 🚀 Major Release - Complete Refactoring

This is a complete rewrite and professionalization of the Wallet Scanner GUI application.

### ✨ Added

#### New Package Structure
- **Professional Python Package**: Complete migration to `src/wallet_scanner/` structure
- **Modular Architecture**: Separated GUI, CLI, and core functionality
- **Modern Build System**: Added `setup.py`, `pyproject.toml`, and proper packaging
- **Entry Points**: Console scripts for `wallet-scanner` and `wallet-scanner-gui`

#### Enhanced CLI Interface
- **Full CLI Support**: New command-line interface with subcommands
- **System Checking**: `wallet-scanner check` for dependency verification
- **Scanner Management**: `wallet-scanner list-scanners` for available scripts
- **Target Analysis**: `wallet-scanner analyze` for pre-scan target evaluation
- **Setup Automation**: `wallet-scanner setup` for configuration initialization

#### Improved GUI Features
- **Refactored Main Window**: Clean, modular PyQt6 interface
- **Enhanced File Dialogs**: Better integration with kdialog and fallback support
- **Professional Layout**: Improved spacing, organization, and visual hierarchy
- **Comprehensive Help**: Detailed in-app documentation and usage guide
- **Error Handling**: Better error messages and user feedback

#### Core Functionality Improvements
- **Scanner Configuration**: Structured configuration management
- **Result Processing**: Enhanced result parsing and display
- **Utility Functions**: Comprehensive helper functions and validation
- **System Integration**: Better desktop environment integration

#### Documentation & Security
- **Comprehensive README**: Professional documentation with badges and examples
- **Installation Guide**: Detailed INSTALL.md with multiple installation methods
- **Security Policy**: Complete SECURITY.md with usage guidelines and compliance
- **Code Documentation**: Full docstrings and type hints throughout codebase

### 🔧 Changed

#### Breaking Changes
- **Import Paths**: All imports now use `wallet_scanner.*` namespace
- **Configuration**: New configuration directory structure
- **Entry Points**: New command-line interface replaces direct script execution
- **Dependencies**: Updated to PyQt6 (was PyQt5 in legacy versions)

#### Improved Architecture
- **Separation of Concerns**: GUI, CLI, and core logic properly separated
- **Type Safety**: Added comprehensive type hints
- **Error Handling**: Improved exception handling and user feedback
- **Code Quality**: Black formatting, flake8 linting, mypy type checking

#### Enhanced User Experience
- **Cleaner Interface**: Redesigned GUI with better organization
- **Better Workflows**: Improved multi-step processes and validation
- **Professional Appearance**: Modern styling and layout improvements
- **Help Integration**: Built-in comprehensive help and documentation

### 🛠️ Fixed

#### Stability Improvements
- **Memory Management**: Better resource handling and cleanup
- **Process Management**: Improved scanner process lifecycle
- **File Handling**: More robust file system operations
- **Error Recovery**: Better handling of edge cases and errors

#### GUI Fixes
- **Dialog Sizing**: Consistent 1200x800 dialog windows
- **Layout Issues**: Fixed spacing and alignment problems
- **Widget Behavior**: Improved responsiveness and interaction
- **Terminal Integration**: Better external terminal support

### 📦 Dependencies

#### Updated Requirements
- **Python**: Minimum version 3.9+ (was 3.7+)
- **PyQt6**: Upgraded from PyQt5 for modern GUI features
- **Type Hints**: Full typing support for better development experience
- **Build Tools**: Modern packaging with setuptools and build

#### Development Dependencies
- **pytest**: Testing framework with Qt support
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **sphinx**: Documentation generation

### 🔄 Migration Guide

#### For End Users
1. Uninstall previous version: `rm -rf old_wallet_gui/`
2. Install new version: `pip install -e .`
3. Run setup: `wallet-scanner setup`
4. Verify installation: `wallet-scanner check`

#### For Developers
1. Update imports: `from wallet_scanner.gui.app import main`
2. Use new CLI: `wallet-scanner gui` instead of `python wallet_gui.py`
3. Follow new project structure for contributions
4. Use development tools: `pip install -e ".[dev]"`

### 🎯 Compatibility

#### Supported Platforms
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 35+
- **Desktop Environments**: KDE, GNOME, XFCE, i3/sway
- **Python**: 3.9, 3.10, 3.11, 3.12

#### Backwards Compatibility
- **Scanner Scripts**: Existing scanner scripts remain compatible
- **Configuration**: Legacy configurations can be migrated
- **Results Format**: Output formats maintained for compatibility
- **Workflows**: Core scanning workflows unchanged

---

## [1.5.0] - 2024-01-01 (Legacy)

### Added
- Terminal window integration option
- Enhanced file dialog support
- Improved scanner script management
- Better device handling for forensic analysis

### Changed
- Updated GUI layout and organization
- Improved error handling and user feedback
- Enhanced documentation and help text

### Fixed
- File size limit handling for large images
- Device mounting issues with newer kernels
- Qt dialog integration improvements

---

## [1.0.0] - 2023-06-01 (Legacy)

### Added
- Initial PyQt5-based GUI application
- Basic scanner script integration
- File and directory selection
- Real-time log output
- Results display with filtering
- Mnemonic detection functionality

### Features
- Multi-target scanning support
- Auto-mount capabilities for disk images
- Native kdialog integration
- Root privilege handling with pkexec
- Export functionality for results

---

## Development Guidelines

### Versioning Strategy
- **Major (X.0.0)**: Breaking changes, major architectural changes
- **Minor (X.Y.0)**: New features, significant improvements, non-breaking changes
- **Patch (X.Y.Z)**: Bug fixes, small improvements, security patches

### Release Process
1. Update version in `src/wallet_scanner/core/config.py`
2. Update CHANGELOG.md with changes
3. Run full test suite: `pytest`
4. Build and test package: `python -m build`
5. Tag release: `git tag v2.0.0`
6. Create GitHub release with changelog
7. Publish to PyPI if applicable

### Contribution Guidelines
- Follow [Conventional Commits](https://www.conventionalcommits.org/)
- Add changelog entries for user-facing changes
- Update documentation for new features
- Include tests for new functionality
- Ensure compatibility with supported platforms