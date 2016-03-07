import functools

from .pysk import Pysk
from .interfaces import Category, Monad


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


@GenericFunction(Category)
def identity(value):
    return Pysk.identity(value)


@GenericFunction(Category)
def apply(element, morphism):
    return Pysk.apply(element, morphism)


@GenericFunction(Category)
def compose(morphism, function):
    return Pysk.compose(morphism, function)


@GenericFunction(Category)
def call(morphism, element):
    return Pysk.call(morphism, element)


@GenericFunction(Monad)
def map(morphism, element):
    return Pysk.call(morphism, element)


@GenericFunction(Monad)
def bind(morphism, function):
    return Pysk.compose(morphism, function)


if __name__ == "__main__":
    from .methods import pedanticmethod

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
