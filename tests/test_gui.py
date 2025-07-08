import unittest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys
from vm_interop.gui import MainWindow

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        
    def setUp(self):
        self.window = MainWindow()
        
    def test_window_title(self):
        """Test window title is set correctly."""
        self.assertEqual(self.window.windowTitle(), "VM Interoperability Tool")
        
    def test_tab_widget(self):
        """Test tab widget setup."""
        tabs = self.window.findChild(QTabWidget)
        self.assertIsNotNone(tabs)
        self.assertEqual(tabs.count(), 2)
        self.assertEqual(tabs.tabText(0), "VM Conversion")
        self.assertEqual(tabs.tabText(1), "Network Analysis")
        
    def test_file_selection(self):
        """Test file selection dialogs."""
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("test.vmdk", "VM Files (*.vmdk)")
            self.window.select_input_file()
            self.assertEqual(self.window.input_path.text(), "test.vmdk")
            
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("test.qcow2", "VM Files (*.qcow2)")
            self.window.select_output_file()
            self.assertEqual(self.window.output_path.text(), "test.qcow2")
            
    def test_conversion_start(self):
        """Test starting VM conversion."""
        self.window.input_path.setText("test.vmdk")
        self.window.output_path.setText("test.qcow2")
        
        with patch('vm_interop.gui.ConversionWorker') as mock_worker:
            mock_worker.return_value.start = MagicMock()
            self.window.start_conversion()
            mock_worker.return_value.start.assert_called_once()
            
    def test_capture_start(self):
        """Test starting network capture."""
        self.window.capture_output.setText("test.pcap")
        
        with patch('vm_interop.gui.NetworkCaptureWorker') as mock_worker:
            mock_worker.return_value.start = MagicMock()
            self.window.start_capture()
            mock_worker.return_value.start.assert_called_once()
            
    def test_conversion_finished(self):
        """Test handling conversion completion."""
        self.window.conversion_finished(True, "Conversion successful")
        self.assertEqual(self.window.progress.value(), 100)
        self.assertIn("Conversion successful", self.window.log_display.toPlainText())
        
    def test_capture_finished(self):
        """Test handling capture completion."""
        self.window.capture_finished(True, "Capture completed")
        self.assertIn("Capture completed", self.window.network_log.toPlainText())
        
    def test_analysis_start(self):
        """Test starting network analysis."""
        self.window.analysis_input.setText("test.pcap")
        
        with patch('vm_interop.gui.NetworkAnalyzer') as mock_analyzer:
            mock_analyzer.return_value.analyze_migration_traffic.return_value = {
                'total_packets': 1000,
                'total_bytes': 1000000
            }
            mock_analyzer.return_value.generate_report.return_value = True
            
            self.window.start_analysis()
            mock_analyzer.return_value.analyze_migration_traffic.assert_called_once()
            mock_analyzer.return_value.generate_report.assert_called_once()
            
if __name__ == '__main__':
    unittest.main() 