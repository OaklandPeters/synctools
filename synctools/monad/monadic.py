"""
Functor/Applicative/Monad classes, drawn from:
https://bitbucket.org/jason_delaat/pymonad

(likely modified soon)
"""

class Container(object):
    """ Represents a wrapper around an arbitrary value and a method to access it. """

    def __init__(self, value):
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.

        """
        self.value = value

    def getValue(self):
        """ Returns the value held by the Container. """
        return self.value

    def __eq__(self, other):
        return self.value == other.value

class Functor(Container):
    """ Represents a type of values which can be "mapped over." """

    def __init__(self, value):
        """ Stores 'value' as the contents of the Functor. """
        super(Functor, self).__init__(value)

    def fmap(self, function):
        """ Applies 'function' to the contents of the functor and returns a new functor value. """
        raise NotImplementedError("'fmap' not defined.")

    def __rmul__(self, aFunction):
        """
        The 'fmap' operator.
        The following are equivalent:

            aFunctor.fmap(aFunction)
            aFunction * aFunctor

        """

        return self.fmap(aFunction)

    @classmethod
    def unit(cls, value):
        """ Returns an instance of the Functor with 'value' in a minimum context.  """
        raise NotImplementedError

def unit(aClass, value):
    """ Calls the 'unit' method of 'aClass' with 'value'.  """
    return aClass.unit(value)


class Applicative(Functor):
    """
    Represents a functor "context" which contains a function as a value rather than
    a type like integers, strings, etc.

    """

    def __init__(self, function):
        """ Stores 'function' as the functors value. """
        super(Applicative, self).__init__(function)

    def amap(self, functorValue):
        """
        Applies the function stored in the functor to the value inside 'functorValue'
        returning a new functor value.

        """
        raise NotImplementedError

    def __and__(self, functorValue):
        """ The 'amap' operator. """
        return self.amap(functorValue)

class Monad(Applicative):
    """
    Represents a "context" in which calculations can be executed.

    You won't create 'Monad' instances directly. Instead, sub-classes implement
    specific contexts. Monads allow you to bind together a series of calculations
    while maintaining the context of that specific monad.

    Abstract Function
    """

    def __init__(self, value):
        """ Wraps 'value' in the Monad's context. """
        super(Monad, self).__init__(value)

    def bind(self, function):
        """ Applies 'function' to the result of a previous monadic calculation. """
        raise NotImplementedError

    def __rshift__(self, function):
        """
        The 'bind' operator. The following are equivalent:
            monadValue >> someFunction
            monadValue.bind(someFunction)

        """
        if callable(function):
            result = self.bind(function)
            if not isinstance(result, Monad): raise TypeError("Operator '>>' must return a Monad instance.")
            return result
        else:
            if not isinstance(function, Monad): raise TypeError("Operator '>>' must return a Monad instance.")
            return self.bind(lambda _: function)
