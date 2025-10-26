#!/usr/bin/env python3
"""
Wallet Scanner Core Module

This module provides the core scanner functionality and integration
with external scanner scripts.
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .config import (
    DEFAULT_FILE_SIZE_LIMIT,
    AGGRESSIVE_FILE_SIZE_LIMIT,
    DEFAULT_THREADS,
    AGGRESSIVE_THREADS
)
from .utils import (
    quoted,
    validate_scanner_script,
    is_image_file,
    is_archive_file,
    is_device_path,
    format_file_size
)


class ScannerConfig:
    """
    Configuration container for scanner execution parameters.
    """
    
    def __init__(self):
        """Initialize with default values."""
        self.root_path: str = ""
        self.targets: List[str] = []
        self.scanner_script: str = ""
        self.aggressive: bool = False
        self.staging: bool = False
        self.auto_mount: bool = True
        self.use_root: bool = False
        self.threads: Optional[int] = None
        self.file_size_limit: Optional[int] = None
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate scanner configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.root_path:
            return False, "ROOT path is required"
        
        if not Path(self.root_path).exists():
            return False, f"ROOT path does not exist: {self.root_path}"
        
        if not self.scanner_script:
            return False, "Scanner script is required"
        
        script_valid, script_error = validate_scanner_script(self.scanner_script)
        if not script_valid:
            return False, script_error
        
        # Validate targets
        for target in self.targets:
            target_path = Path(target)
            if not target_path.exists() and not is_device_path(target):
                return False, f"Target does not exist: {target}"
        
        return True, "Configuration is valid"
    
    def get_file_size_limit(self) -> int:
        """Get effective file size limit based on configuration."""
        if self.file_size_limit is not None:
            return self.file_size_limit
        return AGGRESSIVE_FILE_SIZE_LIMIT if self.aggressive else DEFAULT_FILE_SIZE_LIMIT
    
    def get_thread_count(self) -> int:
        """Get effective thread count based on configuration."""
        if self.threads is not None:
            return self.threads
        return AGGRESSIVE_THREADS if self.aggressive else DEFAULT_THREADS
    
    def requires_root_privileges(self) -> bool:
        """Check if configuration requires root privileges."""
        if self.use_root:
            return True
        
        # Check if any targets are devices or images that need mounting
        for target in self.targets:
            if is_device_path(target):
                return True
            if Path(target).is_file() and (is_image_file(target) or is_archive_file(target)):
                if self.auto_mount:
                    return True
        
        return False


class ScannerCommand:
    """
    Builder for scanner command line arguments.
    """
    
    def __init__(self, config: ScannerConfig):
        """
        Initialize command builder.
        
        Args:
            config: Scanner configuration
        """
        self.config = config
    
    def build_args(self) -> List[str]:
        """
        Build command line arguments for scanner execution.
        
        Returns:
            List of command arguments
        """
        args = [self.config.scanner_script, self.config.root_path]
        
        # Add option flags
        if self.config.aggressive:
            args.append("--aggressive")
        
        if self.config.staging:
            args.append("--staging")
        
        if self.config.auto_mount:
            args.append("--auto-mount")
        
        # Add custom thread count if specified
        if self.config.threads is not None:
            args.extend(["--threads", str(self.config.threads)])
        
        # Add custom file size limit if specified
        if self.config.file_size_limit is not None:
            args.extend(["--max-size", str(self.config.file_size_limit)])
        
        # Add targets
        args.extend(self.config.targets)
        
        return args
    
    def build_command(self) -> List[str]:
        """
        Build complete command including shell wrapper and privilege escalation.
        
        Returns:
            Complete command list ready for execution
        """
        args = self.build_args()
        
        # Build shell command
        shell_cmd = " ".join(quoted(arg) for arg in args)
        cmd = ["bash", "-lc", shell_cmd]
        
        # Add privilege escalation if required
        if self.config.requires_root_privileges():
            cmd = ["pkexec"] + cmd
        
        return cmd


class ScanResults:
    """
    Container for scanner execution results.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize results container.
        
        Args:
            output_dir: Scanner output directory
        """
        self.output_dir = output_dir
        self.hits: List[Tuple[str, int, str]] = []
        self.mnemonics: List[str] = []
        self.summary: Dict = {}
        self.errors: List[str] = []
    
    def load_from_directory(self, output_dir: Path) -> bool:
        """
        Load results from scanner output directory.
        
        Args:
            output_dir: Directory containing scanner output files
            
        Returns:
            True if results were loaded successfully
        """
        if not output_dir.exists():
            return False
        
        self.output_dir = output_dir
        
        # Load hits
        self._load_hits()
        
        # Load mnemonics
        self._load_mnemonics()
        
        # Load summary
        self._load_summary()
        
        return True
    
    def _load_hits(self):
        """Load hits from hits.txt file."""
        hits_file = self.output_dir / "hits.txt"
        self.hits = []
        
        if not hits_file.exists():
            return
        
        try:
            content = hits_file.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                # Parse format: file:line:snippet
                match = re.match(r"^(.*?):(\d+):(.*)$", line)
                if match:
                    file_path, line_num, snippet = match.groups()
                    self.hits.append((file_path, int(line_num), snippet.strip()))
        except Exception as e:
            self.errors.append(f"Error loading hits: {e}")
    
    def _load_mnemonics(self):
        """Load mnemonics from mnemonic_raw.txt file."""
        mnemonics_file = self.output_dir / "mnemonic_raw.txt"
        self.mnemonics = []
        
        if not mnemonics_file.exists():
            return
        
        try:
            content = mnemonics_file.read_text(encoding="utf-8", errors="ignore")
            # Split by lines and filter empty lines
            self.mnemonics = [line.strip() for line in content.splitlines() if line.strip()]
        except Exception as e:
            self.errors.append(f"Error loading mnemonics: {e}")
    
    def _load_summary(self):
        """Load summary from summary.json file if available."""
        import json
        
        summary_file = self.output_dir / "summary.json"
        self.summary = {}
        
        if not summary_file.exists():
            return
        
        try:
            self.summary = json.loads(summary_file.read_text(encoding="utf-8"))
        except Exception as e:
            self.errors.append(f"Error loading summary: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get basic statistics about the results.
        
        Returns:
            Dictionary with result statistics
        """
        return {
            "total_hits": len(self.hits),
            "total_mnemonics": len(self.mnemonics),
            "unique_files": len(set(hit[0] for hit in self.hits)),
            "errors": len(self.errors)
        }
    
    def filter_hits(self, pattern: str) -> List[Tuple[str, int, str]]:
        """
        Filter hits using regex pattern.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            Filtered list of hits
        """
        if not pattern:
            return self.hits
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = []
            
            for file_path, line_num, snippet in self.hits:
                combined = f"{file_path} {line_num} {snippet}"
                if regex.search(combined):
                    filtered.append((file_path, line_num, snippet))
            
            return filtered
        except re.error:
            # Return all hits if regex is invalid
            return self.hits
    
    def export_hits_tsv(self, output_file: Path, pattern: str = "") -> bool:
        """
        Export hits to TSV file.
        
        Args:
            output_file: Output file path
            pattern: Optional filter pattern
            
        Returns:
            True if export was successful
        """
        import csv
        
        try:
            hits = self.filter_hits(pattern) if pattern else self.hits
            
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(["file", "line", "snippet"])
                
                for file_path, line_num, snippet in hits:
                    writer.writerow([file_path, line_num, snippet])
            
            return True
        except Exception as e:
            self.errors.append(f"Error exporting hits: {e}")
            return False
    
    def get_hits_clipboard_text(self, pattern: str = "") -> str:
        """
        Get hits formatted for clipboard.
        
        Args:
            pattern: Optional filter pattern
            
        Returns:
            Tab-separated text suitable for clipboard
        """
        hits = self.filter_hits(pattern) if pattern else self.hits
        return "\n".join(f"{file_path}\t{line_num}\t{snippet}" 
                        for file_path, line_num, snippet in hits)


class TargetAnalyzer:
    """
    Utility class for analyzing scan targets and providing recommendations.
    """
    
    @staticmethod
    def analyze_target(target_path: str) -> Dict[str, Union[str, bool, int]]:
        """
        Analyze a scan target and provide information about it.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Dictionary with target analysis information
        """
        path = Path(target_path)
        analysis = {
            "path": target_path,
            "exists": path.exists(),
            "type": "unknown",
            "size": 0,
            "requires_mount": False,
            "requires_root": False,
            "recommendations": []
        }
        
        if is_device_path(target_path):
            analysis.update({
                "type": "device",
                "requires_mount": True,
                "requires_root": True,
                "recommendations": [
                    "Enable 'Mit Root (pkexec)' option",
                    "Enable 'Auto-Mount' option"
                ]
            })
        elif path.exists():
            if path.is_file():
                analysis["size"] = path.stat().st_size
                
                if is_image_file(path):
                    analysis.update({
                        "type": "disk_image",
                        "requires_mount": True,
                        "requires_root": True,
                        "recommendations": [
                            "Use 'Datei/Abbild hinzufügen' instead of folder selection",
                            "Enable 'Mit Root (pkexec)' option",
                            "Enable 'Auto-Mount' option"
                        ]
                    })
                elif is_archive_file(path):
                    analysis.update({
                        "type": "archive",
                        "requires_mount": True,
                        "recommendations": [
                            "Enable 'Auto-Mount' option for automatic extraction"
                        ]
                    })
                else:
                    analysis["type"] = "file"
                    
                    # Check file size limits
                    if analysis["size"] > DEFAULT_FILE_SIZE_LIMIT:
                        if analysis["size"] > AGGRESSIVE_FILE_SIZE_LIMIT:
                            analysis["recommendations"].append(
                                f"File is very large ({format_file_size(analysis['size'])}). "
                                "Consider using aggressive mode or check if it's an image file."
                            )
                        else:
                            analysis["recommendations"].append(
                                "File is large. Consider enabling 'Aggressiv' mode for scanning."
                            )
            
            elif path.is_dir():
                analysis["type"] = "directory"
                
                # Estimate directory size (first level only for performance)
                try:
                    total_size = sum(f.stat().st_size for f in path.iterdir() if f.is_file())
                    analysis["size"] = total_size
                    
                    if total_size > 10 * 1024 * 1024 * 1024:  # > 10 GB
                        analysis["recommendations"].append(
                            "Large directory detected. Scan may take considerable time."
                        )
                except Exception:
                    pass
        
        return analysis
    
    @staticmethod
    def get_default_targets(root_path: str) -> List[str]:
        """
        Get default scan targets based on root directory structure.
        
        Args:
            root_path: Root directory path
            
        Returns:
            List of recommended default targets
        """
        root = Path(root_path)
        defaults = []
        
        # Common subdirectories to check
        candidates = [
            "_mount/hitachi_sdc3_ntfs",
            "_recovery", 
            "Software/Collected"
        ]
        
        for candidate in candidates:
            target_path = root / candidate
            if target_path.exists():
                defaults.append(str(target_path))
        
        return defaults