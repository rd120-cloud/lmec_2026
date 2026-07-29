from typing import Optional
import yaml
import logging
import logging.config
import argparse
from pathlib import Path
import functools
from contextlib import contextmanager

def setup_logging(verbose: bool = False) -> None:
    log_config = Path(__file__).parent / 'logging_config.yaml'
        
    try:
        with open(log_config, "r") as f:
            config = yaml.safe_load(f)
            
        console_level = "INFO" if verbose else "WARNING"
        config["handlers"]["console"]["level"] = console_level
        
        logging.config.dictConfig(config)
        
        print(f"Logging configured successfully using: {log_config}")
            
    except (ValueError, TypeError, AttributeError, ImportError) as e:
        print("Logging.config.dictConfig() encountered error. Config failed!")
        raise e

    except FileNotFoundError as e:
        print("Logging configuration file not found. Config failed!")
        raise e

# The following context manager is used to temporarily set the logging level based on the verbose flag.
# Wrap all functions that require verbose logging with this context manager to ensure proper logging behavior.   
@contextmanager
def verbose_context(verbose: bool):
    setup_logging(verbose)
    try:
        yield
    finally:
        pass

def verbose_option(func):
    @functools.wraps(func)
    def wrapper(*args, verbose: bool = False, **kwargs):
        with verbose_context(verbose):
            return func(*args, **kwargs)
    return wrapper

def setup_parser():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Allmaps Client")
    parser.add_argument("-id", "--identifier", help="The manifest UID of the image collection to download.", type=str, dest="identifier")
    parser.add_argument("-o", "--output-path", help="The local file path for the data directories.", type=str, dest="output_path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--path", help="The local file path for the data directories.")
    
    global args
    args = parser.parse_args()

@verbose_option
def createDirectoryStructure(output_path: Optional[str] = None):
    if isinstance(output_path, str):
        base_path = Path(output_path) / 'data'
    else:
        base_path = Path('./data')
    
    directories = [
        base_path / 'tmp',
        base_path / 'tmp' / 'img',
        base_path / 'tmp' / 'annotations',
        base_path / 'tmp' / 'annotations' / 'transformed',
        base_path / 'tmp' / 'warped',
        base_path / 'output',
    ]
    for directory in directories:
        if directory.exists():
            logging.info(f"Directory already exists: {directory}")
        else:
            logging.info(f"Creating directory: {directory}")
            directory.mkdir(parents=True)
    
def main():
    setup_parser()
    
if __name__ == "__main__":
    main()