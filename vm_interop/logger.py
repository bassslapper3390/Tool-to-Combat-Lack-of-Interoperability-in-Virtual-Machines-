import logging
import sys
from pathlib import Path
from .config import Config

def setup_logging(config: Config = None):
    """Configure logging for the application."""
    if config is None:
        config = Config()
        
    log_level = getattr(logging, config.get('logging', 'level', 'INFO'))
    log_file = config.get('logging', 'file', 'vm_interop.log')
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers = {
        'vm_interop.converter': logging.INFO,
        'vm_interop.network_analyzer': logging.INFO,
        'vm_interop.gui': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
    return root_logger 