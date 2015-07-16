"""Download all media resources from a url, using sync-media.py.

Typedefs:
    PathParts :: (str, str, str)
    Path :: str
    Location :: str  - URL or local file path
"""
import re
import urllib2

from lxml import html, cssselect
from fn import F

from sync_media_function import sync_media
from metafuncs import branch, combine, maybe, tryit, getitem

# from pymonad.List import List as ListM
from monad.composable import Composable

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
split_path_parts = lambda src: PATH_SPLIT_REGEX.match(src).groups()  # :: str -> PathPats

# Composite work-horse functions
# Retreive src-like properties from <img> tags
get_img_srcs = (
    F()  # :: Location
    >> get_html  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> F(map, get_src)  # List[Optional[Path]]
)
# Retreive URL-paths from CSS 'background-image:' properties
get_css_srcs = (
    F()  # :: Location
    >> read_page  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]
)
# Format relative paths for sync-media
parse_srcs = (
    F()  # :: List[Optional[Path]]
    >> F(filter, is_not_none)  # :: List[Path]
    >> F(filter, lambda phrase: str.startswith(phrase, '/media'))
    >> F(map, tryit(split_path_parts))  # :: List[Optional(PathParts)]
    >> F(filter, is_not_none)  # :: List[PathParts]
    >> F(map, getitem(1))  # :: List[Path]
)
# Combine get_img_srcs with get_css_srcs, and parse resultant paths
fetch_paths = (
    F()  # :: Location
    >> branch(get_img_srcs, get_css_srcs)  # :: (List[Path], List[Path])
    >> combine  # :: List[Path]
    >> unique  # :: List[Path]
    >> parse_srcs  # :: List[Path]
)
executor = fetch_paths >> F(map, sync_media)  # Location -> Side Effects! impure! impure!





def main(location):
    """ Pull down all images referenced in a given HTML URL or file."""

    grab = (
        F() >> cache(branch(get_img_srcs, get_css_srcs)) >> combine >> unique
        >> F(filter, is_not_none)
        >> F(filter, lambda phrase: str.startswith(phrase, '/media'))
    )
    print(grab(location))  # returns nothing. Why?
    print()
    import pdb
    pdb.set_trace()
    print()

    return executor(location)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
