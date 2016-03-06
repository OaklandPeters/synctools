import abc

from .methods import abstractpedanticmethod, pedanticmethod, abstractclassproperty
from .interfaces import Pysk, MonadInterface


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


class MonadicMorphismInterface(Morphism):
    @abstractclassproperty
    def Codomain(cls) -> MonadInterface:
        """For Monads, the category is basically the monad itself."""
        return NotImplemented

    @abstractclassproperty
    def Domain(cls) -> 'CategoryInterface':
        """Domain will almost always be Pysk."""
        return NotImplemented

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


class MonadicElementInterface(MonadInterface, Element):
    @abstractclassproperty
    def Category(cls) -> MonadInterface:
        return NotImplemented


class MonadicMorphism(MonadicMorphismInterface):
    """Placeholder for an idea"""
    @abstractclassproperty
    def Category(cls) -> MonadInterface:
        return NotImplemented

    def __call__(self, element: 'cls.Codomain.Element') -> 'cls.Codomain.Element':
        return self.map(element)

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



class MonadicElement(MonadicElementInterface):
    """Placeholder for any idea"""
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
