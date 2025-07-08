# test_setup.py
import os
import subprocess
import sys

def test_environment():
    print("Testing environment setup...")
    
    # Test Python
    print(f"Python version: {sys.version}")
    
    # Test VirtualBox
    try:
        vbox_version = subprocess.check_output(['VBoxManage', '--version']).decode().strip()
        print(f"VirtualBox version: {vbox_version}")
    except:
        print("VirtualBox not found or not working properly")
    
    # Test QEMU
    try:
        qemu_version = subprocess.check_output(['qemu-img', '--version']).decode().strip()
        print(f"QEMU version: {qemu_version}")
    except:
        print("QEMU not found or not working properly")
    
    # Test VMware
    vmware_path = r"C:\Program Files\VMware\VMware Workstation\vmware.exe"
    if os.path.exists(vmware_path):
        print("VMware Workstation found")
    else:
        print("VMware Workstation not found")

if __name__ == "__main__":
    test_environment()