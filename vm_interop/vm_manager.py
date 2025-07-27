"""
VM Manager module for detecting, listing, and controlling VMs across platforms (VMware, VirtualBox, Hyper-V, KVM).
"""

import subprocess
import re
import platform
import socket
import os
import shutil
import plistlib

def detect_environment():
    env = {
        "os": platform.system(),
        "arch": platform.machine(),
        "vbox_available": shutil.which("VBoxManage") is not None,
        "virsh_available": shutil.which("virsh") is not None,
        "qemu_available": shutil.which("qemu-system-x86_64") is not None,
    }
    return env

class VMManager:
    def __init__(self):
        self.env = detect_environment()

    def list_kvm_vms(self):
        # Stub: real implementation would use libvirt
        try:
            import libvirt
            conn = libvirt.open("qemu:///system")
            domains = conn.listAllDomains()
            vms = []
            for dom in domains:
                vms.append({
                    "name": dom.name(),
                    "status": "Running" if dom.isActive() else "Shut off",
                    "platform": "KVM"
                })
            return vms
        except ImportError:
            return [{"name": "Error", "status": "libvirt not installed. KVM support unavailable.", "platform": "KVM"}]
        except Exception as e:
            return [{"name": "Error", "status": str(e), "platform": "KVM"}]

    def list_hyperv_vms(self):
        # Stub: real implementation would use PowerShell
        try:
            output = subprocess.check_output(
                ["powershell", "-Command", "Get-VM | Format-Table Name, State"],
                shell=True
            ).decode()
            # Parse output here if needed
            return [{"name": "HyperV VM", "status": "Unknown", "platform": "Hyper-V"}]
        except Exception as e:
            return [{"name": "Error", "status": str(e), "platform": "Hyper-V"}]

    def list_utm_vms(self):
        import os
        utm_dir = os.path.expanduser('~/Library/Containers/com.utmapp.UTM/Data/Documents/')
        vms = []
        if os.path.exists(utm_dir):
            for entry in os.listdir(utm_dir):
                if entry.endswith('.utm'):
                    utm_path = os.path.join(utm_dir, entry)
                    config_path = os.path.join(utm_path, 'config.plist')
                    name = entry[:-4]
                    status = 'Unknown'
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'rb') as f:
                                config = plistlib.load(f)
                                if 'name' in config:
                                    name = config['name']
                        except Exception:
                            pass
                    vms.append({'name': name, 'status': status})
        return vms

    def list_vms(self):
        env = self.env
        vms = []
        # Remove VirtualBox VMs: do not call list_virtualbox_vms()
        # if env["vbox_available"]:
        #     vms.extend(self.list_virtualbox_vms())
        if env["virsh_available"]:
            vms.extend(self.list_kvm_vms())
        if env["os"] == "Windows":
            vms.extend(self.list_hyperv_vms())
        # Add UTM VMs on macOS
        if env["os"] == "Darwin":
            vms.extend(self.list_utm_vms())
        if not vms:
            vms.append({"name": "No supported virtualization tools found", "status": "N/A"})
        return vms

    def get_environment_info(self):
        env = self.env
        if env["vbox_available"]:
            tool = "VirtualBox"
        elif env["virsh_available"]:
            tool = "KVM/libvirt"
        elif env["os"] == "Windows":
            tool = "Hyper-V"
        else:
            tool = "None"
        return f"Detected Platform: {env['os']} ({env['arch']}), using {tool}."

    def start_vm(self, vm_id):
        """Start a VM by its identifier."""
        pass

    def stop_vm(self, vm_id):
        """Stop a VM by its identifier."""
        pass

    def get_vm_info(self, vm_name):
        """Get detailed information about a VirtualBox VM by name."""
        info = {'vm_name': vm_name, 'platform': 'VirtualBox'}
        try:
            result = subprocess.run(["VBoxManage", "showvminfo", vm_name, "--machinereadable"], capture_output=True, text=True)
            lines = result.stdout.strip().splitlines()
            for line in lines:
                if line.startswith('VMState='):
                    info['status'] = line.split('=')[1].strip('"')
                elif line.startswith('memory='):
                    info['ram'] = f"{line.split('=')[1]}MB"
                elif line.startswith('ostype='):
                    info['os'] = line.split('=')[1].strip('"')
                elif line.startswith('GuestIP=') or line.startswith('GuestIP0='):
                    ip = line.split('=')[1].strip('"')
                    if ip:
                        info['ip'] = ip
        except Exception as e:
            info['status'] = f"Error: {e}"
        return info

def get_machine_info():
    info = {
        'type': 'host',
        'os': platform.system(),
        'os_version': platform.version(),
        'hostname': socket.gethostname(),
        'ip': None,
        'vm_platform': None
    }
    # Try to get IP address
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and ip != 'Unknown':
            info['ip'] = ip
        else:
            info['ip'] = ''
    except Exception:
        info['ip'] = ''
    # Try to detect if running inside a VM (Linux/Mac)
    vm_type = None
    if info['os'] in ['Linux', 'Darwin']:
        try:
            if os.path.exists('/sys/class/dmi/id/product_name'):
                with open('/sys/class/dmi/id/product_name') as f:
                    prod = f.read().strip()
                    if 'VirtualBox' in prod:
                        vm_type = 'VirtualBox'
                    elif 'VMware' in prod:
                        vm_type = 'VMware'
                    elif 'KVM' in prod or 'QEMU' in prod:
                        vm_type = 'KVM/QEMU'
            # UTM is QEMU-based, so will show as QEMU
        except Exception:
            pass
    elif info['os'] == 'Windows':
        try:
            import subprocess
            result = subprocess.run(['wmic', 'computersystem', 'get', 'model'], capture_output=True, text=True)
            if 'VirtualBox' in result.stdout:
                vm_type = 'VirtualBox'
            elif 'VMware' in result.stdout:
                vm_type = 'VMware'
            elif 'KVM' in result.stdout or 'QEMU' in result.stdout:
                vm_type = 'KVM/QEMU'
        except Exception:
            pass
    if vm_type:
        info['type'] = 'vm'
        info['vm_platform'] = vm_type
    return info 