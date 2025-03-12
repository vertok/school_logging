import logging
import sys
import os
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
    Optimized for multiprocessing environments.
    """
    # Shared file handler path to ensure all processes log to the same file
    _shared_log_file = None
    
    def __init__(self, name: str, verbose: str = 'INFO') -> None:
        self.name = name
        self.level = self._map_log_level(verbose)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # CRITICAL FIX: Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        
        # Remove any existing handlers to prevent duplicate handlers
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        
        # Console handler (colored output)
        ch = logging.StreamHandler()
        ch.setLevel(self.level)
        ch.setFormatter(ColoredFormatter(
            '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
            colored=True
        ))
        logger.addHandler(ch)

        # File handler (all levels, no color)
        # Initialize shared log file if not already done
        if ColoredLogger._shared_log_file is None:
            log_dir = 'logging'
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ColoredLogger._shared_log_file = os.path.join(log_dir, f'logs_{timestamp}.log')
            
        # Use the shared log file path
        # CRITICAL FIX: Use 'a' append mode for multiprocessing compatibility
        fh = logging.FileHandler(ColoredLogger._shared_log_file, mode='a')
        fh.setLevel(logging.DEBUG)  # Always use DEBUG level for files
        fh.setFormatter(ColoredFormatter(
            '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
            colored=False
        ))
        logger.addHandler(fh)

        # Add the CriticalExitHandler
        logger.addHandler(CriticalExitHandler())

        return logger

    def configure_logging(self, module_log_levels=None):
        """
        Configure logging levels for various modules.
        
        Args:
            module_log_levels: Dict of module names and their specific log levels
                              e.g. {"psy_supabase.core.text_generator": "DEBUG"}
        """
        # Set default log levels for third-party libraries
        self._configure_third_party_loggers()
        
        # Apply specific module log levels if provided
        if module_log_levels:
            for module_name, level in module_log_levels.items():
                level_int = self._map_log_level(level)
                module_logger = logging.getLogger(module_name)
                
                # Remove any existing handlers
                for handler in list(module_logger.handlers):
                    module_logger.removeHandler(handler)
                
                module_logger.setLevel(level_int)
                
                # CRITICAL FIX: Also prevent propagation for module loggers
                module_logger.propagate = False
                
                # Make sure module logger has appropriate handlers (console and file)
                # Console handler
                ch = logging.StreamHandler()
                ch.setLevel(level_int)
                ch.setFormatter(ColoredFormatter(
                    '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
                    colored=True
                ))
                module_logger.addHandler(ch)
                
                # File handler - use the shared log file
                # CRITICAL FIX: Use 'a' append mode for multiprocessing compatibility
                fh = logging.FileHandler(ColoredLogger._shared_log_file, mode='a')
                fh.setLevel(logging.DEBUG)  # Always use DEBUG level for files
                fh.setFormatter(ColoredFormatter(
                    '%(asctime)s - %(filename)s - %(name)s - [%(levelname)s] - %(message)s',
                    colored=False
                ))
                module_logger.addHandler(fh)
                
                self.logger.info(f"Set log level for {module_name} to {level}")

    def _configure_third_party_loggers(self):
        """Configure third-party loggers with appropriate log levels."""
        # Set levels for noisy third-party libraries
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('hpack').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('h2').setLevel(logging.WARNING)
        
        # Supabase-related libraries
        logging.getLogger('supabase').setLevel(logging.INFO)
        logging.getLogger('postgrest').setLevel(logging.WARNING)
        logging.getLogger('gotrue').setLevel(logging.WARNING)
        logging.getLogger('realtime').setLevel(logging.WARNING)
        logging.getLogger('storage3').setLevel(logging.WARNING)
        
        # ML-related libraries
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('torch').setLevel(logging.WARNING)
        logging.getLogger('spacy').setLevel(logging.INFO)
        
        # Prevent third-party loggers from propagating to root logger
        for logger_name in ['httpx', 'httpcore', 'hpack', 'urllib3', 'asyncio', 'h2',
                           'supabase', 'postgrest', 'gotrue', 'realtime', 'storage3',
                           'transformers', 'torch', 'spacy']:
            logging.getLogger(logger_name).propagate = False

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
