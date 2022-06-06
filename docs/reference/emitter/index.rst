.. _sec-ref-emitter:

The code emitter
################

All :ref:`snippets <sec-ref-snippets>` and :ref:`generators <sec-ref-generators>`
are provided an emitter, which they must use to generate their output.

The emitter provides a convenient if simple abstraction for output generation.
The main objective of the API is to control lines and indentation.
This permits gcgen to ensure that output generated from a snippet is always
properly indented, such that each line of the snippet are indented relative
to the indentation of the snippet start line.


Example
=======

.. code-block:: python3

    from gcgen.api import Scope, Emitter, snippet

    @snippet("my-snippet")
    def mysnippet(e: Emitter, s: Scope):
        f = Scope["filename"]  # assuming `filename` has been defined
        e.emitln(f"""with open({f!r}) as fh:""")
        e.indent()
        e.emitln("for lines in fh.readlines():")
        e.indent()
        e.emitln("...")


Given the following file:

.. code-block:: python3
    :caption: myfile.py

    def some_function():
        # [[start my-snippet
        # end]]


The expanded output would become:

.. code-block:: python3
    :caption: myfile.py

    def some_function():
        # [[start my-snippet
        with open("foo.txt") as fh:
            for lines in fh.readlines()
                ...
        # end]]


**Note**: While the emitter controls the level of indentation, the characters
used to indent the line is actually determined by
:ref:`gcgen_indent_by <sec-ref-conf-indent-by>`, which can be used to define
how indentation should be handled on a file-type basis.

Emitter API
===========
.. autoclass:: gcgen.api.Emitter
    :members:
    :noindex: