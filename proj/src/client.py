# Largely copied from atlascopify by Ian Spangler
# Updated for specific use with this project, and for more general IIIF database workflow development

import requests
import pandas as pd
import logging
import argparse

def validate_uid(uid) -> bool:
    """Validate the UID to IIIF database"""
    pass

def get_metadata(uid) -> dict:
    """Get the metadata of the image from IIIF database"""
    pass

def get_tiff(uid, tiff_path) -> None:
    """Get the TIFF image from IIIF database"""
    pass