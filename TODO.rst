
Project Refactoring
---------------------
- BUG: PATH_SPLIT_REGEX not working for live urls
    - Solution: make it work for local paths AND live paths
- README.rst, with examples
- Remove unused test/data/ files.
- Make read_html.py mimic the structure of read_html_minimal.py
- Remove all use of F() and _() from read_html.py
- contributors
- setup.py:

Medium-Term
-------------
- Revise Monadic, along with tests.
    - Monads are now defined as applying to *functions*, not values.
    - Remove use of Container -> functor/applicative/monad do not necessarily have a getValue
    - Use abcs: abstract functions for Functor, Applicative, Monad
        - Four core functions to rename: unit, fmap, amap, bind
        - Extra names: transform, lift, apply (overwrites a builtin though), fix/affix, wrap
        - Maybe: lift - type constructor, replaces unit
        - Maybe: bind - chains operations while returning same functor/monad
        - Maybe: unit - returns the empty constructor. This is to satisfy Monoid laws (IE identity)
        - Recall monadic laws:   unit(x) >> f == f(x), m >> unit == m,
            - Associative: (m >> f) >> g == m >> (f >> g)
    - Add more informative __repr__ to Composable. "<Composable function {fname} at {fid}>"
        - Idea: have it print nested function names (if they exist and are not <lambda>)
            ... basically keep recursing if _callback isinstance Composable
    - Fill in Composable, Partial methods for fmap/amap
- See how hard it would be to get my custom Monad.Composable working
    - Test manually as replacement for F()
- Extra monads which would make sense: Stream (Reader + Writer, rpimariy for filtering
    - Partials (improvement of Currying)
