import os
import logging
import pandas as pd
import scapy.all as scapy
from typing import Optional, Dict, Any
from datetime import datetime

class NetworkAnalyzer:
    """Analyzes network traffic during VM migration."""
    
    def __init__(self, interface: Optional[str] = None):
        """
        Initialize network analyzer.
        
        Args:
            interface: Network interface to capture on (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.interface = interface
        
    def capture_traffic(self, duration: int = 60, output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Capture network traffic for specified duration.
        
        Args:
            duration: Capture duration in seconds
            output_file: Path to save capture file (optional)
            
        Returns:
            DataFrame containing captured packets
        """
        try:
            # Start packet capture
            packets = []
            start_time = datetime.now()
            
            def packet_callback(packet):
                if packet.haslayer(scapy.IP):
                    packets.append({
                        'timestamp': datetime.fromtimestamp(packet.time),
                        'src_ip': packet[scapy.IP].src,
                        'dst_ip': packet[scapy.IP].dst,
                        'protocol': packet[scapy.IP].proto,
                        'length': len(packet),
                        'ttl': packet[scapy.IP].ttl
                    })
                    
            # Start sniffing
            scapy.sniff(
                iface=self.interface,
                prn=packet_callback,
                timeout=duration
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(packets)
            
            # Save to file if specified
            if output_file:
                df.to_csv(output_file, index=False)
                
            return df
            
        except Exception as e:
            self.logger.error(f"Traffic capture failed: {str(e)}")
            return pd.DataFrame()
            
    def analyze_migration_traffic(self, capture_file: str) -> Dict[str, Any]:
        """
        Analyze captured traffic for VM migration patterns.
        
        Args:
            capture_file: Path to capture file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load capture data
            df = pd.read_csv(capture_file)
            
            # Basic statistics
            total_packets = len(df)
            total_bytes = df['length'].sum()
            unique_ips = pd.concat([df['src_ip'], df['dst_ip']]).nunique()
            
            # Protocol distribution
            protocol_dist = df['protocol'].value_counts().to_dict()
            
            # Traffic patterns
            df['minute'] = pd.to_datetime(df['timestamp']).dt.floor('min')
            traffic_by_minute = df.groupby('minute')['length'].sum()
            
            # Identify potential migration traffic
            migration_indicators = {
                'high_bandwidth': traffic_by_minute.max() > 1000000,  # 1MB/s threshold
                'consistent_traffic': traffic_by_minute.std() < traffic_by_minute.mean() * 0.5,
                'long_duration': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() > 30
            }
            
            return {
                'total_packets': total_packets,
                'total_bytes': total_bytes,
                'unique_ips': unique_ips,
                'protocol_distribution': protocol_dist,
                'traffic_patterns': {
                    'by_minute': traffic_by_minute.to_dict(),
                    'migration_indicators': migration_indicators
                }
            }
            
        except Exception as e:
            self.logger.error(f"Traffic analysis failed: {str(e)}")
            return {}
            
    def generate_report(self, analysis: Dict[str, Any], output_file: str) -> bool:
        """
        Generate analysis report.
        
        Args:
            analysis: Analysis results dictionary
            output_file: Path to save report
            
        Returns:
            bool: True if report generation successful
        """
        try:
            with open(output_file, 'w') as f:
                f.write("VM Migration Traffic Analysis Report\n")
                f.write("==================================\n\n")
                
                # Basic statistics
                f.write("Basic Statistics:\n")
                f.write(f"Total Packets: {analysis.get('total_packets', 0):,}\n")
                f.write(f"Total Traffic: {analysis.get('total_bytes', 0):,} bytes\n")
                f.write(f"Unique IPs: {analysis.get('unique_ips', 0):,}\n\n")
                
                # Protocol distribution
                f.write("Protocol Distribution:\n")
                for protocol, count in analysis.get('protocol_distribution', {}).items():
                    f.write(f"Protocol {protocol}: {count:,} packets\n")
                f.write("\n")
                
                # Migration indicators
                f.write("Migration Traffic Indicators:\n")
                indicators = analysis.get('traffic_patterns', {}).get('migration_indicators', {})
                f.write(f"High Bandwidth: {'Yes' if indicators.get('high_bandwidth') else 'No'}\n")
                f.write(f"Consistent Traffic: {'Yes' if indicators.get('consistent_traffic') else 'No'}\n")
                f.write(f"Long Duration: {'Yes' if indicators.get('long_duration') else 'No'}\n")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return False 