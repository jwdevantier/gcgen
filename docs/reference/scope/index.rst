.. _sec-ref-scope:

Scope
#####


Every :ref:`snippet <sec-ref-snippets>` and :ref:`generator <sec-ref-generators>`
are handed a scope when they execute.

Scopes work like nested dictionaries. Any new scope may be derived from an
existing scope. This means that during lookup, the new scope will first consult
its own entries, but if no entry is found, it will try its parent scope, and
so on until either an entry is found, or there are no more parent scopes to
search.

Scope Examples
==============

Get Value
~~~~~~~~~

.. doctest:: scope

    >>> from gcgen.api import Scope
    >>> s1 = Scope()
    >>> s1["name"] = "Jane"
    >>> s1["surname"] = "Doe"
    >>> s2 = s1.derive()
    >>> s2["surname"] = "Peterson"
    >>> s3 = s2.derive()
    >>> s3["profession"] = "Programmer"
    >>> s3["profession"]
    'Programmer'
    >>> s3["surname"]
    'Peterson'
    >>> s3["name"]
    'Jane'
    >>> s3["bank password"]
    Traceback (most recent call last):
    KeyError: 'bank password'


Note how entries from the inner-most scope have the highest precedence, as is
shown when the surname redefined in ``s2`` overshadows the original value set in
``s1``.


Set value
~~~~~~~~~~~~~
Here is an example to illustrate:

.. doctest:: scope

    >>> from gcgen.api import Scope
    >>> s1 = Scope()
    >>> s1["name"] = "Jane"
    >>> s1["surname"] = "Doe"
    >>> s2 = s1.derive()
    >>> s2["name"]
    'Jane'
    >>> s2["name"] = "John"
    >>> s2["name"]
    'John'
    >>> s1["name"]
    'Jane'

*Note*: setting a new value in a child scope just overshadows the original
definition, it does not affect any of the parent states.


Remove value
~~~~~~~~~~~~
Entries can be removed from a scope. Since modifying a scope should never impact
the parent scope, removal is actually done by inserting a special object called
a tombstone, to signal that the entry is removed and lookup should abort.

.. doctest:: scope

    >>> from gcgen.api import Scope
    >>> s1 = Scope()
    >>> s1["name"] = "Jane"
    >>> s2 = s1.derive()
    >>> s2["name"]
    'Jane'
    >>> del s2["name"]
    >>> s2["name"]
    Traceback (most recent call last):
    KeyError: 'name'
    >>> s1["name"]
    'Jane'

*Note*: 'deleting' an entry from a scope actually inserts a special entry which
marks the entry as removed, overshadowing any previous definition. The operation
does not impact any of the parent scopes.

How the scope is built
======================
The scope behaves like a dictionary, containing a set of variable definitions
which are set within the :ref:`gcgen_scope_extend <sec-ref-conf-extend>` of any
:ref:`gcgen files <sec-ref-gcgen-file>` on the path from the project root to
the directory in which the snippet is being called or the generator is being
run.

Take the following project as an example:

::

    .
    ├── gcgen_project.ini
    ├── gcgen_conf.py
    └── src
        ├── bar
        │   └── impl
        │       ├── file-a.py
        │       ├── file-b.py
        │       └── gcgen_conf.py
        ├── foo
        │   ├── gcgen_conf.py
        │   └── impl
        │       ├── gcgen_conf.py
        │       └── my_file.py
        └── gcgen_conf.py

In this case, the scope given to any snippet executing in ``file-a.py`` would be
built from:

1. ``gcgen_scope_extend`` in ``./gcgen_conf.py`` file (if defined)
2. ``gcgen_scope_extend`` in ``./src/gcgen_conf.py`` (if defined)
3. ``gcgen_scope_extend`` in the ``src/bar/impl/gcgen_conf.py`` file (if defined)


Similarly, the scope given to any snippet executing in ``my_file.py`` would be
built from:

1. ``gcgen_scope_extend`` in ``./gcgen_conf.py`` file (if defined)
2. ``gcgen_scope_extend`` in ``./src/gcgen_conf.py`` (if defined)
3. ``gcgen_scope_extend`` in ``src/foo/gcgen_conf.py`` (if defined)
4. ``gcgen_scope_extend`` in ``src/foo/impl/gcgen_conf.py`` (if defined)


To see how to implement the ``gcgen_scope_extend`` function, see
:ref:`sec-ref-conf-extend`.