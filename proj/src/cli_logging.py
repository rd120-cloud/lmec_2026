from pathlib import Path
from functools import wraps
import yaml
import logging
import logging.config
from contextlib import contextmanager
from functools import wraps
from typing import Callable
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

# Test CLI functionality
@cli_wrapper
def test(verbose: bool = False, **kwargs):
    logging.info('Test message')
    
    if verbose:
        print("Verbose mode is enabled.")
    else:
        print("Verbose mode is disabled.")
        
    print(**kwargs)