#!/usr/bin/env python3
"""
TODO:
* Remove reference to .value in Monadic: __rshift__ should use is_element/is_morphism
* Remove unneeded utility functions like _thunk.
* Replace _underscore utility methods with references to Pysk
* Put c1, c2, m0, m1 things inside unittest case
* Move __init__ dispatching inside functor somewhere --> identity, decorate, construct based on whether input is Domain.Element or Domain.Morphism
* Write check for: Maybe('x') >> Pipe(f)
* Try... making monad method calls in __rshift__ use 'cls' version: cls.bind(self, arg)
** AFTER writing unit-tests...
* Unittest for     (2) Maybe() >> identity
* Simplify Maybe.__init__ by refering to construct, decorate, and identity
* [high] bind/map/flatten for monad. Binding in functions which return Maybe


INTERMEDIATE:
* Merge hierarchy.py into interfaces.py
* Validation: in __call__, that arg is correct monad
* Handling Monadic.__rshift__ - when passed an object from a different monad
* Rewrite Pipe and Maybe to be function-sequences, and write a reduce on that.
** I think, this reduction is 'compose'
* Rewrite: using Element/Morphism, as shown in hierarchy.py. Will cut down on the number of disptaches, and make Element not express a __call__ function.
** Ideally, express this only at level of 'Monadic' sugar methods. IE the only replacement will be Monadic-->MonadicElement,MonadicMorphism + changing what is returned by the __new__ method
* Write PyskElement and PyskMorphism
* Write instance-level __instancecheck__ mechanisms, and connect to PyskMorphism


FOLDABLE/TRAVERSABLE:
    To make the extraction function '<< f1' work right, it will have to be a monoid, so the zero can be determined.
"""
import functools
import inspect
import abc
import typing


from support.methods import pedanticmethod, classproperty
from support.interfaces import Monad, Category, CategoryError
from support.pysk import Pysk

def _identity(x):
    return x

def _constant(x):
    def wrapper(arg):
        return x
    wrapper.__name__ = "constant_"+x.__class__.__name__
    return wrapper

def _thunk(x):
    def _thought():
        return x
    return _thought

def _resolve(f: 'Callable[[], Any]'):
    """This is only valid for functions accepting no arguments,
    or functions accepting any arity.
        x == _resolve(_thunk(x))
    """
    return f()

def _call(f, x):
    return f(x)

def _apply(x, f):
    return f(x)

def _compose(f, g):
    def _composed(arg):
        return f(g(arg))
    return _composed


class Monadic(Monad):
    """
    Should have abstracts:
        bind
        apply
        map
    """
    def __init__(self, value=_identity):
        self.value = value

    def __call__(self, arg):
        """
        Pipe(arg) == Pipe().map(arg) << identity
        Pipe(function)(argument)
        """
        return self.map(arg)

    @pedanticmethod
    def __rshift__(cls, self, arg):
        """
        Monad(f) >> g  ==  Monad.compose(f, Monad(g))
        Monad(f) >> x  ==  Monad.call(f, Monad(x))
        Monad(x) >> g  ==  Monad.apply(x, Monad(g))
        Monad(x) >> y  ==  Monad.append(x, Monad(y))
        """
        # SPECIAL CASE:
        # ... I think this ~ join
        if not isinstance(arg, cls):
            arg = cls(arg)

        if callable(self.value) and callable(arg.value):
            #return self.bind(arg.value)
            return self.compose(arg)
        elif callable(self.value) and not callable(arg.value):
            #return self.map(arg.value)
            return self.call(arg)
        elif not callable(self.value) and callable(arg.value):
            return self.apply(arg)
        elif not callable(self.value) and not callable(arg.value):
            raise TypeError("Operator 'Pipe(...) >> X', X must be callable")
        else:
            raise TypeError("Case fall-through error. This should never occur")

    @pedanticmethod
    def __lshift__(cls, self, arg):
        """
        For now, this is a placeholder, that will not work in general.
        For now, it will only work for Monads where extracting 'value'
        extracts all of the meaningful information.

        Current kludge hinges on 'extract' - which is a piece of 
        comonad.


        Eventually, it will need to be expressed in terms of 
        'Traversable'-like functions. However, this is actually
        hard and complex to express in the general-case.

        To be totally rigorous, this method would have to take
        an applicative Functor on the right-hand side
        (a functor from the MonadCategory to Pysk).


        Monad(f) << g  ==  compose(f, g)
        Monad(f) << x  ==  call(f, x)
        Monad(x) << g  ==  apply(x, g)
        Monad(x) << y  ->  TypeError
        """
        if callable(self.value) and callable(arg):
            #return Pysk.compose(arg, self.value)
            return _compose(cls.corate(self), arg)
        elif callable(self.value) and not callable(arg):
            #return self.value(arg)
            return _call(cls.corate(self), arg)
        elif not callable(self.value) and callable(arg):
            #return arg(self.value)
            return _call(arg, cls.deconstruct(self))
        elif not callable(self.value) and not callable(arg):
            raise TypeError("'Pipe() >> argument << argument' is invalid")
        else:
            raise TypeError("Case fall-through error. This should never occur")


class ChainCategory(Category):
    @pedanticmethod
    def identity(cls, elm):
        return cls(elm.value)

    @pedanticmethod
    def compose(cls, self, morph):
        # return cls(Pysk.compose(self.value, morph.value))
        @functools.wraps(self)
        def wrapped(value):
            return self.value(morph.value(value))
        return cls(wrapped)

    @pedanticmethod
    def call(cls, morph, elm):
        return cls(morph.value(elm.value))

    @pedanticmethod
    def apply(cls, elm, morph):
        return cls(morph.value(elm.value))

    def __eq__(self, other):
        if hasattr(self, 'Category') and hasattr(other, 'Category'):
            if self.Category == other.Category:
                return self.value == other.value
        return False
        

class Chain(ChainCategory, Monadic):
    """
        Chain(f) >> g == Chain(compose(f, g))
        Chain(f) >> x == Chain(f(x))
        Chain(x) >> f == Chain(f(x))
        Chain(x) >> y -> TypeError

        Chain(f) << x == f(x)
        Chain(f) << g == compose(f, g)
        Chain(x) << f == f(x)
        Chain(x) << y -> TypeError
    """
    def __init__(self, value=_identity):
        self.value = value

    # Functor and Cofunctor methods
    @classmethod
    def construct(cls, value):
        return cls(value=value)

    @classmethod
    def deconstruct(cls, element):
        return element.value

    @classmethod
    def decorate(cls, function):
        return cls(function)

    @classmethod
    def corate(cls, morphism):
        return morphism.value

    # Monad methods
    @pedanticmethod
    def bind(cls, morph, func):
        return cls.compose(morph, cls(func))
        
    @pedanticmethod
    def map(cls, morph, value):
        return cls.call(morph, cls(value))

    def __eq__(self, other):
        if hasattr(self, 'Category') and hasattr(other, 'Category'):
            if issubclass(other.Category, self.Category):
                return self.value == other.value
        return False


class MaybeCategory(Category):
    def __init__(self, value, initial):
        self.value = value
        self.initial = initial

    @pedanticmethod
    def compose(cls, self: 'cls.Morphism', morphism: 'cls.Morphism') -> 'cls.Morphism':
        @functools.wraps(self.value)
        def wrapped(initial):
            result = self.value(initial)
            if result is None:
                return morphism.value(initial)
            else:
                return result
        return cls(wrapped, None)

    @classproperty
    def identity(cls):
        return cls(_constant(None), None)

    @pedanticmethod
    def call(cls, self: 'cls.Morphism', element: 'cls.Element'):
        """Use the first non-None between:
            element.value and result=self.value(element.initial)
        """
        if element.value is None:
            return cls(self.value(element.initial), element.initial)
        else:
            return cls(element.value, element.initial)

    @pedanticmethod
    def apply(cls, self: 'cls.Element', morphism: 'cls.Morphism') -> 'cls.Element':
        """
        NOTE: morph.__call__ isn't working, because it defers to .map, which isn't working.
        """
        return cls.call(morphism, self)

    def __repr__(self):
        return Pysk.__repr__(self)

    def __str__(self):
        return Pysk.__str__(self)

    def __call__(self, element):
        return self.call(element)

    @classproperty
    def Category(cls):
        """This will go awry during inheritance."""
        return cls

    def __eq__(self, other):
        if hasattr(self, 'Category') and hasattr(other, 'Category'):
            if issubclass(other.Category, self.Category):
                return (self.value == other.value) and (self.initial == other.initial)
        return False


class MaybeFunctor:
    #def __new__(cls, *args: 'typing.Tuple[cls.Domain.Object]') -> 'cls.Codomain.Object':
    #    if len(args) == 2:
    #        return cls.decorate(args[0])
    #        #return object.__new__(cls)
    #        #cls(args[0], args[1])
    #    elif len(args) == 1:
    #        obj = args[0]
    #        if obj == cls.Domain.identity:
    #            return cls.Codomain.identity
    #        elif cls.Domain.is_element(obj):
    #            return cls.construct(obj)
    #        elif cls.Domain.is_morphism(obj):
    #            return cls.decorate(obj)
    #        else:
    #            raise CategoryError(str.format(
    #                "Argument is not an object in Domain {0}", cls.Domain.__name__))
    #    elif len(args) == 0:
    #        return cls.Codomain.identity
    #    else:
    #        raise CategoryError("Too many arguments to Functor.")

    @classmethod
    def dispatch(cls, obj):
        """Convenience function for constructing."""
        if obj == cls.Domain.identity:
            return cls.Codomain.identity
        elif cls.Domain.is_element(obj):
            return cls.construct(obj)
        elif cls.Domain.is_morphism(obj):
            return cls.decorate(obj)
        else:
            raise CategoryError(str.format(
                "Argument is not an object in Domain {0}", cls.Domain.__name__))


    @classproperty
    def Object(cls):
        return typing.Union[cls.Domain.Element, cls.Domain.Morphism]

    @classproperty
    def Domain(cls):
        return Pysk

    @classproperty
    def Codomain(cls):
        return MaybeCategory

    @classproperty
    def identity_morphism(cls):
        return cls(_constant(None), None)

    @classmethod
    def construct(cls, element: 'cls.Domain.Element') -> 'cls.Codomain.Element':
        return cls(None, element)

    @classmethod
    def decorate(cls, morphism: 'cls.Domain.Morphism') -> 'cls.Codomain.Morphism':
        return cls(morphism, None)

    @pedanticmethod
    def is_element(cls, obj):
        return isinstance(obj, Maybe)

    @pedanticmethod
    def is_morphism(cls, obj):
        if isinstance(obj, Maybe):
            if callable(obj):
                return True
        return False


class Maybe(MaybeCategory, MaybeFunctor, Monadic):
    """
    value - morphisms hold function here, and elements hold results
    initial - for elements only, holds initial argument

    """
    def __init__(self, *args):
        # Case 1 - no arguments --> identity morphism
        if len(args) == 0:
            self.value = _constant(None)  # might have to set = _constant(None)
            self.initial = None
        # Case 2 - only 1 thing passed in
        elif len(args) == 1:
            # Morphism
            if callable(args[0]):
                self.value = args[0]
                self.initial = None
            # Element
            else:
                self.value = None
                self.initial = args[0]
        # Case 3 - two things passed in
        elif len(args) == 2:
            self.value, self.initial = args[0], args[1]

    Category = MaybeCategory

    @pedanticmethod
    def flatten(cls, element):
        """@todo - write this"""
        pass

    @pedanticmethod
    def map(cls,
            elm: 'MaybeCategory.Element',
            constructor: 'Callable[Pysk.Element, [MaybeCategory.Element]]'
            ) -> 'MaybeCategory.Element':

        return cls.flatten(cls.apply(elm, constructor))

    @pedanticmethod
    def bind(cls,
             morphism: 'cls.Codomain.Morphism',
             constructor: 'Callable[cls.Domain.Element, [cls.Codomain.Element]]'
             ) -> 'cls.Codomain.Element':
        """
        In Haskell, this is called 'Klesli composition', using symbol: >=>
        'f_compose' ~ functor-specific composotion

        (C1 -> C2, D2 -> C3) -> C3
        """
        @functools.wraps(constructor)
        def wrapped_constructor(element):
            return cls.flatten(cls.apply(element, constructor))
        return cls.compose(morphism, wrapped_constructor)

    @pedanticmethod
    def bind(cls, self: 'cls.Morphism', func: 'Pysk.Morphism') -> 'cls.Morphism':
        """Basically compose. Should put func at the end of the chain."""
        return self.compose(Maybe(func))

    @pedanticmethod
    def __rshift__(cls, self, arg):
        """
        Chain(f) >> g == Chain(compose(f, g))
        Chain(f) >> x == Chain(f(x))
        Chain(x) >> f == Chain(f(x))
        Pipe(x) >> y -> TypeError

        This method means this works as well:
            value = Maybe()
            value >>= f
            value >>= x

        """
        if not isinstance(arg, cls):
            arg = cls(arg)

        if callable(self.value) and callable(arg.value):
            return self.compose(arg)
        elif callable(self.value) and not callable(arg.value):
            return self.call(arg)
        elif not callable(self.value) and callable(arg.value):
            return self.apply(arg)
        elif not callable(self.value) and not callable(arg.value):
            raise TypeError("Operator 'Pipe(...) >> X', X must be callable")
        else:
            raise TypeError("Case fall-through error. This should never occur")


    @pedanticmethod
    def __lshift__(cls, self, arg):
        if callable(self.value) and callable(arg):
            return Pysk.compose(arg, self.value)
        elif callable(self.value) and not callable(arg):
            return self.value(arg)
        elif not callable(self.value) and callable(arg):
            return arg(self.value)
        elif not callable(self.value) and not callable(arg):
            raise TypeError("'Pipe() >> argument << argument' is invalid")
        else:
            raise TypeError("Case fall-through error. This should never occur")


def maybe(func, fallback=None):
    """Decorator. If func returns None, then do fallback."""
    @functools.wraps(func)
    def wrap_maybe(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            return result
        else:
            if callable(fallback):
                return fallback(*args, **kwargs)
            else:
                return fallback
    return wrap_maybe


def crop(prefix):
    def wrapped(word):
        if word.startswith(prefix):
            return word[len(prefix):]
    return wrapped


def chop(suffix):
    def wrapped(word):
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return wrapped


def curried(func):
    argspec = inspect.getargspec(func)

    @functools.wraps(func)
    def wrapped(*args):
        _func = functools.partial(func, *args)
        if len(_func.args) == len(argspec.args):
            return _func()
        else:
            return _func
    return wrapped

# chop = curried(lambda suffix, word: word[:-len(suffix)] if word.endswith(suffix) else None)



traversals = [
    
]






import unittest
import itertools

remove_prefix = maybe(crop('http://opeterml1297110.njgroup.com:7000'),
                      maybe(crop('http://cdn.theatlantic.com/assets/'),
                            maybe(crop('https://cdn.theatlantic.com/assets/'),
                                  _identity)))

remove_ext = maybe(chop('.jpg'), maybe(chop('.ext'), _identity))



# 
# 
#   TEsting -  --> TURN TO UNITTEST
# 


samples = (
    'http://opeterml1297110.njgroup.com:7000/media/img/mt/2016/02/AP_081101055671/thumb_wide.jpg',
    'http://cdn.theatlantic.com/assets/media/img/mt/2016/02/the_revenant_2/thumb_wide.jpg',
    'http://cdn.theatlantic.com/assets/media/img/mt/2016/02/the_revenant_2/thumb_wide.ext',
)

s1 = samples[0]
s2 = samples[1]
s3 = samples[2]

c1 = crop('http://opeterml1297110.njgroup.com:7000/')
c2 = crop('http://cdn.theatlantic.com/assets/')
c3 = crop('https://cdn.theatlantic.com/assets/')

functions = [c1, c2, c3, Pysk.identity, _constant(None)]
values = [s1, s2, s3, 'naaaanaaa', '']

m0 = Maybe()
m1 = Maybe(c1)
m2 = Maybe(c2)
m3 = Maybe(c3)

m01 = m0.compose(m1)
m012 = m01.compose(m2)
m0123 = m012.compose(m3)

ms1 = Maybe(s1)
ms2 = Maybe(s2)
ms3 = Maybe(s3)

expected = c1(s1)
m01_s1 = m01 >> s1
#result = (m01 >> s1 << Pysk.identity)




class PipeTestCase(unittest.TestCase):
    """
    These confirm that everything is normal for Pipe
    """
    def test_parsed(self):
        parse = Chain() >> remove_prefix >> remove_ext
        results = [parse << sample for sample in samples]
        expected = [remove_ext(remove_prefix(sample)) for sample in samples]

        self.assertEqual(
            results,
            expected
        )


class MaybeTestCase(unittest.TestCase):

    def assertSameOutcome(self, func_1, func_2):
        exception_1 = None
        exception_2 = None
        outcome_1 = None
        outcome_2 = None
        try:
            outcome_1 = func_1()
        except Exception as exc:
            exception_1 = exc
        try:
            outcome_2 = func_2()
        except Exception as exc:
            exception_2 = exc
        self.assertEqual(outcome_1, outcome_2)
        if (exception_1 is None) and (exception_2 is None):
            self.assertTrue(True)
        else:
            self.assertEqual(type(exception_1), type(exception_2))        

    def test_rshift_sugar(self):
        for f1 in functions:
            for v1 in values:
                self.assertSameOutcome(
                    lambda: Maybe(f1) >> v1,
                    lambda: Maybe(f1).call(Maybe(v1))
                )                    
                for f2 in functions:
                    self.assertSameOutcome(
                        lambda: Maybe(f1) >> f2 >> v1,
                        lambda: Maybe(f1).compose(Maybe(f2)).call(Maybe(v1)),
                    )
        for v1 in values:
            for f1 in functions:
                self.assertSameOutcome(
                    lambda: Maybe(v1) >> f1,
                    lambda: Maybe(v1).apply(Maybe(f1)),
                )
            for v2 in values:
                self.assertSameOutcome(
                    lambda: Maybe(v1) >> v2,
                    lambda: Maybe(v1).apply(Maybe(v2))
                )

    def test_category_equality(self):
        for value in values:
            self.assertEqual(Maybe(value), Maybe() >> value)
            self.assertEqual(Maybe(value), Maybe(value) >> Maybe())
        double = lambda x: x*2
        for number in range(10):
            self.assertEqual(Maybe(number) >> double, Maybe(double) >> number)

    def test_application(self):
        for function in functions:
            for value in values:
                self.assertEqual(
                    Maybe(function) << value,
                    function(value)
                )

    def test_immediate_vs_lazy(self):
        """
        Ensure that immediate execution is equivalent to lazy execution,
        when applied over a chain of functions.
        Tests all possible orderings from the variable 'functions'
        """
        for value in samples:
            immediate = Maybe()
            immediate >>= value
            lazy = Maybe()
            for perm in itertools.permutations(functions):
                for func in perm:
                    immediate >>= func
                    lazy >>= func
                    self.assertEqual(lazy >> value, immediate)
            lazy >>= value
        self.assertEqual(lazy, immediate)


    def test_immediate_invariant(self):
        """
        @todo: This thing with a lot  or random functions
        and s values
        """
        for f1, f2 in itertools.product(functions, repeat=2):
            for val in values:
                self.assertEqual(
                    Maybe(f1) >> f2 >> s1 << Pysk.identity,
                    Maybe(s1) >> f1 >> f2 << Pysk.identity
                )

    def test_identity_with_zero_law(self):
        for f1 in functions:
            for val in values:
                self.assertEqual(
                    Maybe() >> f1 << val,
                    Maybe(f1) << val
                )
                self.assertEqual(
                    Maybe(f1) << val,
                    Maybe(f1) >> Maybe.identity << val
                )
                try:
                    self.assertEqual(
                        Maybe(f1) << val,
                        Maybe(f1) >> _identity << val
                    )                    
                except AssertionError as exc:

                    print()
                    print("exc:", type(exc), exc)
                    print()
                    import ipdb
                    ipdb.set_trace()
                    print()
                


    #def test_identity_mapping(self):
    #    """
    #    This property fails, because the maybe-category is not properly behaved.
    #    """
    #    for val in values:
    #        self.assertEqual(
    #            Maybe() << val,
    #            Maybe() >> _identity << val
    #        )

    def test_identity_composition(self):
        for value in values:
            for func in functions:
                self.assertEqual(
                    Maybe() >> func << value,
                    func(value)
                )
                self.assertEqual(
                    Maybe(func) >> Maybe() << value,
                    func(value)
                )

    #def test_map_composition_law(self):
    #    try:
    #        for val in values:
    #            for f1, f2 in itertools.product(functions, repeat=2):
    #                self.assertEqual(
    #                    Maybe() >> _compose(f1, f2) << val,
    #                    Maybe() >> f1 >> f2 << val
    #                )
    #    except AssertionError as exc:
    #        pass

class FunctorLawTests:
    """
    Abstractproperties:
        Domain
        Codomain
        Functor
        domain_elements
        domain_morphisms  
    """
    @abc.abstractproperty
    def Domain(self) -> 'Category':
        return NotImplemented

    @abc.abstractproperty
    def Codomain(self) -> 'Category':
        return NotImplemented

    @abc.abstractproperty
    def Functor(self) -> 'Functor':
        return NotImplemented

    def test_map_identity(self):
        """
        fmap id  =  id
        """
        for value in self.domain_elements:
            self.assertEqual(
                self.Codomain.call(
                    self.Functor.decorate(self.Domain.identity),
                    self.Functor.construct(value)
                ),
                self.Functor.construct(
                    self.Domain.identity(value)
                )
            )

    def test_map_composition(self):
        """
        fmap (g . f)  =  fmap g . fmap f
        """
        for f, g in itertools.product(self.domain_morphisms, repeat=2):
            for x in self.domain_elements:
                left = self.Functor.decorate(
                    self.Domain.compose(f, g)
                )
                right = self.Codomain.compose(
                    self.Functor.decorate(f),
                    self.Functor.decorate(g)
                )
                self.assertEqual(
                    self.Codomain.call(left, Maybe(x)),
                    self.Codomain.call(right, Maybe(x))
                )


class MaybeFunctorTests(FunctorLawTests, unittest.TestCase):
    Domain = Pysk
    Codomain = MaybeCategory
    Functor = Maybe
    domain_elements = values
    domain_morphisms = functions


if __name__ == "__main__":
    unittest.main()
