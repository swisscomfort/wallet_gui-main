#!/usr/bin/env python3
"""
Setup script for Wallet Scanner GUI

This script handles installation and packaging for the Wallet Scanner
cryptocurrency forensic analysis application.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure Python version compatibility
if sys.version_info < (3, 9):
    sys.exit("ERROR: Python 3.9 or higher is required for this package.")

# Read version from package
def get_version():
    """Extract version from the source code."""
    version_file = Path(__file__).parent / "src" / "wallet_scanner" / "core" / "config.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("APP_VERSION"):
                return line.split("=")[1].strip().strip('"\'')
    return "2.0.0"

# Read long description from README
def get_long_description():
    """Get long description from README file."""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "Cryptocurrency Wallet Forensic Scanner with GUI and CLI interface."

# Read requirements
def get_requirements():
    """Get requirements from requirements.txt."""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
            return requirements
    return ["PyQt6>=6.4.0"]

# Development requirements
dev_requirements = [
    "pytest>=7.0",
    "pytest-qt>=4.0",
    "black>=22.0",
    "flake8>=4.0",
    "mypy>=0.950",
    "sphinx>=4.0",
    "sphinx-rtd-theme>=1.0",
    "twine>=4.0",
    "build>=0.8",
]

# Optional requirements for enhanced functionality
optional_requirements = {
    "dev": dev_requirements,
    "docs": [
        "sphinx>=4.0",
        "sphinx-rtd-theme>=1.0",
        "myst-parser>=0.18",
    ],
    "test": [
        "pytest>=7.0",
        "pytest-qt>=4.0",
        "pytest-cov>=3.0",
    ],
}

# Package data files
def get_package_data():
    """Get package data files."""
    data_files = []
    
    # Look for data files in the package
    src_dir = Path(__file__).parent / "src" / "wallet_scanner"
    
    for pattern in ["*.yaml", "*.yml", "*.json", "*.txt", "*.md"]:
        for file_path in src_dir.rglob(pattern):
            relative_path = file_path.relative_to(src_dir)
            data_files.append(str(relative_path))
    
    return {"wallet_scanner": data_files}

# Entry points for console scripts
entry_points = {
    "console_scripts": [
        "wallet-scanner=wallet_scanner.cli.cli_main:main",
        "wallet-scanner-gui=wallet_scanner.gui.app:main",
    ],
}

# Classifiers for PyPI
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
    "Topic :: System :: Forensics",
    "Topic :: Office/Business :: Financial",
    "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
]

# Setup configuration
setup(
    # Basic package information
    name="wallet-scanner",
    version=get_version(),
    description="Cryptocurrency Wallet Forensic Scanner with GUI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # Author information
    author="Wallet Scanner Team",
    author_email="wallet-scanner@example.com",
    maintainer="Emil",
    
    # URLs and metadata
    url="https://github.com/wallet-scanner/wallet-gui",
    project_urls={
        "Bug Tracker": "https://github.com/wallet-scanner/wallet-gui/issues",
        "Documentation": "https://wallet-scanner.readthedocs.io/",
        "Source Code": "https://github.com/wallet-scanner/wallet-gui",
    },
    
    # License
    license="MIT",
    
    # Package discovery and structure
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=get_package_data(),
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.9",
    install_requires=get_requirements(),
    extras_require=optional_requirements,
    
    # Entry points
    entry_points=entry_points,
    
    # Classification
    classifiers=classifiers,
    keywords=[
        "cryptocurrency", "wallet", "forensics", "blockchain", "security",
        "bitcoin", "ethereum", "scanning", "gui", "cli", "pyqt6"
    ],
    
    # Additional metadata
    zip_safe=False,
    platforms=["Linux"],
    
    # Scripts and data files
    data_files=[
        # Desktop entry for GUI application
        ("share/applications", ["data/wallet-scanner.desktop"]),
        # Icon files
        ("share/icons/hicolor/256x256/apps", ["assets/wallet-scanner.png"]),
        # Documentation
        ("share/doc/wallet-scanner", ["README.md", "INSTALL.md", "SECURITY.md"]),
        # Example configuration
        ("share/wallet-scanner/examples", ["examples/hrm_policy.yaml"]),
        # Scanner scripts directory (will be created)
        ("share/wallet-scanner/scripts", []),
    ] if os.name == "posix" else [],
)

# Post-installation message
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 Wallet Scanner Installation")
    print("="*60)
    print("\nInstallation completed successfully!")
    print("\nNext steps:")
    print("1. Run 'wallet-scanner setup' to initialize configuration")
    print("2. Run 'wallet-scanner check' to verify system requirements")
    print("3. Launch GUI with 'wallet-scanner' or 'wallet-scanner gui'")
    print("4. See 'wallet-scanner --help' for CLI options")
    print("\nRequired system packages:")
    print("  sudo apt install kdialog p7zip p7zip-plugins sleuthkit ntfs-3g")
    print("\nOptional packages for enhanced functionality:")
    print("  sudo apt install ripgrep yara exfatprogs")
    print("\nFor documentation, visit:")
    print("  https://wallet-scanner.readthedocs.io/")
    print("="*60)