import typing
import functools

from .interfaces import Category
from .methods import classproperty, pedanticmethod


class Pysk(Category):
    @staticmethod
    def _identity(value):
        return value

    @classproperty
    def identity(cls):
        return cls._identity

    @pedanticmethod
    def compose(cls, self: 'cls.Morphism', function: 'cls.Morphism'):
        @functools.wraps(self)
        def composed(element: 'cls.Element') -> 'cls.Element':
            return self(function(element))
        return composed

    @pedanticmethod
    def call(cls, self: 'cls.Morphism', element: 'cls.Element') -> 'cls.Element':
        return self(element)

    @pedanticmethod
    def apply(cls, self: 'cls.Element', function: 'cls.Morphism') -> 'cls.Element':
        return function(self)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str.format(
            "{0}({1})", self.__class__.__name__,
            _short_str(self.value)
        )

    def __repr__(self):
        return str.format(
            "{0}({1})",
            self.__class__.__name__,
            repr(self.__dict__))

    @pedanticmethod
    def is_element(cls, obj):
        return True

    @pedanticmethod
    def is_morphism(cls, obj):
        return callable(obj)

    @classproperty
    def Object(cls):
        return typing.Union[cls.Element, cls.Morphism]


# Internal utility functions
def _short_str(obj, max_len=30):
    """
    """
    if hasattr(obj, '__name__'):
        full = obj.__name__
    else:
        full = str(obj)
    if len(full) <= max_len:
        return full
    else:
        return full[:max_len] + " ..."
