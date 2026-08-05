import requests
import logging
from pathlib import Path
from typing import Optional
import json
from src.cli_logging import cli_wrapper

@cli_wrapper
def create_directory_structure(verbose: bool = False, output_path: Optional[str] = None):
    if isinstance(output_path, str):
        base_path = Path(output_path) / 'data'
    else:
        base_path = Path('./data')
    
    directories: list[Path] = [
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

@cli_wrapper
def resolve_paths(verbose: bool = False, output_path: Optional[str] = None):
    return NotImplemented

@cli_wrapper
def download_images(identifier, verbose: bool = False):
    """
    Downloads images from IIIF given the manifest UID and saves them to the specified output path.

    Args:
        identifier (str): The manifest UID of the image collection to download.
    """
    global manifestUID
    manifestUID = identifier
    logging.info(f'UID:{manifestUID}')
    
    global allmapsManifest
    allmapsManifest = requests.get(f'https://annotations.allmaps.org/?url=https://www.digitalcommonwealth.org/search/{identifier}/manifest.json').json()

@cli_wrapper
def manifest(verbose: bool = False):
    if verbose:
        print(allmapsManifest)
    else:
        print(manifestUID)