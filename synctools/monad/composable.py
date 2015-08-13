"""

Functor/Applicative/Monad class hierarchy from pymonad by jason_delaat

"""
#import pymonad
import functools

from . import monadic
from ..metafuncs import compose, _compose

def identity(x):
    return x

class ConstantFunction:
    def __init__(self, value):
        self.value = value
    def __call__(self):
        return self.value

class Composable(monadic.Monad):
    """
    Simple Monad for function composition.
    Inspired by kachayev's fn.py's class F
    https://github.com/kachayev/fn.py/blob/master/fn/func.py
    """

    @classmethod
    def lift(cls, func):
        """ lift """
        return Composable(func)

    def __init__(self, callback=identity, *args, **kwargs):
        assert callable(callback), "Callback must be callable."
        if len(args) > 0 or len(kwargs) > 0:
            callback = functools.partial(callback, *args, **kwargs)
        super(Composable, self).__init__(callback)
        self._callback = callback

    def fmap(self, func):
        # (a->b)
        return self.lift(
            _compose(func, self.value)
        )
        

    def amap(self, functor):
        return self.lift(
            functor.fmap(self.value)
        )

    def bind(self, func):
        # return self.lift(_compose(func, self))
        return self.lift(self.fmap(func))

    def __call__(self, *args, **kwargs):
        return self._callback(*args, **kwargs)




class Partial(Composable):
    def __init__(self, callback=identity, *args, **kwargs):
        if len(args) > 0 or len(kwargs) > 0:
            callback = functools.partial(callback, *args, **kwargs)

        super(Partial, self).__init__(callback)


class Cacheable(monadic.Monad):
    """
    """
    @classmethod
    def lift(cls, func):
        return cls(func)
    def __init__(self, callback=identity, *args, **kwargs):
        super(Cacheable, self).__init__(callback)
        self._callback = callback
    def bind(self, func):
        return self.lift(self.fmap(func))
    def amap(self, endofunction):
        return self.fmap(self.value)


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
