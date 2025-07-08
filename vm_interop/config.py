import os
import json
from pathlib import Path

class Config:
    """Configuration manager for VM Interoperability Tool."""
    
    DEFAULT_CONFIG = {
        'vmware': {
            'path': r'C:\Program Files\VMware\VMware Workstation',
            'player_path': r'C:\Program Files (x86)\VMware\VMware Player'
        },
        'virtualbox': {
            'path': r'C:\Program Files\Oracle\VirtualBox'
        },
        'qemu': {
            'path': r'C:\Program Files\qemu'
        },
        'network': {
            'default_interface': 'Ethernet',
            'capture_duration': 60,
            'output_dir': 'captures'
        },
        'conversion': {
            'temp_dir': 'temp',
            'output_dir': 'converted'
        },
        'logging': {
            'level': 'INFO',
            'file': 'vm_interop.log'
        }
    }
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()
        
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def get(self, section: str, key: str, default=None):
        """Get configuration value."""
        return self.config.get(section, {}).get(key, default)
        
    def set(self, section: str, key: str, value):
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        
    def create_directories(self):
        """Create necessary directories."""
        dirs = [
            self.get('network', 'output_dir'),
            self.get('conversion', 'temp_dir'),
            self.get('conversion', 'output_dir')
        ]
        
        for dir_path in dirs:
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                
    def validate_paths(self) -> bool:
        """Validate all configured paths."""
        paths = [
            self.get('vmware', 'path'),
            self.get('vmware', 'player_path'),
            self.get('virtualbox', 'path'),
            self.get('qemu', 'path')
        ]
        
        return all(os.path.exists(path) for path in paths if path) 