"""
Todo:
* GenericPedanticFunction - currying
* Try out functools.singledispatch - for creating generic categorical/Monad functions
"""
import abc
import functools

from .methods import abstractpedanticmethod, pedanticmethod


class CategoryInterface(metaclass=abc.ABCMeta):
    #
    #   Category Methods
    #
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
        if cls is CategoryInterface:
            for method in cls.__abstractmethods__:
                for base in subclass.__mro__:
                    if method in base.__dict__:
                        break
                    else:
                        return NotImplemented
            return True
        return NotImplemented


class MonadInterface(CategoryInterface):
    @abstractpedanticmethod
    def map(cls, self: 'cls.Morphism', element: 'Psyk.Element') -> 'cls.Element':
        return NotImplemented

    @abstractpedanticmethod
    def bind(cls, self: 'cls.Morphism', function: 'Psyk.Morphism') -> 'cls.Element':
        return NotImplemented

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is MonadInterface:
            for method in cls.__abstractmethods__:
                for base in subclass.__mro__:
                    if method in base.__dict__:
                        break
                    else:
                        return NotImplemented
            return True
        return NotImplemented


class Pysk(CategoryInterface):
    @pedanticmethod
    def identity(cls, self):
        return self

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

    def __repr__(self):
        return str.format("{0}({1})".format(self.__class__.__name__, self.value))



class GenericFunction:
    """
    @todo: Add currying, so identity(WeirdCat) == WeirdCat.identity
    """
    def __init__(self, Interface):
        self.Interface = Interface

    def __call__(self, default):
        generic = functools.singledispatch(default)
        @generic.register(self.Interface)
        def _(first, *args, **kwargs):
            return getattr(first, default.__name__)(*args, **kwargs)
        return generic


@GenericFunction(CategoryInterface)
def identity(value):
    return Pysk.identity(value)

@GenericFunction(CategoryInterface)
def apply(element, morphism):
    return Pysk.apply(element, morphism)

@GenericFunction(CategoryInterface)
def compose(morphism, function):
    return Pysk.compose(morphism, function)

@GenericFunction(CategoryInterface)
def call(morphism, element):
    return Pysk.call(morphism, element)

@GenericFunction(MonadInterface)
def map(morphism, element):
    return Pysk.call(morphism, element)

@GenericFunction(MonadInterface)
def bind(morphism, function):
    return Pysk.compose(morphism, function)



if __name__ == "__main__":
    #
    #  for unit-testing
    # 
    class WeirdCat(Pysk):
        def __init__(self, value):
            self.value = value

        @pedanticmethod
        def identity(cls, self):
            return WeirdCat(Pysk.identity(self.value))

        @pedanticmethod
        def call(cls, self, value):
            return WeirdCat(Pysk.call(self.value, value))

        @pedanticmethod
        def compose(cls, self, func):
            return WeirdCat(Pysk.compose(self.value, func))

        @pedanticmethod
        def apply(cls, self, func):
            return WeirdCat(Pysk.apply(self.value, func))

        def __repr__(self):
            return "WeirdCat({0})".format(self.value)

    print()

    print()
    print("apply:", type(apply), apply)
    print()
    import ipdb
    ipdb.set_trace()
    print()
