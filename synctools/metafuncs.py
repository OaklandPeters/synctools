#pylint: disable=W0212, C0111
"""
Abstract meta-functions
"""
import itertools
import functools

_identity = lambda x: x
_compose = lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs))

def compose(*callables):
    def compose_wrapper(*args, **kwargs):
        result = _identity
        for func in callables:
            result = _compose(result, func)
        return result
    return compose_wrapper

def branch(*callables):
    """ Decorator. Invokes a series of functions with the same arguments.
    :: [A' -> B'] -> (A' -> [B'])
    """
    def wrapper(*args, **kwargs):
        return [func(*args, **kwargs) for func in callables]
    return wrapper

def combine(iterables):
    """ Chain together a series of iterables
    :: Iterable[Iterable[Any]] -> List[Any] """
    return list(itertools.chain(*iterables))

def maybe(func, _else=None):
    """ Decorator, take _else branch if returns None.
    (a -> b) -> (a -> Optional[b])
    """
    def wrap_maybe(*args, **kwargs):
        result = func(*args, **kwargs)
        if result != None:
            return result
        else:
            if callable(_else):
                return _else(*args, **kwargs)
            else:
                return _else
    return wrap_maybe

def tryit(func, _exceptions=(KeyError, AttributeError), _else=None):
    """ Decorator. Convenience for common-case of try/except.
    (a -> b) -> (a -> Optional[b])  """
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
    """ str -> (str -> str) """
    def wrapper(word):
        if word.endswith(end):
            return word
        else:
            return word + end
    return wrapper

def cache(func):
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

def get(key, default=None):
    def wrapper(obj):
        return obj.get(key, default=default)
    return wrapper

# get = lambda key, default=None: lambda obj: obj.get(key, default=default)
# def getter(key, default=None):
#     def wrapper(obj):
#         return obj.get(key, default=default)
#     return wrapper
