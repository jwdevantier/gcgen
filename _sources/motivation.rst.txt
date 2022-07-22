.. _sec-motivation:

Motivation
==========

*Warning* - this section will contain a great deal of pontification and reveal
the author as being more than a little arrogant with a lecturing streak.
Beyond that - you may wish to visit the :ref:`sec-getting-started` section first to
get a sense of how things work.

Writing reusable code is hard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Programming languages often force you to trade code-size for complexity.
The most complex features of a programming language typically lend themselves
to reducing repetition. From functors in Ocaml to generics in C#, metaclasses
in Python, macros in Lisp or implementing code-generation based on
annotations in Java.

Even if intimately familiar with these features, can you justify their
complexity? Programming is generally a team effort, liberally using
the most advanced features of your language, tend to create code
which not all colleagues can follow or extend in meaningful ways.
Simpler code is more inclusive code.


On top of this, most organizations use multiple languages.
Mastering the features of all to write reusable code becomes harder still.

Additionally, while some organizations have internal package repositories,
few have them for all languages used in the organization, so sharing code
across projects becomes problematic. Writing and distributing reusable
code is a hard problem.

Code is liability
~~~~~~~~~~~~~~~~~
On the other hand, writing reams of "simple", repetitive code presents,
another problem: code is a liability, not an asset. As a codebase grows,
the architecture ossifies, it becomes harder to refactor, and keeping the
code maintainable in face of changing requirements becomes increasingly
expensive.


Summary
~~~~~~~
* Reusable code typically leverages advanced language features
   * May be harder to understand for colleagues, whether junior or unfamiliar with the language
   * May be harder to debug and introspect - Java annotations and most macro systems are rightly feared because of this
* Organizations tend to accumulate languages, tools and frameworks over time
   * More languages and DSLs to master
   * More code to manage, maintain and refactor
* Multiple configuration tools and DSLs in use
   * Do you grasp and exploit the features each provide to keep things DRY?
   * Do your colleagues?

