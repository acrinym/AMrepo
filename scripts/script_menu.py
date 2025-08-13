#!/usr/bin/env python3
"""
AMrepo Script Menu
A CLI interface to run all helper scripts
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🔥 AMREPO SCRIPT MENU 🔥")
    print("=" * 60)
    print()

def get_scripts():
    """Get all Python scripts in the scripts directory."""
    scripts_dir = Path(__file__).parent
    scripts = []
    
    for file in scripts_dir.glob("*.py"):
        if file.name != "script_menu.py":
            scripts.append(file)
    
    return sorted(scripts)

def show_menu():
    """Display the script menu."""
    scripts = get_scripts()
    
    print("Available Scripts:")
    print("-" * 40)
    
    for i, script in enumerate(scripts, 1):
        # Get script description from first few lines
        try:
            with open(script, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('"""'):
                    # Read until next """
                    desc = ""
                    for line in f:
                        if '"""' in line:
                            break
                        desc += line.strip() + " "
                    desc = desc.strip()
                else:
                    desc = script.stem
        except:
            desc = script.stem
        
        print(f"{i:2d}. {script.stem}")
        print(f"    {desc[:60]}...")
        print()
    
    print("0. Exit")
    print()

def run_script(script_path):
    """Run a selected script."""
    try:
        print(f"Running {script_path.name}...")
        print("-" * 40)
        
        # Change to the parent directory (AMrepo root) before running
        os.chdir(script_path.parent.parent)
        
        # Run the script
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=False, text=True)
        
        print("-" * 40)
        if result.returncode == 0:
            print(f"✅ {script_path.name} completed successfully")
        else:
            print(f"❌ {script_path.name} failed with exit code {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running {script_path.name}: {e}")
    
    input("\nPress Enter to continue...")

def main():
    while True:
        print_banner()
        show_menu()
        
        try:
            choice = input("Select a script (0 to exit): ").strip()
            
            if choice == "0":
                print("Goodbye! 🔥")
                break
            
            choice_num = int(choice)
            scripts = get_scripts()
            
            if 1 <= choice_num <= len(scripts):
                selected_script = scripts[choice_num - 1]
                run_script(selected_script)
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
        except ValueError:
            print("❌ Please enter a valid number.")
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 🔥")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
