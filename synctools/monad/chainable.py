

import functools

from . import monadic
from ..metafuncs import compose, _compose, _identity



class Chainable(object):
    def __init__(self, callback=_identity):
        self._callback = callback

    def bind(self, func):
        return Chainable(_compose(func, self._callback))

    def __rshift__(self, function):
        """Chaining or 'Bind' operator. The following are equivalent
            monadValue.bind(someFunction)
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

