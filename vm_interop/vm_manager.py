"""
VM Manager module for detecting, listing, and controlling VMs across platforms (VMware, VirtualBox, Hyper-V, KVM).
"""

import subprocess
import re
import platform
import socket
import os
import shutil

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

    def list_virtualbox_vms(self):
        vms = []
        try:
            result = subprocess.run(["VBoxManage", "list", "vms"], capture_output=True, text=True, check=True)
            for line in result.stdout.strip().splitlines():
                match = re.match(r'"(.+?)" \{(.+?)\}', line)
                if match:
                    name, uuid = match.groups()
                    # Get VM state
                    state_result = subprocess.run(["VBoxManage", "showvminfo", name, "--machinereadable"], capture_output=True, text=True)
                    state = 'Unknown'
                    for l in state_result.stdout.splitlines():
                        if l.startswith('VMState='):
                            state = l.split('=')[1].strip('"')
                            break
                    vms.append({
                        'name': name,
                        'status': state,
                        'platform': 'VirtualBox'
                    })
        except FileNotFoundError:
            vms.append({'name': 'Error', 'status': "VirtualBox not available on this system. Skipping...", 'platform': 'VirtualBox'})
        except subprocess.CalledProcessError as e:
            vms.append({'name': 'Error', 'status': f"VBoxManage error: {e.output}", 'platform': 'VirtualBox'})
        except Exception as e:
            vms.append({'name': 'Error', 'status': str(e), 'platform': 'VirtualBox'})
        return vms

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

    def list_vms(self):
        env = self.env
        if env["vbox_available"]:
            return self.list_virtualbox_vms()
        elif env["virsh_available"]:
            return self.list_kvm_vms()
        elif env["os"] == "Windows":
            return self.list_hyperv_vms()
        else:
            return [{"name": "No supported virtualization tools found", "status": "N/A", "platform": "None"}]

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
        info['ip'] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info['ip'] = 'Unknown'
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