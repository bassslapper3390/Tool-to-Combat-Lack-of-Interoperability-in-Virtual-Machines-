import os
import sys
import subprocess
from pathlib import Path

def check_vmware_path():
    print("Checking VMware installation and PATH...")
    
    # Common VMware installation paths
    vmware_paths = [
        r"C:\Program Files\VMware\VMware Workstation",
        r"C:\Program Files (x86)\VMware\VMware Player",
        r"C:\Program Files\VMware\VMware Player"
    ]
    
    # Get current PATH
    current_path = os.environ.get('PATH', '').split(os.pathsep)
    
    # Check if any VMware path exists
    vmware_installed = False
    for path in vmware_paths:
        if os.path.exists(path):
            print(f"Found VMware installation at: {path}")
            vmware_installed = True
            
            # Check if this path is in system PATH
            if path not in current_path:
                print(f"Warning: {path} is not in system PATH")
            else:
                print(f"✓ {path} is in system PATH")
    
    if not vmware_installed:
        print("No VMware installation found in common locations")
    
    # Try to run vmware command
    try:
        result = subprocess.run(['vmware', '--version'], 
                              capture_output=True, 
                              text=True)
        print(f"VMware command output: {result.stdout.strip()}")
    except FileNotFoundError:
        print("'vmware' command not found in PATH")

if __name__ == "__main__":
    check_vmware_path() 