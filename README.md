# VM Interoperability Tool

A powerful tool for converting between different virtual machine formats and managing interoperability tasks between VMs and systems.

## Features

- Convert between various VM formats:
  - VMware (VMDK, OVA, OVF)
  - VirtualBox (VDI)
  - Microsoft (VHD, VHDX)
  - QEMU/KVM (QCOW2)
  - Raw disk images
- Interoperability Dashboard with:
  - File sharing between systems/VMs (via SFTP/SSH)
  - Real-time messaging between systems/VMs (TCP-based)
  - System resource monitoring (CPU, RAM, Disk)
  - Static IP assignment for Linux VMs (via SSH)
  - Connectivity verification (ping)
- User-friendly GUI interface
- Detailed conversion and operation logs

## Requirements

- Python 3.8 or higher
- QEMU tools (qemu-img)
- VMware OVF Tool (for OVA/OVF conversion)
- `paramiko` Python package (for SSH/SFTP)
- `psutil` Python package (for monitoring)
- SSH server running on target for file sharing and static IP assignment (OpenSSH on Windows, sshd on Linux/Mac)
- Administrator/root privileges for some operations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ADIR360/Tool-to-Combat-Lack-of-Interoperability-in-Virtual-Machines-.git
cd Tool-to-Combat-Lack-of-Interoperability-in-Virtual-Machines-
```

2. Install the package:
```bash
pip install -e .
```

## Usage

### GUI Application

Launch the GUI application:
```bash
python run_gui.py
```

The GUI provides these main functions:
1. **VM Conversion**: Convert between different VM formats
2. **Interop Dashboard**:
   - **File Sharing**: Send files between systems/VMs using SFTP/SSH. Requires SSH server on the target. On Windows, enable OpenSSH server.
   - **Messaging**: Send and receive real-time messages between systems/VMs. Ensure firewalls allow traffic on the chosen port (default: 12345).
   - **Monitoring**: View real-time CPU, RAM, and disk usage. Requires `psutil`.
   - **Static IP Assignment**: Assign static IPs to Linux VMs (with `/etc/network/interfaces`). Not supported on Windows or systems using NetworkManager.
   - **Connectivity Verification**: Ping between systems/VMs to check network reachability.

> **Note:** The Network Analysis page has been removed from the GUI in this version. All code remains for future restoration if needed.

### Command Line

For batch processing or scripting, you can use the Python API:

```python
from vm_interop import VMConverter

# Convert VM format
converter = VMConverter()
converter.convert(
    input_path="input.vmdk",
    output_path="output.qcow2",
    input_format="vmdk",
    output_format="qcow2"
)
```

## Supported Formats

### Input Formats
- VMware VMDK
- VMware OVA/OVF
- VirtualBox VDI
- Microsoft VHD/VHDX
- QEMU QCOW2
- Raw disk images

### Output Formats
- VMware VMDK
- VMware OVA/OVF
- VirtualBox VDI
- Microsoft VHD/VHDX
- QEMU QCOW2
- Raw disk images

## Platform Notes

- **File Sharing & Static IP**: Requires SSH server on the target. On Windows, enable OpenSSH server via Windows Features.
- **Messaging**: Both sender and receiver must allow traffic on the chosen port (default: 12345). Check firewall settings.
- **Monitoring**: Cross-platform via `psutil`, but some metrics may not be available on all OSes.
- **Static IP Assignment**: Only works on Linux VMs using `/etc/network/interfaces`. Not supported on Windows or with NetworkManager.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- QEMU project for the qemu-img tool
- VMware for the OVF Tool
- Paramiko for SSH/SFTP
- psutil for system monitoring 