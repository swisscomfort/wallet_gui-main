"""
Core scanning functionality for wallet detection.
"""

# Import only what exists
try:
    from .scanner import ScannerConfig, ScannerCommand, TargetAnalyzer, PatternMatcher
except ImportError:
    ScannerConfig = ScannerCommand = TargetAnalyzer = PatternMatcher = None

try:
    from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION
except ImportError:
    APP_NAME = APP_VERSION = APP_DESCRIPTION = None

try:
    from .utils import quoted, format_file_size, find_scanner_scripts
except ImportError:
    quoted = format_file_size = find_scanner_scripts = None

__all__ = [
    "ScannerConfig",
    "ScannerCommand", 
    "TargetAnalyzer",
    "PatternMatcher",
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "quoted",
    "format_file_size", 
    "find_scanner_scripts"
]