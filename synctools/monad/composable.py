"""

Functor/Applicative/Monad class hierarchy from pymonad by jason_delaat

"""
import pymonad

from ..metafuncs import compose, _compose

class Composable(pymonad.Monad):
    """
    Simple Monad for function composition.
    Inspired by kachayev's fn.py's class F
    https://github.com/kachayev/fn.py/blob/master/fn/func.py
    """

    @classmethod
    def lift(cls, func):
        """ lift """
        return Composable(func)
        # self = object.__new__(cls)
        # self._callback = func
        # return self

    def __init__(self, callback):
        super(Composable, self).__init__(callback)
        self._callback = callback

    def bind(self, func):
        return self.lift(_compose(func, self))

    def __call__(self, *args, **kwargs):
        return self._callback(*args, **kwargs)
