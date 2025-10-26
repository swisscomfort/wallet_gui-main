#!/usr/bin/env python3
"""
Wallet Scanner Utility Functions

This module provides utility functions and helpers used throughout
the Wallet Scanner application.
"""

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .config import TERMINAL_EMULATORS, REQUIRED_PACKAGES, OPTIONAL_PACKAGES


def quoted(string: str) -> str:
    """
    Shell-escape a string for safe command line usage.
    
    Args:
        string: String to escape
        
    Returns:
        Shell-escaped string
    """
    return shlex.quote(string)


def find_scanner_scripts(scripts_dir: Optional[Path] = None) -> List[Path]:
    """
    Find available scanner scripts in the specified directory.
    
    Args:
        scripts_dir: Directory to search for scripts (optional)
        
    Returns:
        List of Path objects for found scanner scripts
    """
    if scripts_dir is None:
        scripts_dir = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
    
    if not scripts_dir.exists():
        return []
    
    scanners = []
    for pattern in ("*.sh", "*.py"):
        scanners.extend(scripts_dir.glob(pattern))
    
    return sorted(scanners, key=lambda p: p.name)


def find_terminal_emulator() -> Optional[Tuple[str, List[str]]]:
    """
    Find the first available terminal emulator from the preferred list.
    
    Returns:
        Tuple of (name, command_template) or None if none found
    """
    for name, cmd_template in TERMINAL_EMULATORS:
        if shutil.which(name):
            return name, cmd_template
    return None


def check_system_requirements() -> Tuple[List[str], List[str]]:
    """
    Check system for required and optional packages.
    
    Returns:
        Tuple of (missing_required, missing_optional) package lists
    """
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package in REQUIRED_PACKAGES:
        if package.startswith("python3-"):
            # For Python packages, check import
            module_name = package.replace("python3-", "").replace("-", "_")
            try:
                __import__(module_name)
            except ImportError:
                missing_required.append(package)
        else:
            # For system packages, check executable
            if not shutil.which(package):
                missing_required.append(package)
    
    # Check optional packages
    for package in OPTIONAL_PACKAGES:
        if not shutil.which(package):
            missing_optional.append(package)
    
    return missing_required, missing_optional


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def is_image_file(path: Union[str, Path]) -> bool:
    """
    Check if a file is a disk image based on its extension.
    
    Args:
        path: File path to check
        
    Returns:
        True if file appears to be a disk image
    """
    from .config import IMAGE_EXTENSIONS
    return Path(path).suffix in IMAGE_EXTENSIONS


def is_archive_file(path: Union[str, Path]) -> bool:
    """
    Check if a file is an archive based on its extension.
    
    Args:
        path: File path to check
        
    Returns:
        True if file appears to be an archive
    """
    from .config import ARCHIVE_EXTENSIONS
    return Path(path).suffix in ARCHIVE_EXTENSIONS


def is_device_path(path: Union[str, Path]) -> bool:
    """
    Check if a path appears to be a block device.
    
    Args:
        path: Path to check
        
    Returns:
        True if path appears to be a device
    """
    path_str = str(path)
    return path_str.startswith("/dev/") and not path_str.endswith("/")


def create_directory_safely(path: Union[str, Path]) -> bool:
    """
    Create directory with proper error handling.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def run_command(
    command: List[str],
    capture_output: bool = True,
    text: bool = True,
    timeout: Optional[float] = None
) -> subprocess.CompletedProcess:
    """
    Run a command with proper error handling.
    
    Args:
        command: Command and arguments to run
        capture_output: Whether to capture stdout/stderr
        text: Whether to return text output
        timeout: Optional timeout in seconds
        
    Returns:
        CompletedProcess instance
    """
    try:
        return subprocess.run(
            command,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            check=False
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        # Create a mock CompletedProcess for error cases
        result = subprocess.CompletedProcess(
            args=command,
            returncode=-1,
            stdout="",
            stderr=str(e)
        )
        return result


def open_file_manager(path: Union[str, Path], select_file: bool = False) -> bool:
    """
    Open file manager at the specified path.
    
    Args:
        path: Path to open
        select_file: Whether to select the file (if path is a file)
        
    Returns:
        True if successful, False otherwise
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        return False
    
    try:
        if select_file and path_obj.is_file() and shutil.which("dolphin"):
            # Use Dolphin's select feature for files
            subprocess.Popen(["dolphin", "--select", str(path_obj)])
        else:
            # Open directory
            target = path_obj if path_obj.is_dir() else path_obj.parent
            subprocess.Popen(["xdg-open", str(target)])
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def validate_scanner_script(script_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Validate that a scanner script exists and is executable.
    
    Args:
        script_path: Path to scanner script
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(script_path)
    
    if not path.exists():
        return False, f"Scanner script not found: {path}"
    
    if not path.is_file():
        return False, f"Scanner path is not a file: {path}"
    
    if not os.access(path, os.R_OK):
        return False, f"Scanner script is not readable: {path}"
    
    if path.suffix not in {".sh", ".py"}:
        return False, f"Unsupported scanner type: {path.suffix}"
    
    # Check for standalone scanner warning
    if "standalone" in str(path):
        return False, (
            f"Standalone scanner detected: {path.name}\n"
            "Standalone scanners are not GUI-compatible and must be run via CLI."
        )
    
    return True, "Scanner script is valid"


def get_latest_scan_output(logs_dir: Union[str, Path]) -> Optional[Path]:
    """
    Find the most recent scan output directory.
    
    Args:
        logs_dir: Logs directory to search
        
    Returns:
        Path to latest scan output directory, or None if not found
    """
    logs_path = Path(logs_dir)
    
    if not logs_path.exists():
        return None
    
    scan_dirs = list(logs_path.glob("walletscan_*"))
    if not scan_dirs:
        return None
    
    # Sort by modification time, newest first
    scan_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return scan_dirs[0]


def ensure_config_directories() -> bool:
    """
    Ensure all required configuration directories exist.
    
    Returns:
        True if successful, False otherwise
    """
    from .config import DEFAULT_CONFIG_DIR, DEFAULT_DATA_DIR, DEFAULT_SCRIPTS_DIR
    
    directories = [DEFAULT_CONFIG_DIR, DEFAULT_DATA_DIR, DEFAULT_SCRIPTS_DIR]
    
    for directory in directories:
        if not create_directory_safely(directory):
            return False
    
    return True


def clean_log_output(text: str) -> str:
    """
    Clean scanner log output for display in GUI.
    
    Args:
        text: Raw log text
        
    Returns:
        Cleaned log text
    """
    # Remove ANSI escape sequences
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', text)
    
    # Normalize line endings
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    
    return cleaned


def extract_output_directory(log_text: str) -> Optional[str]:
    """
    Extract output directory path from scanner log text.
    
    Args:
        log_text: Scanner log output
        
    Returns:
        Output directory path if found, None otherwise
    """
    import re
    match = re.search(r"OUT=(\S+)", log_text)
    return match.group(1) if match else None


class ProgressTracker:
    """
    Simple progress tracking utility for long-running operations.
    """
    
    def __init__(self, total_steps: int = 100):
        """
        Initialize progress tracker.
        
        Args:
            total_steps: Total number of steps expected
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.messages = []
    
    def update(self, step: int, message: str = ""):
        """
        Update progress.
        
        Args:
            step: Current step number
            message: Optional progress message
        """
        self.current_step = min(step, self.total_steps)
        if message:
            self.messages.append(message)
    
    def get_percentage(self) -> float:
        """Get progress as percentage (0-100)."""
        return (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
    
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current_step >= self.total_steps
    
    def get_latest_message(self) -> str:
        """Get the most recent progress message."""
        return self.messages[-1] if self.messages else ""