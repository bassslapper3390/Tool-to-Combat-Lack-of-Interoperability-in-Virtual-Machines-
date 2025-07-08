import argparse
import logging
from pathlib import Path
from converter import VMConverter
from network_analyzer import NetworkAnalyzer

def setup_logging():
    """Configure logging for the main script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vm_interop.log'),
            logging.StreamHandler()
        ]
    )

def convert_vm(args):
    """Handle VM conversion."""
    converter = VMConverter()
    success = converter.convert(
        input_path=args.input,
        output_path=args.output,
        input_format=args.input_format,
        output_format=args.output_format
    )
    
    if success:
        logging.info(f"Successfully converted {args.input} to {args.output}")
    else:
        logging.error("Conversion failed")

def analyze_network(args):
    """Handle network analysis."""
    analyzer = NetworkAnalyzer(interface=args.interface)
    
    if args.capture:
        # Capture new traffic
        df = analyzer.capture_traffic(
            duration=args.duration,
            output_file=args.output_file
        )
        logging.info(f"Captured {len(df)} packets")
    
    if args.analyze:
        # Analyze existing capture
        analysis = analyzer.analyze_migration_traffic(args.input_file)
        analyzer.generate_report(analysis, args.report_file)
        logging.info(f"Analysis report generated: {args.report_file}")

def main():
    parser = argparse.ArgumentParser(description='VM Interoperability Tools')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert VM image format')
    convert_parser.add_argument('--input', required=True, help='Input VM image path')
    convert_parser.add_argument('--output', required=True, help='Output VM image path')
    convert_parser.add_argument('--input-format', help='Input format (auto-detected if not specified)')
    convert_parser.add_argument('--output-format', help='Output format (auto-detected if not specified)')
    
    # Network analysis command
    network_parser = subparsers.add_parser('network', help='Network analysis tools')
    network_parser.add_argument('--interface', default='eth0', help='Network interface to capture')
    network_parser.add_argument('--capture', action='store_true', help='Capture new traffic')
    network_parser.add_argument('--analyze', action='store_true', help='Analyze existing capture')
    network_parser.add_argument('--duration', type=int, default=60, help='Capture duration in seconds')
    network_parser.add_argument('--input-file', help='Input capture file for analysis')
    network_parser.add_argument('--output-file', help='Output capture file')
    network_parser.add_argument('--report-file', help='Analysis report file')
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.command == 'convert':
        convert_vm(args)
    elif args.command == 'network':
        analyze_network(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 