import os
import subprocess
import logging
from typing import Optional, List, Dict
import tempfile
import shutil

class VMConverter:
    """Handles VM format conversion between different virtualization platforms."""
    
    SUPPORTED_FORMATS = {
        'vmdk': 'VMware Virtual Disk',
        'vdi': 'VirtualBox Virtual Disk',
        'vhd': 'Microsoft Virtual Hard Disk',
        'vhdx': 'Microsoft Virtual Hard Disk v2',
        'qcow2': 'QEMU Copy On Write v2',
        'raw': 'Raw Disk Image',
        'ova': 'Open Virtual Appliance',
        'ovf': 'Open Virtualization Format'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the converter."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vm_converter.log'),
                logging.StreamHandler()
            ]
        )
    
    def convert(self, input_path: str, output_path: str, input_format: str, output_format: str) -> bool:
        """
        Convert VM from one format to another.
        Returns True if successful, False otherwise. Logs errors.
        """
        try:
            if not os.path.exists(input_path):
                self.logger.error(f"Input file not found: {input_path}")
                return False
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if input_format == "ova" or input_format == "ovf":
                return self._convert_ova_ovf(input_path, output_path, output_format)
            elif output_format == "ova" or output_format == "ovf":
                return self._convert_to_ova_ovf(input_path, output_path, input_format)
            else:
                return self._convert_disk_format(input_path, output_path, input_format, output_format)
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            return False
            
    def _convert_ova_ovf(self, input_path: str, output_path: str, output_format: str) -> bool:
        """Convert from OVA/OVF to other formats."""
        try:
            temp_vmdk = os.path.splitext(output_path)[0] + "_temp.vmdk"
            ovftool_cmd = ["ovftool", input_path, temp_vmdk]
            result = subprocess.run(ovftool_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"ovftool failed: {result.stderr}")
                return False
            success = self._convert_disk_format(temp_vmdk, output_path, "vmdk", output_format)
            if os.path.exists(temp_vmdk):
                os.remove(temp_vmdk)
            return success
        except Exception as e:
            self.logger.error(f"OVA/OVF conversion failed: {str(e)}")
            return False
            
    def _convert_to_ova_ovf(self, input_path: str, output_path: str, input_format: str) -> bool:
        """Convert to OVA/OVF format."""
        try:
            if input_format != "vmdk":
                temp_vmdk = os.path.splitext(output_path)[0] + "_temp.vmdk"
                success = self._convert_disk_format(input_path, temp_vmdk, input_format, "vmdk")
                if not success:
                    return False
                input_path = temp_vmdk
            ovftool_cmd = ["ovftool", input_path, output_path]
            result = subprocess.run(ovftool_cmd, capture_output=True, text=True)
            if input_format != "vmdk" and os.path.exists(temp_vmdk):
                os.remove(temp_vmdk)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Conversion to OVA/OVF failed: {str(e)}")
            return False
            
    def _convert_disk_format(self, input_path: str, output_path: str, input_format: str, output_format: str) -> bool:
        """Convert between disk formats using qemu-img."""
        try:
            qemu_cmd = ["qemu-img", "convert", "-f", input_format, "-O", output_format, input_path, output_path]
            result = subprocess.run(qemu_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"qemu-img failed: {result.stderr}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Disk format conversion failed: {str(e)}")
            return False
    
    def _detect_format(self, file_path: str) -> str:
        """Detect the format of a virtual machine image."""
        extension = os.path.splitext(file_path)[1].lower().lstrip('.')
        if extension in self.SUPPORTED_FORMATS:
            return extension
        return 'raw'  # Default to raw if format is unknown
    
    def _can_convert_directly(self, input_format: str, output_format: str) -> bool:
        """Check if direct conversion is possible between formats."""
        # Add logic to determine if direct conversion is possible
        return True  # Simplified for now
    
    def _convert_to_raw(self, input_path: str, output_path: str, input_format: str) -> bool:
        """Convert any format to RAW format."""
        try:
            if input_format == 'vmdk':
                self._vmdk_to_raw(input_path, output_path)
            elif input_format == 'vdi':
                self._vdi_to_raw(input_path, output_path)
            elif input_format == 'vhd':
                self._vhd_to_raw(input_path, output_path)
            elif input_format == 'vhdx':
                self._vhdx_to_raw(input_path, output_path)
            elif input_format == 'qcow2':
                self._qcow2_to_raw(input_path, output_path)
            else:
                raise ValueError(f"Unsupported input format: {input_format}")
            return True
        except Exception as e:
            self.logger.error(f"Conversion to RAW failed: {str(e)}")
            return False
    
    def _convert_from_raw(self, input_path: str, output_path: str, output_format: str) -> bool:
        """Convert from RAW format to any other format."""
        try:
            if output_format == 'vmdk':
                self._raw_to_vmdk(input_path, output_path)
            elif output_format == 'vdi':
                self._raw_to_vdi(input_path, output_path)
            elif output_format == 'vhd':
                self._raw_to_vhd(input_path, output_path)
            elif output_format == 'vhdx':
                self._raw_to_vhdx(input_path, output_path)
            elif output_format == 'qcow2':
                self._raw_to_qcow2(input_path, output_path)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            return True
        except Exception as e:
            self.logger.error(f"Conversion from RAW failed: {str(e)}")
            return False
    
    def _vmdk_to_raw(self, input_path: str, output_path: str):
        """Convert VMDK to RAW using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'vmdk',
            '-O', 'raw',
            input_path,
            output_path
        ], check=True)
    
    def _raw_to_vmdk(self, input_path: str, output_path: str):
        """Convert RAW to VMDK using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'raw',
            '-O', 'vmdk',
            input_path,
            output_path
        ], check=True)
    
    def _vdi_to_raw(self, input_path: str, output_path: str):
        """Convert VDI to RAW using VBoxManage."""
        subprocess.run([
            'VBoxManage', 'clonehd',
            input_path,
            output_path,
            '--format', 'RAW'
        ], check=True)
    
    def _raw_to_vdi(self, input_path: str, output_path: str):
        """Convert RAW to VDI using VBoxManage."""
        subprocess.run([
            'VBoxManage', 'convertfromraw',
            input_path,
            output_path,
            '--format', 'VDI'
        ], check=True)
    
    def _vhd_to_raw(self, input_path: str, output_path: str):
        """Convert VHD to RAW using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'vhd',
            '-O', 'raw',
            input_path,
            output_path
        ], check=True)
    
    def _raw_to_vhd(self, input_path: str, output_path: str):
        """Convert RAW to VHD using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'raw',
            '-O', 'vhd',
            input_path,
            output_path
        ], check=True)
    
    def _vhdx_to_raw(self, input_path: str, output_path: str):
        """Convert VHDX to RAW using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'vhdx',
            '-O', 'raw',
            input_path,
            output_path
        ], check=True)
    
    def _raw_to_vhdx(self, input_path: str, output_path: str):
        """Convert RAW to VHDX using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'raw',
            '-O', 'vhdx',
            input_path,
            output_path
        ], check=True)
    
    def _qcow2_to_raw(self, input_path: str, output_path: str):
        """Convert QCOW2 to RAW using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'qcow2',
            '-O', 'raw',
            input_path,
            output_path
        ], check=True)
    
    def _raw_to_qcow2(self, input_path: str, output_path: str):
        """Convert RAW to QCOW2 using qemu-img."""
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'raw',
            '-O', 'qcow2',
            input_path,
            output_path
        ], check=True) 