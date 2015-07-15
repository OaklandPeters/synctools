
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
- See how hard it would be to get my custom Monad.Composable working
- Extra monads which would make sense: Stream (Reader + Writer, rpimariy for filtering
    - Partials (improvement of Currying)
