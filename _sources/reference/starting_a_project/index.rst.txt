.. _sec-ref-new-project:

Starting a project
##################

Gcgen code should live alongside your project code. The typical use-case is
thus to configure gcgen to consider the root of your project the root of
the corresponding gcgen project.

How gcgen determines the project folder
=======================================
When gcgen runs, it will try to determine the root of the project. It does this
by examining the current directory, and then each parent directory in turn, first
looking for a ``gcgen_project.ini`` configuration file.
If this fails, it will re-start the search, this time looking for the ``.git``
folder which characterizes the root of a project using git.


If gcgen infers a different project root than you would like, then create the
``gcgen_project.ini`` file, which also serves to configure a few global settings,
or pass the ``-p`` flag, specifying the project path manually.


.. _sec-ref-prj-ini:

Configuring the project
=======================
To configure global gcgen settings for the project, create the
``gcgen_project.ini`` file. The default settings would correspond to the
following:

.. code-block:: ini
    :linenos:

    [parse]
    tag_start = <<?
    tag_end = ?>>

    [log]
    level = warning


The ``tag_start`` and ``tag_end`` values define the character-sequences which
will mark the start- and end of a snippet.

The log level value can be a string corresponding to any of the standard Python
logger's supported log levels:

* notset
* debug
* info
* warning
* error
* critical

A setting of ``warning`` means that any log entry of level notset, debug or info
is not shown.