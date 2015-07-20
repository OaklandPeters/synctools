
Project Refactoring
---------------------
- README.rst, with examples
- Remove unused test/data/ files.
- Make read_html.py mimic the structure of read_html_minimal.py
- Remove all use of F() and _() from read_html.py
- contributors
- setup.py:

Medium-Term
-------------
- Revise Monadic, along with tests.
    - Remove use of Container -> functor/applicative/monad do not necessarily have a getValue
    - Use abcs: abstract functions for Functor, Applicative, Monad
    - Find better name than fmap/amap. Maybe see if I can pin these with bind/lift/unit/transform
        - Maybe: lift - type constructor, unit - wraps value into the functor/monad,
        - Maybe: bind - chains operations while returning same functor/monad
        - Recall monadic laws:   unit(x) >> f == f(x), m >> unit == m,
            - Associative: (m >> f) >> g == m >> (f >> g)
    - Add more informative __repr__ to Composable. "<Composable function {fname} at {fid}>"
        - Idea: have it print nested function names (if they exist and are not <lambda>)
            ... basically keep recursing if _callback isinstance Composable
- See how hard it would be to get my custom Monad.Composable working
    - Test manually as replacement for F()
- Extra monads which would make sense: Stream (Reader + Writer, rpimariy for filtering
    - Partials (improvement of Currying)
