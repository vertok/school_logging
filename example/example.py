import argparse
from school_logging.log import ColoredLogger

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

def main() -> None:
    """
    Main function to run the logger example.
    
    It initializes the logger based on the verbosity flag and logs several messages
    with different log levels.
    """
    args = parse_args()

    # Create an instance of ColoredLogger with the desired log level
    log = ColoredLogger('logger', args.verbose)

    # Example usage: Logging messages at different levels
    log.debug("This is a debug message")  # Will be logged if --verbose is set
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message. Program will terminate.")

if __name__ == "__main__":
    main()
