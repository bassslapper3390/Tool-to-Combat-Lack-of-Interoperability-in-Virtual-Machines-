# VM Interoperability Tool

A powerful tool for converting between different virtual machine formats and analyzing VM migration traffic.

## Features

- Convert between various VM formats:
  - VMware (VMDK, OVA, OVF)
  - VirtualBox (VDI)
  - Microsoft (VHD, VHDX)
  - QEMU/KVM (QCOW2)
  - Raw disk images
- Analyze network traffic during VM migration
- User-friendly GUI interface
- Detailed conversion and analysis reports

## Requirements

- Python 3.8 or higher
- QEMU tools (qemu-img)
- VMware OVF Tool (for OVA/OVF conversion)
- Administrator/root privileges for network capture

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vm-interop.git
cd vm-interop
```

2. Install the package:
```bash
pip install -e .
```

## Usage

### GUI Application

Launch the GUI application:
```bash
vm-interop
```

The GUI provides two main functions:
1. VM Conversion: Convert between different VM formats
2. Network Analysis: Capture and analyze VM migration traffic

### Command Line

For batch processing or scripting, you can use the Python API:

```python
from vm_interop import VMConverter, NetworkAnalyzer

# Convert VM format
converter = VMConverter()
converter.convert(
    input_path="input.vmdk",
    output_path="output.qcow2",
    input_format="vmdk",
    output_format="qcow2"
)

# Analyze network traffic
analyzer = NetworkAnalyzer(interface="eth0")
df = analyzer.capture_traffic(duration=60, output_file="capture.csv")
analysis = analyzer.analyze_migration_traffic("capture.csv")
analyzer.generate_report(analysis, "report.txt")
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- QEMU project for the qemu-img tool
- VMware for the OVF Tool
- Scapy for network packet capture and analysis 