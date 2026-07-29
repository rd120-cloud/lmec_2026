import requests
from .cli import verbose_option

@verbose_option
def download_images(identifier):
    """
    Downloads images from IIIF given the manifest UID and saves them to the specified output path.

    Args:
        identifier (str): The manifest UID of the image collection to download.
    """
    allmapsManifest = requests.get(f'https://annotations.allmaps.org/?url=https://www.digitalcommonwealth.org/search/{identifier}/manifest.json').json()