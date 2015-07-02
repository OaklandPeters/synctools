"""
"""
import sys

from sync_media_function import sync_media
from read_html import fetch_paths, sync_page_images

def main(location):
    """
    location: url or file path
    """
    return [
        sync_media(path)
        for path in sync_page_images(location)
    ]


if __name__ == "__main__":
    main(sys.argv[1])
