"""Abstract meta-functions.

pylint: disable=W0212, C0111
"""
import itertools
import functools

_identity = lambda x: x
_compose = lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs))


def compose(*callables):
    """Metafunction. Compose multiple functions, with the rightmost being first executed."""
    composed = _identity
    for func in callables:
        composed = _compose(func, composed)
    composed.__name__ = composed
    return composed


def branch(*callables):
    """Metafunction. Invokes a series of functions with the same arguments."""
    def wrapper(*args, **kwargs):
        return [func(*args, **kwargs) for func in callables]
    return wrapper


def combine(iterables):
    """Chain together a series of iterables."""
    return list(itertools.chain(*iterables))


def maybe(func, _else=None):
    """Decorator. If func returns None, then do _else."""
    @functools.wraps(func)
    def wrap_maybe(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            return result
        else:
            if callable(_else):
                return _else(*args, **kwargs)
            else:
                return _else
    return wrap_maybe


def tryit(func, _exceptions=(KeyError, AttributeError), _else=None):
    """Decorator. Convenience for common-case of try/except."""
    @functools.wraps(func)
    def wrap_tryit(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except _exceptions:
            if callable(_else):
                return _else(*args, **kwargs)
            else:
                return _else
    return wrap_tryit


def ensure_end(end):
    """Operator. Returns function which ensures strings bear a certain ending."""
    def wrapper(word):
        if word.endswith(end):
            return word
        else:
            return word + end
    return wrapper


def cache(func):
    """Decorator. Simple caching of results for functions of a single Hashable argument."""
    func._cache = {}

    def wrapper(value):
        if value not in func._cache:
            result = func(value)
            try:
                func._cache[value] = result
            except TypeError:  # Unhashable type
                return result
        return func._cache[value]
    return wrapper


def getitem(key, default=None):
    """Operator. Return a function retreiving a key, with optional default."""
    def getter_wrapper(obj):
        if hasattr(obj, 'get'):
            return obj.get(key, default)  # defer to get method, for Mappings
        try:
            return obj[key]
        except (KeyError, IndexError):
            return default
    return getter_wrapper


def get(key, default=None):
    """Operator. __getitem__, which optional default value."""
    def wrapper(obj):
        return obj.get(key, default)
    return wrapper



#
#   Unused metafunctions
#
# These should be abstracted out
def mapper(func):
    """Decorator. Return a function mapping function over iterables."""
    def wrap_map(*args, **kwargs):
        return map(func, *args, **kwargs)
    return wrap_map

def filterer(func):
    """Decorator."""
    def wrap_filter(*args, **kwargs):
        return filter(func, *args, **kwargs)
    return wrap_filter

