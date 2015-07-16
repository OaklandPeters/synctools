"""
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

from fn import F, _


def get_html(location):
    """ :: str -> ElementTree
    location can be a file path or a url
    """
    return html.parse(location)

def img_tags(tree):
    """ :: ElementTree -> List[Element] """
    return CSSSelector('img')(tree)



def get_src(img_tag):
    """ Element -> str """
    # maybe(_.call('get', 'src'),
    #   maybe(_.call('get', 'data-src'),
    #       maybe(_.call('get', 'data-srcset'))))
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


# def get(key, default=None):
#     def wrap_get(obj):
#         return obj.get(key, default=None)
#     return wrap_get

get = lambda key, default=None: _.call('get', key, default=default)

def maybe(func, _else=None):
    def wrap_maybe(obj):
        result = func(obj)
        if result != None:
            return result
        else:
            if callable(_else):
                return _else(obj)
            else:
                return _else
    return wrap_maybe

try_get_src = maybe(get('src'),
                maybe(get('data-src'),
                    maybe(get('data-srcset'))))


def startswith(word):
    """ str -> (str -> bool) """
    def wrapper(string):
        return str.startswith(string, word)
    return wrapper

PATH_SPLIT_REGEX = re.compile(r'^(/media)/(.*)/(.*?\..*?)$')
def split_path_parts(src):
    """ str -> Optional[(str, str, str)] """
    matchobj = PATH_SPLIT_REGEX.match(src)
    if matchobj:
        return matchobj.groups()  # (front, body_path, file_name_and_query)
    else:
        return None

def ensure_end(end):
    """ str -> (str -> str) """
    def wrapper(word):
        if word.endswith(end):
            return word
        else:
            return word + end
    return wrapper

def unique(sequence):
    return list(set(sequence))

BACKGROUND_IMAGE_REGEX = re.compile(r'background-image: url\((.*?\))')

def read_page(url):
    """ str -> str """
    return urllib2.urlopen(url).read()

def branch(*callables):
    """ Decorator. Return a function which invokes a series of
    functions with the same arguments.
    :: [Any -> Any] -> (Any -> [Any])
    Haskellish :: [(* -> *)] -> (* -> [*])
    """
    def wrapper(*args, **kwargs):
        return [func(*args, **kwargs) for func in callables]
    return wrapper

def combine(iterables):
    """ Chain together a series of iterables
    :: Iterable[Iterable[Any]] -> List[Any] """
    return list(itertools.chain(*iterables))



get_img_srcs = (F()
    >> get_html  # :: ElementTree
    >> img_tags  # :: List[Element]
    >> F(map, get_src)  # List[Optional[Path]]
)

get_css_srcs = (F()
    >> read_page  # :: str
    >> BACKGROUND_IMAGE_REGEX.findall  # :: List[str]    
)

parse_srcs = (F()
    >> F(filter, _ != None)  # :: List[Path]
    >> F(filter, startswith("/media"))  # :: List[Path]
    >> F(map, split_path_parts)  # :: List[Optional(PathParts)]
    >> F(filter, _ != None)  # :: List[PathParts]
    >> F(map, _[1])  # :: List[Path]
)

fetch_paths = (F()
    >> branch(get_img_srcs, get_css_srcs)
    >> combine
    >> unique
    >> parse_srcs
)

def sync_page_images(url):
    """Functional Python.    """


    print("tags = (F(get_html)>>img_tags)(url); tag = tags[0];")
    print()
    print("url:", type(url), url)
    print()
    import ipdb
    ipdb.set_trace()
    print()
    

    executor = fetch_paths >> F(map, sync_media)
    return executor(url)


def sync_page_images_classic(url):
    """Equivalent classical Python.
    ... because some people will feel uncomfortable using the pipeline version.
    """
    tree = get_html(example_file)
    imgs = img_tags(tree)
    src_strings = map(get_src, imgs)
    nonempty_strings = filter(_ != None, src_strings)
    media_strings = filter(startswith("/media"), nonempty_strings)
    src_path_parts = map(split_path_parts, media_strings)
    nonempty_path_parts = filter(_ != None, src_path_parts)
    body_paths = map(_[1], nonempty_path_parts)
    unique_paths = unique(body_paths)
    return map(sync_media, unique_paths)



def main():
    """Run example code. In future, should take commandline arguments."""
    return sync_page_images(example_url_1)
    

if __name__ == "__main__":
    main()