"""
One-file version, few dependencies
"""
import re
import urllib2
from functools import partial

from lxml import html, cssselect

from sync_media_function import sync_media
from metafuncs import branch, combine, maybe, tryit, getitem, cache, Chainable


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
    Chainable()  # :: Location
    >> get_html  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> partial(map, get_src)  # List[Optional[Path]]
)
# Retreive URL-paths from CSS 'background-image:' properties
get_css_srcs = (
    Chainable()  # :: Location
    >> read_page  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]
)
# Format relative paths for sync-media
parse_srcs = (
    Chainable()  # :: List[Optional[Path]]
    >> partial(filter, is_not_none)  # :: List[Path]
    >> partial(filter, is_media_path)
    >> partial(map, tryit(split_path_parts))  # :: List[Optional(PathParts)]
    >> partial(filter, is_not_none)  # :: List[PathParts]
    >> partial(map, getitem(1))  # :: List[Path]
)
# Combine get_img_srcs with get_css_srcs, and parse resultant paths
fetch_full_paths = (
    Chainable()  # :: Location
    >> cache(branch(get_img_srcs, get_css_srcs))  # :: (List[Path], List[Path])
    >> combine  # :: List[Path]
    >> unique  # :: List[Path]
)
fetch_paths = fetch_full_paths >> parse_srcs  # :: List[Path]
executor = fetch_paths >> partial(map, sync_media)  # Location -> Side Effects! impure! impure!

def main(location):
    """ Pull down all images referenced in a given HTML URL or file."""
    return executor(location)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
