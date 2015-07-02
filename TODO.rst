
Project Refactoring
---------------------
- Add requirements.txt: fn.py
- Folder structure: synctools/synctools/, test/, test/data/
- README.rst, with examples
- unittests: based on files
    - requires making the CSS thing support the files --> put in try/catch block
- Unify the html get method between the HTML and css versions (get as text, then HTML parses it)
- contributors
- setup.py: 

Medium-Range
--------------
- Build a web-scrapping example based on this.
    - Publish as tutorial online for Functional Python
    - Maybe... 
- Rewrite F() function as Composable monad (work in currying functionality)
- Think hard about how to write a better partial()/F() function to allow partial on 2nd/3rd arguments
    - Idea: *arguments -> if any == _ --> is_partial --> returns object whose __call__ fills in those '_' args


Side
-------
- My own version of Monads library, Composable, Partials, Stream (based on reader/writer?)
- Consider if '_' can be improved. I would like it if `_(value)` -> operator.call(value)
- Very simply bump.py script, using argparse etc. `bump`, `bump --minor`
    - In long run: `bumptools`, to bump version number, git tags (and tags based on version)
