"""Download all media resources from a url, using sync-media.py.

Typedefs:
    PathParts :: (str, str, str)
    Path :: str
    Location :: str  - URL or local file path
"""
import re
import urllib2

from lxml import html, cssselect

from sync_media_function import sync_media
from metafuncs import branch, combine, maybe, tryit, getitem, cache, Chainable

# Composable = Chainable
from monad.composable import Composable
import functools
F = functools.partial


# Support functions
is_not_none = lambda obj: obj is not None
unique = lambda sequence: list(set(sequence))
get_html = html.parse  # :: str -> ElementTree
img_tags = cssselect.CSSSelector('img')  # :: ElementTree -> List[Element]
get_src = maybe(getitem('src'),     # normal
            maybe(getitem('data-src'),  # photo pages
                maybe(getitem('data-srcset'))))  # home page
BACKGROUND_IMAGE_REGEX = re.compile(r'background-image: url\((.*?\))')
read_page = lambda url: urllib2.urlopen(url).read()
PATH_SPLIT_REGEX = re.compile(r'^(/media)/(.*)/(.*?\..*?)$')
# PATH_SPLIT_REGEX = re.compile(r'/media/(.*)/(')
split_path_parts = lambda src: PATH_SPLIT_REGEX.match(src).groups()  # :: str -> PathPats
MEDIA_PATH_REGEX = re.compile(r'/media/')
is_media_path = lambda path: MEDIA_PATH_REGEX.search(path) is not None

# Composite work-horse functions
# Retreive src-like properties from <img> tags
get_img_srcs = (
    Composable()  # :: Location
    >> cache(get_html)  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> F(map, get_src)  # List[Optional[Path]]
)
# Retreive URL-paths from CSS 'background-image:' properties
get_css_srcs = (
    Composable()  # :: Location
    >> cache(read_page)  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]
)
# Format relative paths for sync-media
parse_srcs = (
    Composable()  # :: List[Optional[Path]]
    >> F(filter, is_not_none)  # :: List[Path]
    # >> F(filter, lambda phrase: str.startswith(phrase, '/media'))
    >> F(filter, is_media_path)
    >> F(map, tryit(split_path_parts))  # :: List[Optional(PathParts)]
    # >> mapper(tryit(split_path_parts))
    >> F(filter, is_not_none)  # :: List[PathParts]
    >> F(map, getitem(1))  # :: List[Path]
    # >> mapper(getitem(1))
)
# Combine get_img_srcs with get_css_srcs, and parse resultant paths
fetch_full_paths = (
    Composable()  # :: Location
    # >> cache(branch(get_img_srcs, get_css_srcs))  # :: (List[Path], List[Path])
    >> branch(get_img_srcs, get_css_srcs)  # :: (List[Path], List[Path])
    >> combine  # :: List[Path]
    >> unique  # :: List[Path]
)
fetch_paths = fetch_full_paths >> parse_srcs  # :: List[Path]
executor = fetch_paths >> F(map, sync_media)  # Location -> Side Effects! impure! impure!


def main(location):
    """ Pull down all images referenced in a given HTML URL or file."""
    return executor(location)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
