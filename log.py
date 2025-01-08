"""
This module defines a custom logger class, `ColoredLogger`, that provides colored
log output to the console. It uses ANSI escape codes to color the log messages
based on their severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

Additionally, the `ColoredLogger` is designed to terminate the program immediately
when a message with a CRITICAL log level is emitted. This behavior is implemented
by raising a custom exception, `CriticalError`, in the `critical()` method.

The module also includes a custom logging handler, `CriticalExitHandler`, which
can be used as an alternative to raising an exception. This handler will
terminate the program when a CRITICAL log message is received.

Usage:

    from logger import ColoredLogger

    # Create a logger instance
    log = ColoredLogger(__name__)

    # Log messages with different levels
    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message. The program will terminate.")

The module can also be used directly as a script. In this case, it will parse
command-line arguments to set the logging level and demonstrate the logger's usage.
"""

import logging
import sys
import argparse
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
        """
        Handles the log record. If the record's level is CRITICAL or higher, terminates the program.

        Args:
            record (logging.LogRecord): The log record.
        """
        if record.levelno >= logging.CRITICAL:
            # Terminate the program
            sys.exit(1)

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_color: str = LOG_COLORS.get(record.levelname, RESET_COLOR)
        message: str = super().format(record)
        return f"{log_color}{message}{RESET_COLOR}"

class ColoredLogger:
    """
    A custom logger class that provides colored output and terminates the program on critical errors.
    """
    def __init__(self,
                 name: str,
                 verbose_level_str: str = 'INFO'
                 ) -> None:
        """
        Initializes the ColoredLogger with a name and optional verbosity level.

        Args:
            name (str): The name of the logger.
            verbose_level_str (str): String representing the logging level ('DEBUG', 'INFO', etc.).
        """
        self.name: str = name
        self.verbose_level_str: str = verbose_level_str
        self.verbose_level: int = getattr(logging, self.verbose_level_str.upper(), logging.INFO)
        self.logger: logging.Logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Sets up and returns the logger instance.
        """
        logger: logging.Logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)  # Set to lowest level to handle all levels

        # Check if the logger already has handlers to avoid duplicate logs
        if not logger.handlers:
            # Create console handler and set level based on verbose_level
            ch: logging.StreamHandler = logging.StreamHandler()
            ch.setLevel(self.verbose_level)

            # Create formatter and add it to the handler
            formatter: logging.Formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)

            # Add handler to the logger
            logger.addHandler(ch)

            # Add the CriticalExitHandler
            critical_handler: CriticalExitHandler = CriticalExitHandler()
            logger.addHandler(critical_handler)

        return logger

    def debug(self,
              msg: str,
              *args: Any,
              **kwargs: Any
              ) -> None:
        """Logs a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self,
             msg: str,
             *args: Any,
             **kwargs: Any
             ) -> None:
        """Logs an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self,
                msg: str,
                *args: Any,
                **kwargs: Any
                ) -> None:
        """Logs a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self,
              msg: str,
              *args: Any,
              **kwargs: Any
              ) -> None:
        """Logs an error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self,
                 msg: str,
                 *args: Any,
                 **kwargs: Any
                 ) -> None:
        """
        Logs a critical message and raises a CriticalError.
        """
        self.logger.critical(msg, *args, **kwargs)

def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Colored Logger')
    parser.add_argument('--verbose', type=str.upper, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        help='Set the logging level (case-insensitive)')
    args: argparse.Namespace = parser.parse_args()
    return args

if __name__ == "__main__":
    args: argparse.Namespace = parse_args()
    log: ColoredLogger = ColoredLogger(__name__, args.verbose)

    # Example usage
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message. Program will terminate.")
