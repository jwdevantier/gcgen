.. _sec-ref-gcgen-file:


gcgen file
##########

This page describes gcgen files, the files named `gcgen_conf.py` which may be located
in any subdirectory of the project, and which drive all aspects of code
generation using gcgen.

The gcgen files provide hooks to modify the scope in the context of their
directory and any subdirectories, hooks to specify which files should be parsed
for snippets. Snippet and generator definitions, file indentation rules and
more.

gcgen requires a `gcgen_conf.py` file in each directory whose files might contain
snippets to parse or where generators should create new files from scratch.
This in turn encourages keeping snippet definitions and specific scope variables
local to those subdirectories which use them.


To see more about using gcgen in a new project, consult
:ref:`sec-ref-new-project`.
To better understand how the scope and subdirectories work together, see
:ref:`sec-ref-scope`.

Finally, this page will not cover defining :ref:`snippets <sec-ref-snippets>`
or :ref:`generators <sec-ref-generators>` see their sections for details on
that.

.. _sec-ref-conf-parse-files:

Parse files
===========

When adding :ref:`snippets <sec-ref-snippets>` to a file, you also need to
tell gcgen to parse that file for code-generation to work.

In the same directory, create a ``gcgen_conf.py`` file and implement the
``gcgen_parse_files`` hook like so:

.. code-block:: python3
    :caption: gcgen_conf.py - parse files
    :linenos:


    def gcgen_parse_files():
        return [
            "my_file.c",
            "my_other_file.go"
        ]

This extra step may seem onerous, but it drastically speeds up the compilation
process, which would otherwise have to parse every file, line-by-line.
Furthermore, it requires creating ``gcgen_conf.py`` files in each directory which
uses gcgen for code-generation. This both makes it easier to identify where
gcgen is used, and encourages keeping snippet definitions and relevant scope
entries local to the consuming code.

Since ``gcgen_parse_files`` is a function, you could generate the list of files:

.. code-block:: python3
    :caption: gcgen_conf.py - parse files, parse all python files
    :linenos:

    from pathlib import Path


    def gcgen_parse_files():
        # return all .py files in the current directory
        return list(Path(".").glob("*.py"))


.. _sec-ref-conf-extend:

Extend the Scope
================

The introduction touches on the :ref:`compile process <sec-intro-compile>`,
noting that each gcgen file may implement a function which modifies the
:ref:`scope <sec-ref-scope>` passed to their own snippets & generators, and all
of their subdirectories.

.. code-block:: python3
    :caption: gcgen_conf.py - scope extend hook
    :linenos:

    from gcgen.api import Scope

    
    def gcgen_scope_extend(scope: Scope):
        # add some definitions
        scope["name"] = "Jane"
        scope["surname"] = "Doe"
        # can also remove definitions
        # (this does not affect the parent scope(s))
        del scope["something"]


Configure indentation
=====================
.. _sec-ref-conf-indent-by:

Each :ref:`snippet <sec-ref-snippets>` and :ref:`generator <sec-ref-generators>`
is passed an :ref:`emitter <sec-ref-emitter>` object which is used to produce
the generated output and to indent & dedent lines.

In the ``gcgen_conf.py`` file, you can define the characters used to indent on a
per-filetype basis:


.. code-block:: python3
    :caption: gcgen_conf.py - configure indentation
    :linenos:

    from gcgen.api import Scope

    
    gcgen_indent_by = {
        # indent python files by 4 spaces
        "py": "    ",
        # indent go files by one tab
        "go": " ",
    }


Typically, indentation would be defined in the top-level ``gcgen_conf.py`` file, for
all subdirectories to inherit.
However, a ``gcgen_conf.py`` in some subdirectory can implement ``gcgen_indent_by``
to configure indentation for further file types.
