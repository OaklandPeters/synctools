"""
This treats Functors as decorators.
That is, they taken a function as an input, and return a callable function
as output.



__mod__(self, other)        %
__pow__(self, other)        **
__mul__(self, other)        *
__rshift__(self, other)     >>
__lshift__(self, other)     <<
__xor__                     ^
"""
import abc
import itertools
import functools

def _hasattr(C, attr):
    try:
        return any(attr in B.__dict__ for B in C.__mro__)
    except AttributeError:
        # Old-style class
        return hasattr(C, attr)

class OperatorMeta(type):
    def __mul__(cls, other):
        if _hasattr(cls, '__mul__'):
            return cls.__mul__(other)
        else:
            raise TypeError(str.format(
                "unspported operand type(s) for *: '{0}' and '{1}'",
                cls.__name__, type(other).__name__
            ))


class Functor(object):
    __metaclass__ = OperatorMeta

    def __init__(self, wrapped):
        """Functionally equivalent to:  functools.partial(Map, wrapped) """
        self.wrapped = wrapped

    # classmethod + abstractmethod works in Python 3.3, but not Python 2.7
    @classmethod
    #@abc.abstractmethod
    def __transform__(cls, wrapped):
        """
        Defined: to be equivalent to Haskell's 'fmap'
        So: fmap f g
            transform(f, g)


        Should do all the work. Thus,

        Map.__transform__(add3)([1, 2, 3])
        is equivalent to:
        map(add3, [1, 2, 3])
        """
        return NotImplemented

    @classmethod
    def __transform_call__(cls, wrapped, *args, **kwargs):
        """This would be simpler, but not so robust (maybe...)"""
        return NotImplemented

    @classmethod
    def __mul__(cls, wrapped):
        """ Infix operator form of fmap/__transform__.
        In Haskell, I think this is Applicative's '<*>' operator."""
        return cls.__transform__(wrapped)

    def __call__(self, *args, **kwargs):
        return self.__transform__(self.wrapped)(*args, **kwargs)


def transform(functor, function):
    """Generic function. Very similar to the Pythonic @decorator pattern.
    """
    return functor.__transform__(function)





class Map(Functor):
    """
    Several use-cases:
    
    # This will be true for all cases
    add3 = lambda x: x+3
    add3_seq([1, 2, 3]) == [4, 5, 6]
    

    (1) Pythonic decorator
        @Map
        def add3_seq(x):
            return add3(x)

    (2) Inline Decorator style
        add3_seq = Map(add3)

    (3) Class '*' (fmap style)
        add3_seq = Map * add3

    (4) Pythonic generic function
        add3_seq = transform(Map, add3)
    """
    @classmethod
    def __transform__(cls, wrapped):
        """
        """
        return functools.partial(map, wrapped)


class Filter(Functor):
    @classmethod
    def __transform__(cls, wrapped):
        return functools.partial(filter, wrapped)




import unittest


add3 = lambda x: x+3
class MapTests(unittest.TestCase):
    """Tests of Map functor."""
    def setUp(self):
        self.seq = [1, 2, 3]
        self.expected = map(add3, self.seq)

    def test_decorator(self):
        """Python @decorator"""
        @Map
        def add3_seq(x):
            """This style is awkward for small test cases..."""
            return add3(x)
        self.assertEqual(self.expected, add3_seq(self.seq))

    def test_inline_decorator(self):
        """Inline functional decorator."""
        add3_seq = Map(add3)
        self.assertEqual(self.expected, add3_seq(self.seq))

    def test_operator(self):
        """Basically, * similar to 'fmap'."""
        add3_seq = Map * add3
        self.assertEqual(self.expected, add3_seq(self.seq))

    def test_generic_function(self):
        """Test the transform() function"""
        add3_seq = transform(Map, add3)
        self.assertEqual(self.expected, add3_seq(self.seq))



gte6 = lambda x: x > 6

class FilterTests(unittest.TestCase):
    """Tests of the functor version of filter."""
    def setUp(self):
        self.seq = [4, 5, 6, 7, 8]
        self.expected = filter(gte6, self.seq)

    def test_decorator(self):
        @Filter
        def gte6_seq(x):
            return gte6(x)
        self.assertEqual(self.expected, gte6_seq(self.seq))

    def test_inline_operator(self):
        gte6_seq = Filter(gte6)
        self.assertEqual(self.expected, gte6_seq(self.seq))

    def test_operator(self):
        gte6_seq = Filter * gte6
        self.assertEqual(self.expected, gte6_seq(self.seq))

    def test_generic_function(self):
        gte6_seq = transform(Filter, gte6)
        self.assertEqual(self.expected, gte6_seq(self.seq))


if __name__ == "__main__":
    unittest.main()
