#!/usr/bin/env python3
"""
Wallet Scanner Command Line Interface Main Module

This module provides command line interface functionality for the
Wallet Scanner application when run without GUI.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from ..core.config import APP_NAME, APP_VERSION, APP_DESCRIPTION
try:
    from ..core.scanner import ScannerConfig, ScannerCommand, TargetAnalyzer
except ImportError:
    ScannerConfig = ScannerCommand = TargetAnalyzer = None
from ..core.utils import (
    find_scanner_scripts,
    check_system_requirements,
    format_file_size,
    ensure_config_directories
)


class WalletScannerCLI:
    """
    Command line interface for the Wallet Scanner.
    """
    
    def __init__(self):
        """Initialize the CLI application."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser."""
        parser = argparse.ArgumentParser(
            prog="wallet-scanner",
            description=APP_DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_epilog()
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version=f"{APP_NAME} {APP_VERSION}"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # GUI command (default)
        gui_parser = subparsers.add_parser("gui", help="Launch GUI application (default)")
        
        # Check command
        check_parser = subparsers.add_parser("check", help="Check system requirements")
        
        # List scanners command
        list_parser = subparsers.add_parser("list-scanners", help="List available scanner scripts")
        
        # Analyze targets command
        analyze_parser = subparsers.add_parser("analyze", help="Analyze scan targets")
        analyze_parser.add_argument("targets", nargs="+", help="Targets to analyze")
        
        # Setup command
        setup_parser = subparsers.add_parser("setup", help="Set up configuration directories")
        
        return parser
    
    def _get_epilog(self) -> str:
        """Get epilog text for help message."""
        return f"""
Examples:
  {sys.argv[0]}                    # Launch GUI (default)
  {sys.argv[0]} gui                # Launch GUI explicitly
  {sys.argv[0]} check              # Check system requirements
  {sys.argv[0]} list-scanners      # List available scanner scripts
  {sys.argv[0]} analyze /path/to/target  # Analyze scan target
  {sys.argv[0]} setup              # Set up configuration directories

For GUI usage, simply run without arguments or use the 'gui' command.
"""
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.
        
        Args:
            args: Optional command line arguments (for testing)
            
        Returns:
            Exit code
        """
        parsed_args = self.parser.parse_args(args)
        
        # Default to GUI if no command specified
        if not parsed_args.command:
            return self._run_gui()
        
        # Route to appropriate handler
        handlers = {
            "gui": self._run_gui,
            "check": self._run_check,
            "list-scanners": self._run_list_scanners,
            "analyze": lambda: self._run_analyze(parsed_args.targets),
            "setup": self._run_setup,
        }
        
        handler = handlers.get(parsed_args.command)
        if handler:
            return handler()
        else:
            self.parser.print_help()
            return 1
    
    def _run_gui(self) -> int:
        """Launch the GUI application."""
        try:
            from ..gui.app import main
            return main()
        except ImportError as e:
            print(f"Error: Could not import GUI components: {e}")
            print("Please ensure PyQt6 is installed: pip install PyQt6")
            return 1
        except Exception as e:
            print(f"Error launching GUI: {e}")
            return 1
    
    def _run_check(self) -> int:
        """Check system requirements."""
        print(f"{APP_NAME} {APP_VERSION} - System Requirements Check")
        print("=" * 60)
        
        missing_required, missing_optional = check_system_requirements()
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        min_python = "3.9"
        
        print(f"Python version: {python_version}")
        if sys.version_info < (3, 9):
            print(f"⚠️  Warning: Python {min_python}+ recommended, found {python_version}")
        else:
            print("✅ Python version OK")
        
        print()
        
        # Required packages
        print("Required packages:")
        if not missing_required:
            print("✅ All required packages are available")
        else:
            print("❌ Missing required packages:")
            for package in missing_required:
                print(f"   - {package}")
            print("\nInstall missing packages with:")
            print(f"   sudo apt install {' '.join(missing_required)}")
        
        print()
        
        # Optional packages
        print("Optional packages:")
        if not missing_optional:
            print("✅ All optional packages are available")
        else:
            print("⚠️  Missing optional packages (recommended):")
            for package in missing_optional:
                print(f"   - {package}")
            print("\nInstall optional packages with:")
            print(f"   sudo apt install {' '.join(missing_optional)}")
        
        print()
        
        # Configuration directories
        print("Configuration:")
        if ensure_config_directories():
            print("✅ Configuration directories OK")
        else:
            print("❌ Could not create configuration directories")
        
        # Scanner scripts
        print("\nScanner scripts:")
        scripts = find_scanner_scripts()
        if scripts:
            print(f"✅ Found {len(scripts)} scanner script(s)")
        else:
            print("⚠️  No scanner scripts found")
            print("   Scanner scripts should be placed in:")
            print(f"   {Path.home() / '.local' / 'share' / 'wallet-gui' / 'scripts'}")
        
        return 0 if not missing_required else 1
    
    def _run_list_scanners(self) -> int:
        """List available scanner scripts."""
        print(f"{APP_NAME} - Available Scanner Scripts")
        print("=" * 50)
        
        scripts = find_scanner_scripts()
        
        if not scripts:
            print("No scanner scripts found.")
            print()
            print("Scanner scripts should be placed in:")
            print(f"  {Path.home() / '.local' / 'share' / 'wallet-gui' / 'scripts'}")
            return 1
        
        for i, script in enumerate(scripts, 1):
            print(f"{i:2d}. {script.name}")
            print(f"     Path: {script}")
            
            # Show file info
            stat = script.stat()
            size = format_file_size(stat.st_size)
            print(f"     Size: {size}")
            
            # Check if executable
            if script.suffix == ".sh":
                print(f"     Type: Shell script")
            elif script.suffix == ".py":
                print(f"     Type: Python script")
            
            print()
        
        return 0
    
    def _run_analyze(self, targets: List[str]) -> int:
        """Analyze scan targets."""
        print(f"{APP_NAME} - Target Analysis")
        print("=" * 40)
        
        for i, target in enumerate(targets, 1):
            print(f"\nTarget {i}: {target}")
            print("-" * (len(target) + 20))
            
            analysis = TargetAnalyzer.analyze_target(target)
            
            # Basic info
            print(f"Exists: {'Yes' if analysis['exists'] else 'No'}")
            print(f"Type: {analysis['type'].replace('_', ' ').title()}")
            
            if analysis['size'] > 0:
                print(f"Size: {format_file_size(analysis['size'])}")
            
            # Requirements
            requirements = []
            if analysis['requires_root']:
                requirements.append("Root privileges")
            if analysis['requires_mount']:
                requirements.append("Auto-mount")
            
            if requirements:
                print(f"Requires: {', '.join(requirements)}")
            
            # Recommendations
            if analysis['recommendations']:
                print("\nRecommendations:")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
        
        return 0
    
    def _run_setup(self) -> int:
        """Set up configuration directories."""
        print(f"{APP_NAME} - Setup Configuration")
        print("=" * 40)
        
        from ..core.config import DEFAULT_CONFIG_DIR, DEFAULT_DATA_DIR, DEFAULT_SCRIPTS_DIR
        
        directories = [
            ("Configuration", DEFAULT_CONFIG_DIR),
            ("Data", DEFAULT_DATA_DIR),
            ("Scripts", DEFAULT_SCRIPTS_DIR),
        ]
        
        success = True
        
        for name, directory in directories:
            print(f"\nCreating {name.lower()} directory...")
            print(f"  Path: {directory}")
            
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created successfully")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                success = False
        
        if success:
            print(f"\n✅ Setup completed successfully!")
            print(f"\nNext steps:")
            print(f"1. Place scanner scripts in: {DEFAULT_SCRIPTS_DIR}")
            print(f"2. Run 'wallet-scanner check' to verify installation")
            print(f"3. Launch GUI with 'wallet-scanner' or 'wallet-scanner gui'")
        else:
            print(f"\n❌ Setup failed. Please check permissions and try again.")
        
        return 0 if success else 1


def main():
    """Main entry point for the CLI application."""
    cli = WalletScannerCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())