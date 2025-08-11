#!/usr/bin/env python3
"""
launch_gui_fixed.py — Improved launcher for AmandaMap GUI Analyzer.
Handles warnings, encoding issues, and provides better error handling.
"""

import sys
import subprocess
import warnings
import os

def suppress_warnings():
    """Suppress annoying warnings."""
    warnings.filterwarnings('ignore', message='.*protobuf.*')
    warnings.filterwarnings('ignore', message='.*Protobuf.*')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'sklearn', 'chardet'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install -r requirements_gui.txt")
        return False
    
    return True

def fix_encoding_issues():
    """Fix encoding issues in chat files."""
    try:
        from fix_encoding import fix_chat_files
        print("Checking for encoding issues in chat files...")
        fix_chat_files()
        return True
    except Exception as e:
        print(f"Warning: Could not fix encoding issues: {e}")
        return False

def main():
    """Main launcher function."""
    print("AmandaMap GUI Analyzer Launcher (Fixed Version)")
    print("=" * 50)
    
    # Suppress warnings
    suppress_warnings()
    print("✓ Warnings suppressed")
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        input("Press Enter to exit...")
        return
    
    print("✓ All dependencies found")
    
    # Fix encoding issues
    fix_encoding_issues()
    
    print("Launching AmandaMap GUI Analyzer...")
    
    try:
        # Import and run the GUI
        from amandamap_gui_analyzer import main as gui_main
        gui_main()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("\nTrying alternative launch method...")
        
        try:
            # Try running as subprocess
            subprocess.run([sys.executable, "amandamap_gui_analyzer.py"], check=True)
        except Exception as e2:
            print(f"Alternative launch also failed: {e2}")
            print("\nPlease run manually: python amandamap_gui_analyzer.py")
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
