"""
Typedefs:
    PathParts :: (str, str, str, Optional(str))
    Path :: str
    Location :: str  - URL or local file path
"""
import re
import urllib2

from lxml import html, cssselect
from fn import F, _

from sync_media_function import sync_media
from metafuncs import branch, combine, maybe, tryit, get

# Support functions
unique = lambda sequence: list(set(sequence))
get_html = html.parse  # :: str -> ElementTree
img_tags = cssselect.CSSSelector('img')  # :: ElementTree -> List[Element]
#get = lambda key, default=None: lambda obj: obj.get(key, default=default)
get_src = maybe(get('src'),     # normal
            maybe(get('data-src'),  # photo pages
                maybe(get('data-srcset'))))  # home page
BACKGROUND_IMAGE_REGEX = re.compile(r'background-image: url\((.*?\))')
read_page = lambda url: urllib2.urlopen(url).read()
PATH_SPLIT_REGEX = re.compile(r'^(/media)/(.*)/(.*?\..*?)$')
split_path_parts = lambda src: PATH_SPLIT_REGEX.match(src).groups()  # :: str -> (str, str, str)

# Composite work-horse functions
# Retreive src-like properties from <img> tags
get_img_srcs = (F()  # :: Location
    >> get_html  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> F(map, get_src)  # List[Optional[Path]]
)
# Retreive URL-paths from CSS 'background-image:' properties
get_css_srcs = (F()  # :: Location
    >> read_page  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]
)
# Format relative paths for sync-media
parse_srcs = (F()  # :: List[Optional[Path]]
    >> F(filter, _ != None)  # :: List[Path]
    >> F(filter, lambda phrase: str.startswith(phrase, '/media'))
    >> F(map, tryit(split_path_parts))  # :: List[Optional(PathParts)]
    >> F(filter, _ != None)  # :: List[PathParts]
    >> F(map, _[1])  # :: List[Path]
)
# Combine get_img_srcs with get_css_srcs, and parse resultant paths
fetch_paths = (F()  # :: Location
    >> branch(get_img_srcs, get_css_srcs)  # :: (List[Path], List[Path])
    >> combine  # :: List[Path]
    >> unique  # :: List[Path]
    >> parse_srcs  # :: List[Path]
)
executor = fetch_paths >> F(map, sync_media)  # Location -> Side Effects! impure! impure!

def main(location):
    """ Pull down all images referenced in a given HTML URL or file."""

    tags = (F() >> get_html >> img_tags)(location)
    tag = tags[1]
    print()
    print("tag:", type(tag), tag)
    print()
    import ipdb
    ipdb.set_trace()
    print()
    

    return executor(location)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
