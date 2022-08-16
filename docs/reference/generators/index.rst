.. _sec-ref-generators:

Generators
##########

Generators are simply hooks in the :ref:`gcgen file <sec-ref-gcgen-file>`, which
are executed as part of the compile process.

Snippets should be preferred to generators in most cases because:

* snippets allow mixing hand-written and generated code
* snippets allow using multiple snippets to build the final file (compositional)
* snippets provide a properly initialized :ref:`Section <sec-ref-section>`
  object
* ``gcgen`` ensures that either the full file is processed successfully or
  no changes are made to the file


However, in cases where the number of files to output itself is dynamic, then
using a generator is required.
The following example shows a simple generator:

.. code-block:: python3

    from gcgen.api import generator, Scope, write_file


    @generator
    def do_something(scope: Scope):
        with write_file("foo.txt") as section:
            section.emitln("line 1")
            section.emitln("line 2")
        with write_file("bar.txt") as section:
            section.emitln("line 1")
            section.emitln("line 2")
        ...


This particular generator uses the ``write_file`` helper, which provides an
``Section`` and which, if the code exits the context without raising an
exception, writes to the file given by the filename.
Note, just like for snippets, ``write_file`` operates on a temporary file first,
thereby preventing any files whose output is only half-way generated.

write_file helper
~~~~~~~~~~~~~~~~~

.. autoclass:: gcgen.api.write_file
    :members:
    :noindex: