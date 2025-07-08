import unittest
import os
import tempfile
from pathlib import Path
from vm_interop.converter import VMConverter
from unittest.mock import patch, MagicMock

class TestVMConverter(unittest.TestCase):
    def setUp(self):
        self.converter = VMConverter()
        self.test_dir = tempfile.mkdtemp()
        self.test_input = "test.vmdk"
        self.test_output = "test.qcow2"
        
    def tearDown(self):
        # Clean up test files
        for file in Path(self.test_dir).glob("*"):
            file.unlink()
        os.rmdir(self.test_dir)
        
    def test_format_detection(self):
        """Test automatic format detection."""
        # Test VMDK detection
        test_file = Path(self.test_dir) / "test.vmdk"
        test_file.touch()
        self.assertEqual(self.converter._detect_format(str(test_file)), "vmdk")
        
        # Test VDI detection
        test_file = Path(self.test_dir) / "test.vdi"
        test_file.touch()
        self.assertEqual(self.converter._detect_format(str(test_file)), "vdi")
        
    def test_conversion_validation(self):
        """Test conversion input validation."""
        # Test missing input file
        with self.assertRaises(FileNotFoundError):
            self.converter.convert(
                input_path="nonexistent.vmdk",
                output_path="output.vdi"
            )
            
    def test_supported_formats(self):
        """Test supported format listing."""
        formats = self.converter.SUPPORTED_FORMATS
        self.assertIn("vmdk", formats)
        self.assertIn("vdi", formats)
        self.assertIn("vhd", formats)
        self.assertIn("vhdx", formats)
        self.assertIn("qcow2", formats)
        self.assertIn("raw", formats)
        
    def test_convert_input_file_not_found(self):
        """Test conversion with non-existent input file."""
        with patch('os.path.exists', return_value=False):
            result = self.converter.convert(
                self.test_input,
                self.test_output,
                "vmdk",
                "qcow2"
            )
            self.assertFalse(result)
            
    def test_convert_ova_to_vmdk(self):
        """Test conversion from OVA to VMDK."""
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            result = self.converter.convert(
                "test.ova",
                self.test_output,
                "ova",
                "vmdk"
            )
            self.assertTrue(result)
            mock_run.assert_called()
            
    def test_convert_vmdk_to_ova(self):
        """Test conversion from VMDK to OVA."""
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            result = self.converter.convert(
                self.test_input,
                "test.ova",
                "vmdk",
                "ova"
            )
            self.assertTrue(result)
            mock_run.assert_called()
            
    def test_convert_disk_format(self):
        """Test direct disk format conversion."""
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            result = self.converter.convert(
                self.test_input,
                self.test_output,
                "vmdk",
                "qcow2"
            )
            self.assertTrue(result)
            mock_run.assert_called()
            
    def test_convert_failure(self):
        """Test conversion failure handling."""
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Conversion failed"
            result = self.converter.convert(
                self.test_input,
                self.test_output,
                "vmdk",
                "qcow2"
            )
            self.assertFalse(result)
            
if __name__ == '__main__':
    unittest.main() 