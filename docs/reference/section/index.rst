.. _sec-ref-section:

Section
################

All :ref:`snippets <sec-ref-snippets>` and :ref:`generators <sec-ref-generators>`
are provided an section, which they must use to generate their output.

The section provides a convenient if simple abstraction for output generation.
The main objective of the API is to control lines and indentation.
This permits gcgen to ensure that output generated from a snippet is always
properly indented, such that each line of the snippet are indented relative
to the indentation of the snippet start line.


Example
=======

.. code-block:: python3

    from gcgen.api import Scope, Section, Json, snippet

    @snippet("my-snippet")
    def include_file_output(sec: Section, scope: Scope, val: Json):
        if isinstance(v, str):
            filename = v
        else:
            raise RuntimeError("expected filename passed as string argument")
        sec.emitln(f"""with open({filename!r}) as fh:""")
        sec.indent()
        sec.emitln("for lines in fh.readlines():")
        sec.indent()
        sec.emitln("...")


Given the following file:

.. code-block:: python3
    :caption: myfile.py

    def some_function():
        # <<? include_file_output "/etc/issue"
        # ?>>


The expanded output would become:

.. code-block:: python3
    :caption: myfile.py

    def some_function():
        # <<? include_file_output "/etc/issue"
        with open("/etc/issue") as fh:
            for lines in fh.readlines()
                ...
        # ?>>


**Note**: While the section controls the level of indentation, the characters
used to indent the line is actually determined by
:ref:`gcgen_indent_by <sec-ref-conf-indent-by>`, which can be used to define
how indentation should be handled on a file-type basis.

Section API
===========
.. autoclass:: gcgen.api.Section
    :members:
    :noindex: