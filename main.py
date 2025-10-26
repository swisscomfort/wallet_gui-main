#!/usr/bin/env python3
"""
Wallet Scanner - Main Entry Point

This module provides the main entry point for the Wallet Scanner application.
It handles argument parsing and routes to the appropriate interface (GUI or CLI).
"""

import sys
from pathlib import Path

# Add src directory to Python path if running from development environment
if __name__ == "__main__" and "src" in str(Path(__file__).parent):
    src_dir = Path(__file__).parent / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))

try:
    from wallet_scanner.cli.cli_main import main as cli_main
except ImportError as e:
    print(f"Error importing wallet_scanner: {e}")
    print("Make sure the package is properly installed:")
    print("  pip install -e .")
    sys.exit(1)


def main():
    """
    Main entry point that routes to CLI handler.
    
    The CLI handler will determine whether to launch GUI or CLI mode
    based on command line arguments.
    """
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())