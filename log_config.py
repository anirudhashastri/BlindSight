import logging
import os
from datetime import datetime

def setup_logger(module_name):
    """
    Configures logging for a module with both timestamp and latest logs.
    
    Args:
        module_name (str): Name of the module (e.g., 'STT', 'TTS', 'pipeline')
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Generate timestamp for log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create handlers
    # 1. Timestamped log file
    timestamp_handler = logging.FileHandler(f"logs/blindsight_{timestamp}.log")
    timestamp_handler.setFormatter(formatter)
    
    # 2. Latest log file (will be overwritten on each run)
    latest_handler = logging.FileHandler(f"logs/blindsight_{module_name}_latest.log", mode='w')
    latest_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(timestamp_handler)
    logger.addHandler(latest_handler)
    
    return logger