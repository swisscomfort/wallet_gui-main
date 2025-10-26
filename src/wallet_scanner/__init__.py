#!/usr/bin/env python3
"""
Wallet Scanner - Cryptocurrency Wallet Forensic Analysis Tool

A comprehensive forensic analysis tool for cryptocurrency wallets, featuring
both modern GUI and CLI interfaces. Designed for security professionals,
forensic investigators, and blockchain analysts.

Features:
- PyQt6-based professional GUI with native system integration
- Command-line interface for scripting and automation
- Multi-format support for disk images, archives, and devices
- Read-only operations to preserve evidence integrity
- Advanced pattern recognition and mnemonic detection
- Comprehensive logging and audit trails

Usage:
    GUI Mode:
        >>> from wallet_scanner.gui.app import main
        >>> main()
    
    CLI Mode:
        >>> from wallet_scanner.cli.cli_main import main
        >>> main()
    
    Core Components:
        >>> from wallet_scanner.core.scanner import ScannerConfig
        >>> from wallet_scanner.core.utils import format_file_size
"""

from .core.config import APP_NAME, APP_VERSION, APP_DESCRIPTION

# Package metadata
__version__ = APP_VERSION
__title__ = APP_NAME
__description__ = APP_DESCRIPTION
__author__ = "Wallet Scanner Team"
__email__ = "wallet-scanner@example.com"
__license__ = "MIT"
__url__ = "https://github.com/wallet-scanner/wallet-gui"

# Version information
__version_info__ = tuple(map(int, APP_VERSION.split('.')))

# Export public API
__all__ = [
    "__version__",
    "__title__", 
    "__description__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "__version_info__",
]


def get_version_string() -> str:
    """
    Get formatted version string for display.
    
    Returns:
        Formatted version string with application name
    """
    return f"{__title__} v{__version__}"


def get_system_info() -> dict:
    """
    Get system information for debugging and support.
    
    Returns:
        Dictionary containing system and package information
    """
    import sys
    import platform
    from pathlib import Path
    
    try:
        from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        pyqt_info = {"qt_version": QT_VERSION_STR, "pyqt_version": PYQT_VERSION_STR}
    except ImportError:
        pyqt_info = {"qt_version": "Not available", "pyqt_version": "Not installed"}
    
    return {
        "wallet_scanner_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "executable": sys.executable,
        **pyqt_info,
        "install_path": str(Path(__file__).parent),
    }


def check_dependencies() -> dict:
    """
    Check if required dependencies are available.
    
    Returns:
        Dictionary with dependency status information
    """
    dependencies = {
        "PyQt6": False,
        "pathlib": False,
        "subprocess": False,
        "shutil": False,
        "re": False,
        "json": False,
    }
    
    # Check Python standard library modules
    try:
        import pathlib, subprocess, shutil, re, json
        dependencies.update({
            "pathlib": True,
            "subprocess": True, 
            "shutil": True,
            "re": True,
            "json": True,
        })
    except ImportError:
        pass
    
    # Check PyQt6
    try:
        import PyQt6
        dependencies["PyQt6"] = True
    except ImportError:
        pass
    
    return dependencies


# Convenience imports for common usage
try:
    from .core.config import (
        APP_NAME,
        APP_VERSION, 
        DEFAULT_ROOT_PATH,
        DEFAULT_SCANNER,
        RECOMMENDED_SCANNER
    )
    from .core.utils import (
        quoted,
        format_file_size,
        find_scanner_scripts,
        check_system_requirements
    )
    
    # Add to __all__ for public API
    __all__.extend([
        "APP_NAME",
        "APP_VERSION",
        "DEFAULT_ROOT_PATH", 
        "DEFAULT_SCANNER",
        "RECOMMENDED_SCANNER",
        "quoted",
        "format_file_size",
        "find_scanner_scripts",
        "check_system_requirements",
        "get_version_string",
        "get_system_info",
        "check_dependencies",
    ])

except ImportError:
    # Core modules not available - package may be partially installed
    pass