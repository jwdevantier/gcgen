.. _sec-getting-started:

Getting Started
###############


Example
=======
Let's start by way of an example. Note that several concepts are introduced
here such as snippets, scope and the gcgen configuration file format - we will
cover all of these in the coming sections, this example will just serve to
illustrate the concept.

Consider the following toy example, where the modulo (``mod``) and exponent
(``exp``) functions are hand-written, but we wish to generate the functions for
addition (``add``), subtraction (``sub``), division (``div``) and multiplication
(``mul``):

.. code-block::
    :caption: my_mathlib.py - before code generation
    :linenos:
    :emphasize-lines: 7, 8

    """This library contains some arithmetic functions"""

    def mod(x, y):
        return x % y


    # <<? common_math_funcs [["add", "+"], ["sub", "-"], ["div", "/"], ["mul", "*"]]
    # ?>>


    def exp(number, exponent):
        return number ** exponent


Note the highlighted lines - these identify the start- and end of a *snippet*.
Snippets are regions of auto-generated code in an otherwise hand-written source
file.
In this case, it is referencing some snippet called ``common_math_funcs``, when
gcgen is run, it will resolve this name to a function (an implementation) of
the snippet, which defines, through code, what the output should be.

The following configuration file implements the snippet, starting at line 5,
and tells gcgen to process the ``my_mathlib.py``, expanding any snippets, by
defining the ``gcgen_parse_files`` hook in line 27-30:

.. literalinclude:: ../examples/01_intro/gcgen_conf.py
    :caption: gcgen_conf.py -- gcgen configuration file
    :language: python
    :linenos:

Given this configuration file, running ``gcgen`` changes ``my_mathlib.py`` 
to have the following contents:

.. literalinclude:: ../examples/01_intro/my_mathlib.py
    :caption: my_mathlib.py - after code generation
    :language: python
    :linenos:


This example is a toy example, it demonstrates the basic concept, but
cannot really illustrate the potential of code generation.
As you come to understand scope and how subdirectories in your projects 
can contain their own `gcgen_conf.py` files which extend the scope, define new
snippets or override the implementation of existing ones, 


A high-level introduction to gcg
================================

Snippets & Generators
~~~~~~~~~~~~~~~~~~~~~
gcg supports two forms of code generation, snippets and generators, both
generate code using a :ref:`section <sec-ref-section>`, which provides a
convenient API for writing output, lines and handling indentation.

:ref:`Snippets <sec-ref-snippets>`, as shown above, mark regions within a
file, whose contents are auto-generated and will be rewritten each time gcgen
is run.

By contrast :ref:`generators <sec-ref-generators>` are functions in a gcgen
file (see next paragraph), which are mostly useful when generating files,
where the number and naming of the files is dynamic and depends on some input
data or model.

Each snippet and generator are passed two objects, a
:ref:`section <sec-ref-section>` as mentioned before, and a
:ref:`scope <sec-ref-scope>`.

Scope
~~~~~
The :ref:`scope <sec-ref-scope>` functions as a lexical scope or a layered
dictionary. When looking up a variable in a scope, the key is first checked
against the inner-most scope, the instance you are holding. If the key is not
found, the key is then searched for in the parent scope, and so on, until
reaching the top scope.

In essence this allows a derived/child scope to set values in its own scope
without impacting the parent scope(s), while still being able to read values
from the parent scopes.

Each subdirectory containing a :ref:`gcgen file <sec-ref-gcgen-file>` creates
a new scope, and the configuration file may modify the scope's definitions by
implementing the :ref:`gcgen_scope_extend <sec-ref-conf-extend>` function.

Each generator and each file being parsed for snippets gets their own scope.


The gcgen file(s)
~~~~~~~~~~~~~~~~~
Both snippets and generators are defined in a 
:ref:`gcgen file <sec-ref-gcgen-file>`. These files are always named 
``gcgen_conf.py``.
When running ``gcgen`` inside a project, these files are imported and their
definitions are used.

These files define snippets, generators, mark which files in a directory should
be parsed (meaning, scanned for snippets to expand) and they manage the
:ref:`scope <sec-ref-scope>`, which is passed along to each snippet and
generator when called.


The compile process
~~~~~~~~~~~~~~~~~~~
.. _sec-intro-compile:

The gcgen compile process traverses down the project hierarchy of directories,
importing each directory's :ref:`gcgen file <sec-ref-gcgen-file>` as they
encounter them.

After importing a :ref:`gcgen file <sec-ref-gcgen-file>`, they create a new
child scope and run the :ref:`gcgen_scope_extend <sec-ref-conf-extend>` hook,
if defined, which can add or remove variables from the scope.

Furthermore, the compiler also maintains a mapping of snippet definitions.
Any snippets defined in the :ref:`gcgen file <sec-ref-gcgen-file>` extend the
mapping, possibly overriding similarly named snippets from parent directories.
These snippet definitions, in turn, are available for use in any file contained
in the current directory, or any of its subdirectories.

Snippet and generator execution is done in a depth-first manner, meaning the
snippets and generators in the deepest subdirectories are executed first, and
any snippets and generators in the project root directory are executed last.
