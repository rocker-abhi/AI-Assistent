import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name: str = "friday_app", log_dir: str = "logs") -> logging.Logger:
    """
    Sets up a logger that outputs to the console and to date-rotated log files.
    
    Args:
        name: Name of the logger
        log_dir: Directory where log files will be saved
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if the logger is already initialized
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)

    # Define the log format
    log_format = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - (%(filename)s:%(funcName)s:%(lineno)d) - %(message)s"
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Standard output only needs INFO and above
    console_handler.setFormatter(log_format)

    # 2. File Handler (Date-wise rotation)
    # This will create a new file at midnight every day
    log_file_path = os.path.join(log_dir, "app.log")
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when="midnight",      # Rotate at midnight
        interval=1,           # Every 1 day
        backupCount=30,       # Keep logs for 30 days before deleting older ones
        encoding="utf-8"
    )
    # The file handler saves everything (DEBUG and above)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    
    # Customize the suffix of the rolled files to match a clean date format (e.g. app.log.2023-10-26)
    file_handler.suffix = "%Y-%m-%d"

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create a default logger instance to be imported across the app
logger = setup_logger()
