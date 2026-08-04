from typing import Callable, ParamSpec, TypeVar, Concatenate
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
import yaml
import logging
import logging.config
import argparse

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
    
# Define type variables for the decorator
P = ParamSpec('P')
T = TypeVar('T')

def verbose_option(func: Callable[Concatenate[bool, P], T]) -> Callable[Concatenate[bool, P], T]:
    @wraps(func)
    def wrapper(verbose: bool = False, *args: P.args, **kwargs: P.kwargs):
        verboness = verbose
        with verbose_context(verbose):
            return func(verbose = verboness, *args, **kwargs)
    return wrapper

################################################################################

def setup_parser():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Allmaps Client")
    parser.add_argument("-id", "--identifier", help="The manifest UID of the image collection to download.", type=str, dest="identifier")
    parser.add_argument("-v", "--verbose", action="store_true", type=bool, dest='verbose', help="Enable verbose logging.")
    
    global args
    args = parser.parse_args()

from client import createDirectoryStructure, resolve_paths, download_images, manifest

command_registry: dict[str, Callable] = {
    'download': download_images,
    'path': resolve_paths,
    'manifest': manifest
}

################################################################################

@verbose_option
def test(verbose: bool = False):
    logging.info('Test message')
    
    if verbose:
        print("Verbose mode is enabled.")
    else:
        print("Verbose mode is disabled.")

def main():
    setup_parser()
    
if __name__ == "__main__":
    main()