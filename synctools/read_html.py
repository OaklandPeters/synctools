"""Pull down all media resources for a web-page, using sync-media.py.

@todo: Validation for non-existing urls (and must begin with http://) if not os.path.exists
@todo: Add the new css-code to the `classic` function
@todo: Refactor the `classic` functions into their own file
@todo: Make main() handle commandline arguments.
@todo: Consider adding F & _ in this project, for people's approval


Note: This doesn't work for Photo-pages, because the relevant URLS
    are contained in the CSS: figure.img {background-image: url({url}); }
Easiest solution: Selenium or whatever Josh is using for Live page unit-tests
    background_image_strings = RunJS(
        _($("figure.img")).map(function (elm){ return $(elm).css('background-image') });
    )

Uses the syntax using F and _ from
    https://github.com/kachayev/fn.py

Typedefs:
    PathParts :: (str, str, str, Optional(str))
    Path :: str
"""
import re
import urllib2
import itertools

from lxml import html
from lxml.cssselect import CSSSelector

from fn import F

from .sync_media_function import sync_media
from .metafuncs import branch


def get_html(location):
    """Read and parse location (file path or url) into ElementTree."""
    return html.parse(location)


def img_tags(tree):
    """Retreive image tags from ElementTree."""
    return CSSSelector('img')(tree)


def get_src(img_tag):
    """Get contents of src attribute from Element."""
    src = img_tag.get('src')
    if src:
        return src
    else:
        src = img_tag.get('data-src')
        if src:
            return src
        else:
            src = img_tag.get('data-srcset')
            if src:
                return src
            else:
                return None


def startswith(word):
    """Operator. Returns a predicate function which checks if strings bear a certain begining."""
    def wrapper(string):
        return str.startswith(string, word)
    return wrapper


PATH_SPLIT_REGEX = re.compile(r'^(/media)/(.*)/(.*?\..*?)$')


def split_path_parts(src):
    """Split a url path into front (/media), directores, and file-name+query."""
    matchobj = PATH_SPLIT_REGEX.match(src)
    if matchobj:
        return matchobj.groups()  # (front, body_path, file_name_and_query)
    else:
        return None


def unique(sequence):
    """Find all unique elements of a sequence."""
    return list(set(sequence))

BACKGROUND_IMAGE_REGEX = re.compile(r'background-image: url\((.*?\))')


def read_page(url):
    """Read URL into a string."""
    return urllib2.urlopen(url).read()


def combine(iterables):
    """Chain together a series of iterables."""
    return list(itertools.chain(*iterables))


get_img_srcs = (
    F()
    >> get_html  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> F(map, get_src)  # List[Optional[Path]]
)

get_css_srcs = (
    F()
    >> read_page  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]
)

parse_srcs = (
    F()
    >> F(filter, lambda obj: obj is not None)  # :: List[Path]
    >> F(filter, startswith("/media"))  # :: List[Path]
    >> F(map, split_path_parts)  # :: List[Optional(PathParts)]
    >> F(filter, lambda obj: obj is not None)  # :: List[PathParts]
    >> F(map, lambda obj: obj[1])  # :: List[Path]
)

fetch_paths = (F()
    >> branch(get_img_srcs, get_css_srcs)
    >> combine
    >> unique
    >> parse_srcs
)

def sync_page_images(url):
    """Functional Python version."""
    executor = (fetch_paths >> F(map, sync_media))
    return executor(url)


def sync_page_images_classic(url):
    """Equivalent classical Python.

    ...because some people will feel uncomfortable using the pipeline version.
    """
    tree = get_html(url)
    imgs = img_tags(tree)
    src_strings = map(get_src, imgs)
    nonempty_strings = filter(lambda obj: obj is not None, src_strings)
    media_strings = filter(startswith("/media"), nonempty_strings)
    src_path_parts = map(split_path_parts, media_strings)
    nonempty_path_parts = filter(lambda obj: obj is not None, src_path_parts)
    body_paths = map(lambda obj: obj[1], nonempty_path_parts)
    unique_paths = unique(body_paths)
    return map(sync_media, unique_paths)


def main(location):
    """Run example code. In future, should take commandline arguments."""

    return sync_page_images_classic(location)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
