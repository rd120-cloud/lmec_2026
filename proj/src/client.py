'''
File management and downloading functionality
'''

import requests
from tqdm import tqdm
import logging
from pathlib import Path
from typing import Optional
import json
from src.cli_logging import cli_wrapper

@cli_wrapper
def create_directory_structure(verbose: bool = False, input_path: Optional[str] = None):
    '''
    Create directory structure for AllMaps Python project. This function sets up the necessary directories for storing temporary files, images, annotations, and output data. If an input path is provided, the directories will be created within that path; otherwise, they will be created in the current working directory.
    '''
    if isinstance(input_path, str):
        base_path = Path(input_path) / 'data'
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

class Source:
    def __init__(self, identifier: str):
        self.identifier = identifier
        
        self.all_maps_manifest = requests.get(f'https://annotations.allmaps.org/?url=https://www.digitalcommonwealth.org/search/{self.identifier}/manifest.json').json()
    
    @cli_wrapper
    def get_UID(self):
        logging.info(f"UID: {self.identifier}")
        return self.identifier
    
    @cli_wrapper        
    def get_manifest(self):
        logging.info(self.all_maps_manifest)
        return self.all_maps_manifest
        
    @cli_wrapper
    def download_source(self):
        source_name: str = self.all_maps_manifest[]
        logging.info(f"Beginning to download source files for {source_name}")
        
        # Download any annotations not present in directory
        logging.info(f"\nBeginning to download {len((self.all_maps_manifest)['items'])} annotations...\n")
        for item in tqdm(self.all_maps_manifest['items'], desc="Downloading annotations"):
            all_maps_mapURL = item['id']
            if Path(f'./tmp/annotations/{all_maps_mapURL[-16:]}.json').is_file() == True:
                logging.info(f'Skipping {all_maps_mapURL[-16:]}.json, already exists...')
            else:
                logging.info(f'Downloading annotation {all_maps_mapURL}')
                all_maps_annotation = requests.get(all_maps_mapURL, stream=True).json()
                with open(f'./tmp/annotations/{all_maps_mapURL[-16:]}.json', 'w') as f:
                    json.dump(all_maps_annotation, f)
        
        logging.info("All annotations downloaded!")
        
        # Download any images not present in directory
        logging.info(f"\nBeginning to download {len((self.all_maps_manifest)['items'])} images...\n")
        for item in tqdm(self.all_maps_manifest["items"], desc="Downloading images"):
            img_manifest = item["target"]["source"]["id"]
            img_ID = img_manifest.split("commonwealth:")[1][0:9]
            img_URL=f"https://curator.digitalcommonwealth.org/api/filestreams/image/commonwealth:{img_ID}?show_primary_url=true"
            img_file = f'./tmp/img/{img_ID}.tif'
            if Path(img_file).is_file() == True:
                logging.info(f'Skipping {img_file}, already exists...')
            else:
                logging.info(f'Downloading image {img_manifest}')
                image_request = requests.get(img_URL, stream=True)
                response = image_request.json()
                img = requests.get(response['file_set']['image_primary_url'])
                with open(img_file, 'wb') as fd:
                    for chunk in img.iter_content(chunk_size=128):
                        fd.write(chunk)
    
        logging.info("All images downloaded!")
        
        # Create tileset.json template
    
        logging.info("Creating template `tileset.json` file...")
    
        template = requests.get("https://raw.githubusercontent.com/bplmaps/atlascope-utilities/master/modern-workflow/template.json").json()
        tileset = open('output/tileset.json', 'w+')
        tileset.write(json.dumps(template, indent=2))
        tileset.close()
    
        logging.info("Template `tileset.json` file created in `output` directory!\n")