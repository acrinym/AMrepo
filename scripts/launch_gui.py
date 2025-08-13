#!/usr/bin/env python3
"""
launch_gui.py — Simple launcher for the AmandaMap GUI Analyzer.
"""

import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'sklearn'
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

def main():
    """Main launcher function."""
    print("AmandaMap GUI Analyzer Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        input("Press Enter to exit...")
        return
    
    print("All dependencies found!")
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
