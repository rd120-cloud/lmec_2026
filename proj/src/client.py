# Based on atlascopify.py by Ian Spangler
# Accessible at https://github.com/bplmaps/atlascope-utilities/tree/master/modern-workflow
# Updated for specific use with this project, and for more general IIIF database workflow development

import argparse
import logging
import json
import yaml
import requests
import pandas as pd

# Configure parsing and logging

parser = argparse.ArgumentParser(description='Tools to help in the process of geotransforming urban atlases.')
parser.add_argument('--step', metavar='{download-inputs, allmaps-transform, warp-plates, mosaic-plates, create-xyz, write-extents, write-wasabi}', type=str, 
                    help='steps to execute (default: download-inputs)', default='download-inputs', dest='step')
parser.add_argument('-id', '--identifier', type=str, 
                    help='commonwealth id', dest='identifier')
args = parser.parse_args()

with open('log_config.yaml', 'r') as f:
    cfg = yaml.load(f)
    
logging.config.dictConfig(cfg)
logger = logging.getLogger('client')

def proceed(nextFunction, *args, **kwargs):
    choice = input(f"Do you want to proceed to {nextFunction.__name__}? (y/n): ").strip().lower()
    if choice == "y":
        nextFunction(*args, **kwargs)