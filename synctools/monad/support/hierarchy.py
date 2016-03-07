"""
@todo: Add Functor Interface
@todo: Make a category-specific version of __rshift__, which just has apply/call/compose, and call it Category-Sugar
@todo: Build a monad-specific version of __rshift__, that rests on the category version, and adds use of decorate/construct
"""
import abc
import typing

from .methods import abstractpedanticmethod, pedanticmethod, abstractclassproperty
from .interfaces import Pysk, Monad, Category


class Element(metaclass=abc.ABCMeta):
    @abstractclassproperty
    def Category(cls):
        return NotImplemented

    @abstractpedanticmethod
    def apply(cls, self, morph):
        return NotImplemented


class MonoidalElement(Element):
    @abstractpedanticmethod
    def append(cls, self, element):
        """
        The case of M(value) >> M(value)
        """
        return NotImplemented


class Morphism(metaclass=abc.ABCMeta):
    @abstractclassproperty
    def Category(cls):
        return NotImplemented

    @abstractpedanticmethod
    def compose(cls, self, morphism):
        return NotImplemented

    @abstractpedanticmethod
    def call(cls, self, element):
        return NotImplemented


class Category(metaclass=abc.ABCMeta):
    #
    #   Category Methods
    #
    @abstractclassproperty
    def Category(cls):
        return NotImplemented

    @abstractclassproperty
    def Element(cls):
        return NotImplemented

    @abstractclassproperty
    def Morphism(cls):
        return NotImplemented

    @abstractclassproperty
    def Object(cls):
        return typing.Union[cls.Element, cls.Morphism]

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


class Functor:
    @abstractclassproperty
    def Codomain(cls) -> Monad:
        """For Monads, the category is basically the monad itself."""
        return NotImplemented

    @abstractclassproperty
    def Domain(cls) -> 'Category':
        """Domain will almost always be Pysk."""
        return NotImplemented    


class Monadic(Category, Functor):
    @abstractpedanticmethod
    def bind(cls,
             morphism: 'cls.Codomain.Morphism',
             constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]'
             ) -> 'cls.Codomain.Element':
        """
        In Haskell, this is called 'Klesli composition', using symbol: >=>
        'f_compose' ~ functor-specific composotion

        (C1 -> C2, D2 -> C3) -> C3
        """
        return NotImplemented

    @abstractpedanticmethod
    def f_apply(cls,
                element: 'cls.Codomain.Element',
                constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]'
                ) -> 'cls.Codomain.Element':
        """This is an alias of the bind function."""
        return cls.bind(element, constructor)

    @abstractpedanticmethod
    def f_compose(cls,
                  morphism: 'cls.Codomain.Morphism',
                  constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]'
                  ) -> 'cls.Codomain.Morphism':
        """This is kleisli-composition, which is basically the function-to-function
        version of the bind function."""
        return NotImplemented


class MonadicElement(Monadic, Element):
    pass


class MonadicMorphism(Monadic, Morphism):
    """Placeholder for an idea"""
    def __call__(self, element: 'cls.Codomain.Element') -> 'cls.Codomain.Element':
        return self.call(self.construct(element))

    @pedanticmethod
    def __rshift__(cls, self: 'Morphism', arg) -> 'Union[cls.Codomain.Element, cls.Codomain.Morphism]':
        if isinstance(arg, cls.Codomain.Morphism):
            return cls.compose(self, arg)
        elif isinstance(arg, cls.Codomain.Element):
            return cls.call(self, arg)
        elif isinstance(arg, Pysk.Morphism):
            return cls.compose(self, cls.decorate(arg))
        elif isinstance(arg, Pysk.Element):
            return cls.call(self, cls.construct(arg))
        else:
            raise _category_mismatch_error(cls, self, arg)

    @pedanticmethod
    def __matmul__(cls, self: '', constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]') -> 'cls.Codomain.Morphism':
        """This is kleisli-composition, which is basically the function-to-function
        version of the bind function."""
        return cls.f_compose(self, constructor)



class MonadicElement(MonadicElement):
    """Placeholder for any idea"""
    @abstractpedanticmethod
    def map(cls,
            element: 'cls.Codomain.Element',
            constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]'
            ) -> 'cls.Codomain.Element':
        """
        In Haskell, this is called 'bind', using symbol: >>=
        'f_apply' ~ functor-specific apply

        (C1, D1 -> C2)  ->  C2
        """
        return NotImplemented

    @pedanticmethod
    def __rshift__(cls, self: 'MonadicElement', arg) -> 'Union[cls.Domain.Element, cls.Domain.Morphism]':
        if isinstance(arg, cls.Codomain.Morphism):
            return cls.apply(self, arg)
        elif isinstance(arg, cls.Codomain.Element):
            return cls.append(self, arg)
        elif isinstance(arg, Pysk.Morphism):
            return cls.apply(self, cls.decorate(arg))
        elif isinstance(arg, Pysk.Element):
            return cls.append(self, cls.construct(arg))
        else:
            raise _category_mismatch_error(cls, self, arg)

    @pedanticmethod
    def __matmul__(cls, self: 'Element', constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]') -> 'cls.Domain.Morphism':
        """This is the bind function."""
        return cls.f_call(self, constructor)



class Cofunctor(Functor):
    """
    A thing designed to make '<<' sensible.
    """
    @abstractpedanticmethod
    def corate(cls, morphism: 'cls.Codomain.Morphism') -> 'cls.Domain.Morphism':
        """Conjugate of decorate
        for all X in cls.Domain.Elements and f in cls.Domain.Morphisms(X -> Y)
            cls.corate(cls.decorate(f))(X) == f(X)
        """
        return NotImplemented

    @abstractpedanticmethod
    def deconstruct(cls, element: 'cls.Codomain.Element') -> 'cls.Domain.Element':
        """Conjugate of construct.
        for all X in cls.Domain
            cls.deconstruct(cls.construct(X)) == X
        """
        return NotImplemented


class Comonad(Cofunctor, Category):
    """
    Honestly, at present, I have no idea how these functions
    would work, or be used. I do suspect they will be closely related
    to Comonad + Traversable though.
    """
    @abstractpedanticmethod
    def comap(cls, element, deconstructor):
        return NotImplemented

    @abstractpedanticmethod
    def unbind(cls, morphism, deconstructor):
        return NotImplemented


#
#   Utility functions
#
def try_to_append(self, arg, cls):
    """This should be inline in MonadicElement, but I'm moving it here for clarity.
    """
    # The logic in this step could be made tighter
    # I think it's mostly correct, but I would like to verify
    # isinstance(self, X), isinstance(arg, X), issubclass(cls.Codomain.Element, X)
    if isinstance(self, MonoidalElement):
        return self.append(arg)
    else:
        raise TypeError(str.format(
            "Element >> Element is invalid, because {0} is not a Monoidal Category.",
            cls.Codomain.Element.__name__
        ))

def _category_mismatch_error(cls, self, arg):
    return TypeError(str.format(
        "Argument of type '{0}' is not in the domain or codomain of " +
        "'{1}' in category '{2}'.",
        arg.__class__.__name__,
        self.__class__.__name__,
        cls.Codomain.__name__
    ))
