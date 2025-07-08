import os
import subprocess
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VMConversionTest:
    def __init__(self):
        self.test_dir = Path("test_vms")
        self.test_dir.mkdir(exist_ok=True)
        
    def create_test_vm(self):
        """Create a test VM in VirtualBox"""
        logger.info("Creating test VM...")
        
        # Create a 10GB VDI disk (size in MB, use absolute path with forward slashes)
        vdi_path = (self.test_dir / "test.vdi").resolve()
        vdi_path_str = str(vdi_path).replace('\\', '/')
        logger.info(f"VDI path: {vdi_path_str}")
        quoted_vdi_path = f'"{vdi_path_str}"'
        try:
            subprocess.run([
                'VBoxManage', 'createhd',
                '--filename', vdi_path_str,
                '--size', '10240'
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"VBoxManage createhd failed: {e.stderr if hasattr(e, 'stderr') else e}")
            raise
        
        # Create a VM
        subprocess.run([
            'VBoxManage', 'createvm',
            '--name', 'TestVM',
            '--ostype', 'Ubuntu_64',
            '--register'
        ], check=True)
        
        # Add SATA controller
        subprocess.run([
            'VBoxManage', 'storagectl', 'TestVM',
            '--name', 'SATA Controller',
            '--add', 'sata',
            '--controller', 'IntelAhci'
        ], check=True)
        
        # Attach the disk
        subprocess.run([
            'VBoxManage', 'storageattach', 'TestVM',
            '--storagectl', 'SATA Controller',
            '--port', '0',
            '--device', '0',
            '--type', 'hdd',
            '--medium', vdi_path_str
        ], check=True)
        
        logger.info("Test VM created successfully")
        return vdi_path
        
    def convert_to_vmdk(self, input_path):
        """Convert VDI to VMDK"""
        logger.info("Converting to VMDK...")
        output_path = self.test_dir / "test.vmdk"
        subprocess.run([
            'VBoxManage', 'clonehd',
            str(input_path),
            str(output_path),
            '--format', 'VMDK'
        ], check=True)
        logger.info("Conversion to VMDK completed")
        return output_path
        
    def convert_to_vhd(self, input_path):
        """Convert VDI to VHD"""
        logger.info("Converting to VHD...")
        output_path = self.test_dir / "test.vhd"
        subprocess.run([
            'qemu-img', 'convert',
            '-f', 'vdi',
            '-O', 'vhd',
            str(input_path),
            str(output_path)
        ], check=True)
        logger.info("Conversion to VHD completed")
        return output_path
        
    def verify_conversion(self, file_path):
        """Verify the converted file"""
        logger.info(f"Verifying {file_path}...")
        if file_path.suffix == '.vmdk':
            subprocess.run(['VBoxManage', 'showhdinfo', str(file_path)], check=True)
        elif file_path.suffix == '.vhd':
            subprocess.run(['qemu-img', 'info', str(file_path)], check=True)
        logger.info("Verification completed")
        
    def cleanup(self):
        """Clean up test resources"""
        logger.info("Cleaning up...")
        try:
            # Delete the VM
            subprocess.run(['VBoxManage', 'unregistervm', 'TestVM', '--delete'], check=True)
            # Delete test files
            for file in self.test_dir.glob('*'):
                file.unlink()
            self.test_dir.rmdir()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

def main():
    test = VMConversionTest()
    try:
        # Create test VM
        vdi_path = test.create_test_vm()
        
        # Convert to different formats
        vmdk_path = test.convert_to_vmdk(vdi_path)
        vhd_path = test.convert_to_vhd(vdi_path)
        
        # Verify conversions
        test.verify_conversion(vmdk_path)
        test.verify_conversion(vhd_path)
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        # Clean up
        test.cleanup()

if __name__ == "__main__":
    main() 