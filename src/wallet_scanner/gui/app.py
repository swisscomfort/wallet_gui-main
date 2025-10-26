#!/usr/bin/env python3
"""
Wallet Scanner GUI Application Module

This module provides the main application entry point and initialization
for the Wallet Scanner GUI application.
"""

import sys
from PyQt6 import QtWidgets

from .main_window import MainWindow


class WalletScannerApp:
    """
    Main application class for the Wallet Scanner GUI.
    
    This class handles application initialization, configuration,
    and the main event loop management.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.app = None
        self.main_window = None
    
    def run(self):
        """
        Start the application and enter the main event loop.
        
        Returns:
            int: Application exit code
        """
        self.app = QtWidgets.QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("Wallet Scanner GUI")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("Wallet Scanner")
        self.app.setOrganizationDomain("wallet-scanner.local")
        
        # Create and show main window
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Enter event loop
        return sys.exit(self.app.exec())


def main():
    """Main entry point for the application."""
    app = WalletScannerApp()
    return app.run()


if __name__ == "__main__":
    main()