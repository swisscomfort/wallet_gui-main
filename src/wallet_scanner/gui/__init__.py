"""
GUI components for the wallet scanner.
"""

try:
    from .main_window import MainWindow
    from .app import WalletScannerApp
except ImportError:
    MainWindow = None
    WalletScannerApp = None

__all__ = ["MainWindow", "WalletScannerApp"]