import logging
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any

# Define log level colors
LOG_COLORS: Dict[str, str] = {
    'DEBUG':    '\033[94m',  # Blue
    'INFO':     '\033[92m',  # Green
    'WARNING':  '\033[93m',  # Yellow
    'ERROR':    '\033[91m',  # Red
    'CRITICAL': '\033[95m'   # Magenta
}

# Reset color
RESET_COLOR: str = '\033[0m'

class CriticalExitHandler(logging.Handler):
    """
    Custom handler that terminates the program when a CRITICAL-level log is emitted.
    """
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.CRITICAL:
            sys.exit(1)

class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', colored: bool = True):
        super().__init__(fmt, datefmt, style)
        self.colored = colored

    def format(self, record: logging.LogRecord) -> str:
        log_color = LOG_COLORS.get(record.levelname, RESET_COLOR)
        message = super().format(record)
        return f"{log_color}{message}{RESET_COLOR}" if self.colored else message

class ColoredLogger:
    """
    A custom logger class that provides colored output and terminates the program on critical errors.
    """
    def __init__(self, name: str, verbose: str = 'INFO') -> None:
        self.name = name
        self.level = self._map_log_level(verbose)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)

        if not logger.handlers:
            # Console handler (colored output)
            logging.basicConfig(level=self.level)
            ch = logging.StreamHandler()
            ch.setLevel(self.level)
            ch.setFormatter(ColoredFormatter(
                '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
                colored=True
            ))
            logger.addHandler(ch)

            # File handler (all levels, no color, saved with timestamp)
            log_dir = 'logging'
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file_path = os.path.join(log_dir, f'logs_{timestamp}.log')
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(ColoredFormatter(
                '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
                colored=False
            ))
            logger.addHandler(fh)

            # Add the CriticalExitHandler
            logger.addHandler(CriticalExitHandler())

        return logger

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs a critical message and raises a CriticalError."""
        self.logger.critical(msg, *args, **kwargs)

    def _map_log_level(self, verbose: str) -> int:
        """
        Maps the verbose string to a logging level integer.

        Args:
            verbose (str): The verbosity level as a string (e.g., 'DEBUG', 'INFO').

        Returns:
            int: Corresponding logging level constant.
        """
        log_level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return log_level_mapping.get(verbose.upper(), logging.INFO)

def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Colored Logger')
    parser.add_argument('--verbose', type=str.upper,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set the logging level (case-insensitive)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    log = ColoredLogger('logger', args.verbose)

    # Example usage
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message. Program will terminate.")
