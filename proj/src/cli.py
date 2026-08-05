from typing import Callable
import argparse

from src.cli_logging import cli_wrapper, setup_logging, test
from src.client import create_directory_structure
# Commands are included using a list of tuples, where each tuple contains a function, command line name, and its corresponding argument specifications. Argument specifications should be in the form of the argument name and a dictionary of keyword arguments to be passed to the add_argument method of the ArgumentParser. This allows for easy addition of new commands and their arguments without modifying the core parser setup logic.
commands: list[tuple[Callable, str, dict[str, dict]]] = [
    (test, 'test', {}),
    (create_directory_structure, 'cdir', {})
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
        cmd_name: str = command[1].upper()
        cmd_doc: str = f"{command[0].__name__}: " + (command[0].__doc__ or "No description available.")
        cmd = subparsers.add_parser(cmd_name, help=cmd_doc)
        cmd.set_defaults(func=command[0])
        
        for arg_name, arg_kwargs in command[2].items():
            cmd.add_argument(f"--{arg_name}", **arg_kwargs)
            
    return parser

################################################################################

def main():
    parser = setup_parser()
    args = parser.parse_args()
    args.func(**vars(args))
    
if __name__ == "__main__":
    main()