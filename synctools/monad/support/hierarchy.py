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
    def Category(cls) -> MonadInterface:
        return NotImplemented

    @abstractpedanticmethod
    def map(cls, morphism: 'cls.Category.Morphism', element: 'Pysk.Element') -> 'cls.Category.Morphism':
        return NotImplemented

    @abstractpednanticmethod
    def bind(cls, morphism: 'cls.Category.Morphism', constructor) -> 'cls.Category.Morphism':
        """Constructor accepts Psyk.Element and return Category.Element."""
        return NotImplemented

class MonadicElementInterface(MonadInterface, Element):
    @abstractclassproperty
    def Category(cls) -> MonadInterface:
        return NotImplemented


class MonadicMorphism(MonadicMorphismInterface):
    """Placeholder for an idea"""
    def __call__(self, element):
        return self.map(element)

    @pedanticmethod
    def __rshift__(cls, self: 'Element', arg) -> 'Union[cls.Category.Element, cls.Category.Morphism]':
        if isinstance(arg, cls.Category.Morphism):
            return self.compose(arg)
        elif isinstance(arg, cls.Category.Element):
            return self.call(arg)
        else:
            if isinstance(arg, Pysk.Morphism):
                return self.bind(arg)
            elif isinstance(arg, Pysk.Element):
                return self.map(arg)
            else:
                raise _category_mismatch_error(cls, self, arg)


class MonadicElement(MonadicElementInterface):
    """Placeholder for any idea"""
    @pedanticmethod
    def __rshift__(cls, self: 'MonadicElement', arg) -> 'Union[Pysk.Element, Pysk.Morphism]':
        if isinstance(arg, cls.Category.Element):
            return self.append(arg)
        elif isinstance(arg, cls.Category.Morphism):
            return self.apply(arg)
        else:
            if isinstance(arg, Pysk.Morphism):
                return self.bind(arg)
            elif isinstance(arg, Pysk.Element):
                return self.map(arg)
            else:
                raise _category_mismatch_error(cls, self, arg)


#
#   Utility functions
#
def try_to_append(self, arg, cls):
    """This should be inline in MonadicElement, but I'm moving it here for clarity.
    """
    # The logic in this step could be made tighter
    # I think it's mostly correct, but I would like to verify
    # isinstance(self, X), isinstance(arg, X), issubclass(cls.Category.Element, X)
    if isinstance(self, MonoidalElement):
        return self.append(arg)
    else:
        raise TypeError(str.format(
            "Element >> Element is invalid, because {0} is not a Monoidal Category.",
            cls.Category.Element.__name__
        ))

def _category_mismatch_error(cls, self, arg):
    return TypeError(str.format(
        "Argument of type '{0}' is not in the domain or codomain of " +
        "'{1}' in category '{2}'.",
        arg.__class__.__name__,
        self.__class__.__name__,
        cls.Category.__name__
    ))
