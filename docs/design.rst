.. _sec-design:

Design Choices
==============

This document should give you a better idea of the principles behind the
design of Ghostwriter. Hopefully this gives you a better sense of the
tradeoffs involved and why each choice was made.

Keep it simple (KISS)
~~~~~~~~~~~~~~~~~~~~~
This project does not try to radically redefine code-generation or
introduce a novel hybrid template/code DSL.
Instead it uses plain Python, introducing only the concept of a
snippet, a region of code within a source file, whose contents is
managed by a corresponding Python function which uses a simple emitter
class to write plain lines of text and manage indentation.

It's very tempting to think a problem requires a new (bad) DSL, and
even those DSLs which start out small and self-contained often bloat
with features and complexity as an ever-increasing set of use-cases
are supported.

Use a general-purpose language (Python)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Not using a bespoke DSL reduces the barrier to entry in two ways.
Firstly, DSLs are very hard to get right, I learned this from fighting
extensively with Terraform and Ansible, both wonderful tools with unfortunate
DSLs.

Secondly, using a widely used language with the standard approach to
organizing the code means that existing code editors, IDEs and analysis
tools just work.
Refactoring, type analysis, linting and external libraries all work
just as expected.

Similarly, it allows a fringe tool to reap the benefits of popularity. 
The Python ecosystem has packages for interacting with pratically every
database, serialization format that exists.

Finally, if you are already familiar with Python, the barrier to entry is
lower still. If not, knowledge of Python is much more transferable and
conducive to CV polishing than expertise in a bespoke, fringe DSL.

Separate code-generation logic from regular content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are two benefits to moving code-generation code out into separate
Python files. Firstly, it reduces the amount of noise in the target files. 
Secondly, following a standard Python project structure is what ensures
full support from IDE's, code analysis- and unit-testing tools and more.
It is also how it becomes easy to factor out common functionality into
utility code and so on.

Mix hand-written and generated code in files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
By allowing a mixture of hand-written and generated code in the same file,
we encourage granular use of code-generation. This ideally prevents pulling
in more and more code into templates.
