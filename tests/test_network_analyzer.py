import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from vm_interop.network_analyzer import NetworkAnalyzer

class TestNetworkAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = NetworkAnalyzer(interface="eth0")
        self.test_capture_file = "test_capture.csv"
        
    def test_capture_traffic(self):
        """Test traffic capture functionality."""
        with patch('scapy.all.sniff') as mock_sniff:
            # Mock packet data
            mock_packet = MagicMock()
            mock_packet.haslayer.return_value = True
            mock_packet.time = datetime.now().timestamp()
            mock_packet[MagicMock()].src = "192.168.1.1"
            mock_packet[MagicMock()].dst = "192.168.1.2"
            mock_packet[MagicMock()].proto = 6
            mock_packet.__len__.return_value = 1500
            
            # Set up mock sniff to call callback with mock packet
            def mock_sniff_side_effect(**kwargs):
                kwargs['prn'](mock_packet)
                return []
            mock_sniff.side_effect = mock_sniff_side_effect
            
            # Run capture
            df = self.analyzer.capture_traffic(duration=1)
            
            # Verify results
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]['src_ip'], "192.168.1.1")
            self.assertEqual(df.iloc[0]['dst_ip'], "192.168.1.2")
            self.assertEqual(df.iloc[0]['protocol'], 6)
            self.assertEqual(df.iloc[0]['length'], 1500)
            
    def test_analyze_migration_traffic(self):
        """Test migration traffic analysis."""
        # Create test data
        test_data = {
            'timestamp': [
                datetime.now(),
                datetime.now() + timedelta(seconds=1),
                datetime.now() + timedelta(seconds=2)
            ],
            'src_ip': ['192.168.1.1', '192.168.1.1', '192.168.1.1'],
            'dst_ip': ['192.168.1.2', '192.168.1.2', '192.168.1.2'],
            'protocol': [6, 6, 6],
            'length': [1000000, 1000000, 1000000],
            'ttl': [64, 64, 64]
        }
        df = pd.DataFrame(test_data)
        df.to_csv(self.test_capture_file, index=False)
        
        # Run analysis
        analysis = self.analyzer.analyze_migration_traffic(self.test_capture_file)
        
        # Verify results
        self.assertIsInstance(analysis, dict)
        self.assertEqual(analysis['total_packets'], 3)
        self.assertEqual(analysis['total_bytes'], 3000000)
        self.assertEqual(analysis['unique_ips'], 2)
        self.assertIn('protocol_distribution', analysis)
        self.assertIn('traffic_patterns', analysis)
        
        # Clean up
        os.remove(self.test_capture_file)
        
    def test_generate_report(self):
        """Test report generation."""
        test_analysis = {
            'total_packets': 1000,
            'total_bytes': 1000000,
            'unique_ips': 2,
            'protocol_distribution': {6: 800, 17: 200},
            'traffic_patterns': {
                'by_minute': {'2023-01-01 00:00:00': 500000},
                'migration_indicators': {
                    'high_bandwidth': True,
                    'consistent_traffic': True,
                    'long_duration': True
                }
            }
        }
        
        test_report_file = "test_report.txt"
        result = self.analyzer.generate_report(test_analysis, test_report_file)
        
        # Verify report was generated
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_report_file))
        
        # Verify report contents
        with open(test_report_file, 'r') as f:
            content = f.read()
            self.assertIn("1000", content)
            self.assertIn("1000000", content)
            self.assertIn("Yes", content)
            
        # Clean up
        os.remove(test_report_file)
        
if __name__ == '__main__':
    unittest.main() 