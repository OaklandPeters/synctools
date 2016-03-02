"""Abstract meta-functions.

pylint: disable=W0212, C0111
"""
import itertools
import functools

_identity = lambda x: x
_compose = lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs))
_apply = lambda x, f: f(x)
_call = lambda f, x: f(x)


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



class Chainable(object):
    """
    Stand-in replacement for using Monads for function ordering and chaining.
    """
    def __init__(self, callback=_identity):
        self._callback = callback

    def bind(self, func):
        return Chainable(_compose(func, self._callback))

    def __rshift__(self, function):
        """'>>', used as a chaining or 'Bind' operator. The following are equivalent:
            chainableValue >> someFunction
            chainableValue.bind(someFunction)
            someFunction(Chainable._callback)
        """
        if callable(function):
            result = self.bind(function)
            if not isinstance(result, Chainable): raise TypeError("Operator '>>' must return a Chainable instance.")
            return result
        else:
            if not isinstance(function, Chainable): raise TypeError("Operator '>>' must return a Chainable instance.")
            return self.bind(lambda _: function)

    def __call__(self, *args, **kwargs):
        return self._callback(*args, **kwargs)


class Pipe(object):
    """Future... 
    * if/elif could be simplified by PipeElm/PipeMorph
    """
    def __init__(self, value=_identity):
        self._value = value

    def bind(self, func):
        return Pipe(_compose(func, self._value))

    def apply(self, func):
        return Pipe(_apply(self._value, func))

    def map(self, arg):
        return Pipe(_call(self._value, arg))

    def __call__(self, *args, **kwargs):
        """
        Pipe(arg) == Pipe().map(arg) << identity
        Pipe(function)(argument)
        """
        return self._value(*args, **kwargs)

    def __rshift__(self, arg):
        """Chains inside the category.
        Pipe(function) >> function == Pipe(function)
        Pipe(function) >> argument == Pipe(function(argument))
        Pipe(argument) >> function == Pipe(function(argument))
        Pipe(argument) >> argument -> TypeError
        """
        if callable(self._value) and callable(arg):
            return self.bind(arg)
        elif callable(self._value) and not callable(arg):
            return self.map(arg)
        elif not callable(self._value) and callable(arg):
            self.apply(arg)
        elif not callable(self._value) and not callable(arg):
            raise TypeError("Operator 'Pipe(...) >> X', X must be callable")
        else:
            raise TypeError("Case fall-through error. This should never occur")

    def __lshift__(self, arg):
        """Exit the category.
        Pipe(function) << argument == function(argument)
        Pipe(function) << function == _compose(function, function)
        Pipe(argument) << function == function(argument)
        Pipe(argument) << argument -> TypeError
        """
        if callable(self._value) and callable(arg):
            return _compose(arg, self._value)
        elif callable(self._value) and not callable(arg):
            return self(arg)
        elif not callable(self._value) and callable(arg):
            return arg(self._value)
        elif not callable(self._value) and not callable(arg):
            raise TypeError("'Pipe() >> argument << argument' is invalid")
        else:
            raise TypeError("Case fall-through error. This should never occur")


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
    """Decorator. Return a function which applies the function as a filter."""
    def wrap_filter(*args, **kwargs):
        return filter(func, *args, **kwargs)
    return wrap_filter





