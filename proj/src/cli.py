from typing import Callable
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
import yaml
import logging
import logging.config
import argparse
import inspect

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

def cli_wrapper(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, verbose: bool = False, **kwargs):
        verboness = verbose
        with verbose_context(verbose=verboness):
            sig = inspect.signature(func)
            func_params = set(sig.parameters.keys())
            
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in func_params}
            
            return func(verbose=verboness, *args, **filtered_kwargs)
    return wrapper

@cli_wrapper
def test(verbose: bool = False):
    logging.info('Test message')
    
    if verbose:
        print("Verbose mode is enabled.")
    else:
        print("Verbose mode is disabled.")

################################################################################

# Commands are included using a list of tuples, where each tuple contains a function and its corresponding argument specifications. Argument specifications should be in the form of the argument name and a dictionary of keyword arguments to be passed to the add_argument method of the ArgumentParser. This allows for easy addition of new commands and their arguments without modifying the core parser setup logic.
commands: list[tuple[Callable, dict[str, dict]]] = [
    (test, {})
]

def setup_parser():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Allmaps Python. Allows for downloading and processing images from atlases and maps available through the AllMaps API. AllMaps Python is a project of the Leventhal Map and Education Center (LMEC) and uses digital collections available through IIIF. For more information, visit https://www.allmaps.org")
    parser.add_argument("-id", "--identifier", type=str, dest="UID", help="The manifest UID of the image collection to download.")
    parser.add_argument("-v", "--verbose", action="store_true", dest='verbose', help="Enable verbose logging.")
    parser.add_argument("-o", "--output", type=str, dest="output_path", help="Specify the path for function output.")
    parser.add_argument("-i", "--input", type=str, dest="input_path", help="Specify the path for function input.")
    
    subparsers = parser.add_subparsers(title="Client Commands", dest="command", required=True)
    
    for command in commands:
        cmd_name: str = command[0].__name__.replace('_', '').upper()
        cmd_doc: str = command[0].__doc__ or "No description available."
        cmd = subparsers.add_parser(cmd_name, help=cmd_doc)
        cmd.set_defaults(func=command[0])
        
        for arg_name, arg_kwargs in command[1].items():
            cmd.add_argument(f"--{arg_name}", **arg_kwargs)
            
    return parser

################################################################################

def main():
    return NotImplemented
    
if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    args.func(**vars(args))