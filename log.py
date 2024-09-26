"""school module with logging"""

import logging

# Define log level colors
LOG_COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m'  # Magenta
}

# Reset color
RESET_COLOR = '\033[0m'


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, RESET_COLOR)
        message = super().format(record)
        return f"{log_color}{message}{RESET_COLOR}"


def setup_logger(_verbose_level):
    # Create logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)  # Set to lowest level to handle all levels

    # Create console handler and set level based on _verbose_level
    ch = logging.StreamHandler()
    ch.setLevel(_verbose_level)

    # Create formatter and add it to the handler
    formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add handler to the logger
    _logger.addHandler(ch)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Colored Logger')
    parser.add_argument('--verbose', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Set the logging level')

    args = parser.parse_args()
    return args.verbose


def config_logger():
    verbose_level_str = parse_args()
    verbose_level = getattr(logging, verbose_level_str.upper(), logging.INFO)
    setup_logger(verbose_level)
    logger = logging.getLogger('ui')
    logger.debug("verbose level was set to %s", verbose_level)
    return logger


if __name__ == "__main__":
    verbose_level_str = parse_args()
    verbose_level = getattr(logging, verbose_level_str.upper(), logging.INFO)

    setup_logger(verbose_level)

    # Example usage
    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
