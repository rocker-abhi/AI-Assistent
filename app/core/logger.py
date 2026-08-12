import os
import time
import logging

class DailyRotatingFileHandler(logging.FileHandler):
    """
    Custom file handler that writes to a new file named with the current date,
    and automatically rolls over at midnight without renaming old files.
    """
    def __init__(self, log_dir: str, base_name: str = "app", backupCount: int = 30, **kwargs):
        self.log_dir = log_dir
        self.base_name = base_name
        self.backupCount = backupCount
        self.current_date = time.strftime("%Y-%m-%d")
        filename = self._get_filename(self.current_date)
        super().__init__(filename, **kwargs)

    def _get_filename(self, date_str: str) -> str:
        return os.path.join(self.log_dir, f"{self.base_name}_{date_str}.log")

    def _cleanup_old_logs(self):
        if self.backupCount <= 0:
            return
        
        # Calculate the cutoff time
        cutoff_time = time.time() - (self.backupCount * 86400)
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.startswith(f"{self.base_name}_") and filename.endswith(".log"):
                    file_path = os.path.join(self.log_dir, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
        except OSError:
            pass

    def emit(self, record):
        new_date = time.strftime("%Y-%m-%d")
        if self.current_date != new_date:
            self.current_date = new_date
            self.close()
            self.baseFilename = os.path.abspath(self._get_filename(self.current_date))
            self.stream = self._open()
            self._cleanup_old_logs()
        super().emit(record)

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
    file_handler = DailyRotatingFileHandler(
        log_dir=log_dir,
        base_name="app",
        backupCount=30,       # Keep logs for 30 days before deleting older ones
        encoding="utf-8"
    )
    # The file handler saves everything (DEBUG and above)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create a default logger instance to be imported across the app
logger = setup_logger()
