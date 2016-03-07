"""
Todo:
* Ussage of is_element/is_morphism is a hack until I get __instancecheck__ working
* GenericPedanticFunction - currying
* Try out functools.singledispatch - for creating generic categorical/Monad functions
"""
import abc

from .methods import (abstractpedanticmethod, abstractclassproperty)


class CategoryError:
    pass


class CategoryTypeError(CategoryError, TypeError):
    pass


class Category(metaclass=abc.ABCMeta):
    #
    #   Category Methods
    #
    @abstractclassproperty
    def Category(cls):
        return NotImplemented

    @abstractpedanticmethod
    def identity(cls, self):
        return NotImplemented

    @abstractpedanticmethod
    def apply(cls, self: 'cls.Element', function: 'cls.Morphism') -> 'cls.Element':
        return NotImplemented

    @abstractpedanticmethod
    def call(cls, self: 'cls.Morphism', element: 'cls.Element') -> 'cls.Element':
        return NotImplemented

    @abstractpedanticmethod
    def compose(cls, self: 'cls.Morphism', function: 'cls.Morphism') -> 'cls.Morphism':
        return NotImplemented

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Category:
            for method in cls.__abstractmethods__:
                for base in subclass.__mro__:
                    if method in base.__dict__:
                        break
                    else:
                        return NotImplemented
            return True
        return NotImplemented


class Monad(Category):
    @abstractpedanticmethod
    def map(cls, self: 'cls.Morphism', element: 'Psyk.Element') -> 'cls.Element':
        return NotImplemented

    @abstractpedanticmethod
    def bind(cls, self: 'cls.Morphism', function: 'Psyk.Morphism') -> 'cls.Element':
        return NotImplemented

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Monad:
            for method in cls.__abstractmethods__:
                for base in subclass.__mro__:
                    if method in base.__dict__:
                        break
                    else:
                        return NotImplemented
            return True
        return NotImplemented
