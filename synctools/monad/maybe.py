#!/usr/bin/env python3
"""
Monadic.__rshift__
    WILL go wrong when passed an object which is Monadic, but not from the monad in question
    Maybe('x') >> Pipe(f)

TODO:
* Make Monadic refer to .map/.bind, by dispatching in __rshift__.
** Current cases: When isinstance(arg, cls) --> 
** When not isinstance(arg, cls): if callable(arg) --> 
* Write check for: Maybe('x') >> Pipe(f)
* Try... making monad method calls in __rshift__ use 'cls' version: cls.bind(self, arg)
** AFTER writing unit-tests...

INTERMEDIATE:
* Rewrite Pipe and Maybe to be function-sequences, and write a reduce on that.
** I think, this reduction is 'compose'
* Trial: rewrite using Element/Morphism distinction. Will cut down on number of dispatches.
** Ideally, express this only at level of 'Monadic' sugar methods.
"""
import functools
import inspect
import abc


from support.methods import pedanticmethod
from support.interfaces import MonadInterface, CategoryInterface, Pysk

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


class Monadic(MonadInterface):
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

    # OLD __rshift__
    #def __rshift__(self, arg):
    #    """Chains inside the category.
    #    Pipe(function) >> function == Pipe(function)
    #    Pipe(function) >> argument == Pipe(function(argument))
    #    Pipe(argument) >> function == Pipe(function(argument))
    #    Pipe(argument) >> argument -> TypeError
    #    """
    #    if isinstance(arg, Monadic):
    #        return self >> arg.value

    #    if callable(self.value) and callable(arg):
    #        return self.bind(arg)
    #    elif callable(self.value) and not callable(arg):
    #        return self.map(arg)
    #    elif not callable(self.value) and callable(arg):
    #        return self.apply(arg)
    #    elif not callable(self.value) and not callable(arg):
    #        raise TypeError("Operator 'Pipe(...) >> X', X must be callable")
    #    else:
    #        raise TypeError("Case fall-through error. This should never occur")

    @pedanticmethod
    def __rshift__(cls, self, arg):
        """
        Chain(f) >> g == Chain(compose(f, g))
        Chain(f) >> x == Chain(f(x))
        Chain(x) >> f == Chain(f(x))
        Pipe(x) >> y -> TypeError
        """
        if not isinstance(arg, cls):
            return self >> cls(arg)

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


    # Old __lshift__
    #def __lshift__(self, arg):
    #    """Exit the category.
    #    Pipe(function) << argument == function(argument)
    #    Pipe(function) << function == Pysk.compose(function, function)
    #    Pipe(argument) << function == function(argument)
    #    Pipe(argument) << argument -> TypeError
    #    """
    #    if isinstance(arg, Monadic):
    #        return self << arg.value

    #    if callable(self.value) and callable(arg):
    #        return Pysk.compose(arg, self.value)
    #    elif callable(self.value) and not callable(arg):
    #        return self.value(arg)
    #    elif not callable(self.value) and callable(arg):
    #        return arg(self.value)
    #    elif not callable(self.value) and not callable(arg):
    #        raise TypeError("'Pipe() >> argument << argument' is invalid")
    #    else:
    #        raise TypeError("Case fall-through error. This should never occur")

    @pedanticmethod
    def __lshift__(cls, self, arg):
        """
        This really needs to be written in terms of something like foldable and traversable
        Chain(f) << x == f(x)
        Chain(f) << g == compose(f, g)
        Chain(x) << f == f(x)
        Chain(x) << y -> TypeError
        """
        try:
            # SPECIAL CASE:
            # ... I think this ~ join
            if not isinstance(arg, cls):
                return self << cls(arg)
        except AttributeError as exc:

            print()
            print("exc:", type(exc), exc)
            print()
            import ipdb
            ipdb.set_trace()
            print()
            

        if callable(self.value) and callable(arg.value):
            return Pysk.compose(arg.value, self.value)
        elif callable(self.value) and not callable(arg.value):
            return self.value(arg.value)
        elif not callable(self.value) and callable(arg.value):
            return arg.value(self.value)
        elif not callable(self.value) and not callable(arg.value):
            raise TypeError("'Pipe() >> argument << argument' is invalid")
        else:
            raise TypeError("Case fall-through error. This should never occur")








class ChainCategory(CategoryInterface):
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

    @pedanticmethod
    def bind(cls, morph, func):
        return cls.compose(morph, cls(func))
        
    @pedanticmethod
    def map(cls, morph, value):
        return cls.call(morph, cls(value))


class NotPassed:
    pass


class MaybeCategory(CategoryInterface):
    #@property
    #@abc.abstractmethod
    #def value(self):
    #    return NotImplemented

    @pedanticmethod
    def compose(cls, self: 'cls.Morphism', morphism: 'cls.Morphism') -> 'cls.Morphism':
        @functools.wraps(self)
        def wrapped(value: 'Pysk.Element') -> 'Pysk.Element':
            result = self.initial(value)
            if result is None:
                return morphism.initial(value)
            else:
                return result
        return cls(wrapped)

    @pedanticmethod
    def identity(cls, self):
        return cls(None)

    @pedanticmethod
    def call(cls, morph: 'cls.Morphism', element: 'cls.Element'):
        #return cls(morph.value(element.value))
        return element.apply(morph)

    @pedanticmethod
    def apply(cls, elm, morph):
        return cls(morph.value(elm.value))
        
        # Experimenting, to get strict eval working: Maybe(value) >> f1
        #previous = elm.value
        #current = morph.value(elm.initial)
        #if previous is None:
        #    return cls(current, elm.initial)
        #else:
        #    return cls(previous, elm.initial)



        

    def __repr__(self):
        return Pysk.__repr__(self)

    def __call__(self, element):
        return self.call(element)

    def __eq__(self, other):
        if isinstance(other, Maybe):
            return self.value == other.value
        return False


class Maybe(MaybeCategory, Monadic):
    """
    Concerns:
    (1) what should this be?
        Maybe() << 'x'
            'x', None, or error?

    (2) Maybe() >> identity

    (3) Like Pipe, I think this doesn't handle the case when trying to
        combine two instances of Maybe:
            Maybe(argument) >> Maybe(function)
            Maybe(function) >> Maybe(argument)

    fmap( f . g) == fmap(f) . fmap(g)

    Maybe( Maybe.compose(f, g) )  == Maybe(f) >> Maybe(g)
    Maybe( Maybe.compose(identity, f)) == Maybe() >> Maybe(f)

    So, this might have to be true
        Maybe(f)  !=   Maybe() >> f


    Important:
        Maybe('value') >> f >> g
            should be valid
    """
    def __init__(self, value=NotPassed, initial=NotPassed):
        if value is NotPassed and initial is NotPassed:
            # Zero value
            self.value = _constant(None)
            self.initial = None
        elif value is NotPassed and initial is not NotPassed:
            # By explicitly providing initial, we are saying a value, and not a morphism
            self.value = _constant(None)
            self.initial = initial
        elif value is not NotPassed and initial is NotPassed:
            # Have to consider what type of value we have
            #    this is the complicated case
            # Maybe(function) - treat as morphism
            if callable(value):
                self.value = value
                self.initial = None
            # Maybe(valuee) - treat as element
            else:
                self.value = _constant(None)
                self.initial = value
        elif value is not NotPassed and initial is not NotPassed:
            # Both are provided - use whatever was given
            self.value = value
            self.initial = initial



    @pedanticmethod
    def map(cls, morphism: 'cls.Morphism', value: 'Pysk.Element') -> 'cls.Element':
        #result = morphism.value(value)
        #if result is not None:
        #    return cls(result)
        #else:
        #    # When result is None - look at fallback
        #    if isinstance(morphism.fallback, Maybe):
        #        return morphism.fallback.map(value)
        #    else:
        #        return cls(morphism.fallback)


        result = morphism.value(value)
        if result is None:
            return morphism.value(value)
        else:
            return result

    @pedanticmethod
    def bind(cls, self: 'cls.Morphism', func: 'Pysk.Morphism') -> 'cls.Morphism':
        """Basically compose. Should put func at the end of the chain."""
        return self.compose(Maybe(func))


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

functions = [c1, c2, c3, Pysk.identity, _snuff]
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
result = (m01 >> s1 << Pysk.identity)


print()
print("result:", type(result), result)
print()
import ipdb
ipdb.set_trace()
print()


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
    def test_sugar(self):
        self.assertEqual(((Maybe() >> c1 >> c2 >> c3) << s1), c1(s1))

    def test_s1(self):
        self.assertEqual((m0 << s1), s1)
        self.assertEqual((m1 << s1), c1(s1))
        self.assertEqual((m2 << s1), c1(s1))
        self.assertEqual((m3 << s1), c1(s1))

    def test_s2(self):
        self.assertEqual((m0 << s2), s2)
        self.assertEqual((m1 << s2), None)
        self.assertEqual((m2 << s2), c2(s2))
        self.assertEqual((m3 << s2), c2(s2))


    def test_composition_0_1(self):
        m01 = m0 >> c1

        self.assertEqual(m01 << s1, c1(s1))
        self.assertEqual(m01 << Maybe(s1), c1(s1))
        self.assertEqual((m01 >> s1 << Pysk.identity), c1(s1))
        self.assertEqual((m01 >> s1), Maybe(c1(s1)))

    def test_composition_0_1_2(self):
        m012 = Maybe() >> c1 >> c2

        m012 = m1 >> c2
        m0123 = m2 >> c3

    def test_composition_0_1_2_3(self):
        m0123 = Maybe() >> c1 >> c2 >> c3

    def test_immediate_invariant(self):
        """
        @todo: This thing with a lot  or random functions
        and s values
        """
        for f1, f2 in itertools.product(functions, repeat=2):
            for val in values:
                try:
                    self.assertEqual(
                        Maybe(f1) >> f2 >> s1 << Pysk.identity,
                        Maybe(s1) >> f1 >> f2 << Pysk.identity
                    )
                except AssertionError as exc:

                    (Maybe(s1) >> f1).rshift(f2)

                    print()
                    print(f1, f2, s1)
                    print("exc:", type(exc), exc)
                    print()
                    import ipdb
                    ipdb.set_trace()
                    print()
                    

    def test_identity_law(self):
        for f1 in functions:
            for val in values:
                self.assertEqual(
                    Maybe() >> f1 << val,
                    Maybe(f1) << val
                )

    #def test_play(self):
    #    result = Maybe(s1) >> c1

    #    print()
    #    print("result:", type(result), result)
    #    print()
    #    import ipdb
    #    ipdb.set_trace()
    #    print()


if __name__ == "__main__":
    unittest.main()
