from typing import Callable
import yaml
import logging
import logging.config
import argparse
from pathlib import Path
from functools import wraps
from contextlib import contextmanager

def setup_logging(verbose: bool = False) -> None:
    log_config = Path(__file__).parent / 'logging_config.yaml'
        
    try:
        with open(log_config, "r") as f:
            config = yaml.safe_load(f)
            
        console_level = "INFO" if verbose else "WARNING"
        config["handlers"]["console"]["level"] = console_level
        
        logging.config.dictConfig(config)
            
    except (ValueError, TypeError, AttributeError, ImportError) as e:
        print("Logging.config.dictConfig() encountered error. Config failed!")
        raise e

    except FileNotFoundError as e:
        print("Logging configuration file not found. Config failed!")
        raise e

################################################################################

# The following context manager is used to temporarily set the logging level based on the verbose flag.
# Wrap all functions that require verbose logging with this context manager to ensure proper logging behavior.   
@contextmanager
def verbose_context(verbose: bool = False):
    setup_logging(verbose)
    try:
        yield
    finally:
        pass

def verbose_option(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, verbose: bool = False, **kwargs):
        verboness = verbose
        with verbose_context(verbose):
            return func(*args, verbose = verboness, **kwargs)
    return wrapper

################################################################################

def setup_parser():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Allmaps Client")
    parser.add_argument("-id", "--identifier", help="The manifest UID of the image collection to download.", type=str, dest="identifier")
    parser.add_argument("-v", "--verbose", action="store_true", type=bool, dest='verbose', help="Enable verbose logging.")
    
    global args
    args = parser.parse_args()

from . import client

command_registry: dict[str, Callable] = {
    'download': client.download_images,
    'path': client.resolve_paths,
    'manifest': client.manifest
}

################################################################################

@verbose_option
def test():
    logging.info('Test message')

def main():
    setup_parser()
    
if __name__ == "__main__":
    main()