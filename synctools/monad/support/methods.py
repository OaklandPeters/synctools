import functools


class classproperty(object):
    """Read-only."""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class abstractclassproperty(classproperty):
    """abstract check happens in __init__, and only for classes
    descending from metaclass=abc.ABCMeta. If abstract methods have not
    been concretely implemented, will raise TypeError.
    """

    __isabstractmethod__ = True


class pedanticmethod:
    """
    Allows a method to be used as both a classmethod and an instancmethod, but in the specific (and pedantic) way so that:
        instance.method(*args, **kwargs) == klass.method(instance, *args, **kwargs)
    """
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*positional, **keywords):
            if obj is not None:  # instancemethod
                return self.method(type(obj), obj, *positional, **keywords)
            else:  # classmethod
                return self.method(objtype, *positional, **keywords)                
        return _wrapper


class abstractpedanticmethod(pedanticmethod):
    """Abstract method, intended to be overridden as a pedanticmethod - that is,
    one usable as both a classmethod and an instancemethod.

    KNOWN PROBLEM: Overridding this with @classmethod produces no errors,
    but it probably should.
    """
    __isabstractmethod__ = True

    def __init__(self, _callable):
        _callable.__isabstractmethod__ = True
        super().__init__(_callable)
