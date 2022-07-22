.. _sec-ref-installation:

Installing gcgen
################

Gcgen is available as a Python package from 
`PyPi <https://pypi.org/project/gdgen/>`_, and can be installed
with the Python package manager, pip.


User-wide
=========
Gcgen has no dependencies on any other Python package, thus, if you do not 
expect your code generation code to require additional libraries, you may
simply install gcgen globally for your user like so:

.. code-block:: 

    pip install --user gcgen


Isolated
========
Python projects can be installed using virtual environments to isolate their
dependencies from one another. This is often used to avoid conflicts between
requirements.

Note that gcgen has no dependencies so these steps are only useful if your
own code generation code will use additional dependencies, such as packages to
read in yaml files or extract information from databases.

The Python documentation has a tutorial explaining the use of virtual
environments in depth 
(`Python Venv Tutorial <https://docs.python.org/3/tutorial/venv.html>`_),
but the gist is this:

.. code-block:: bash

    # Create virtual environment folder `gcgen_venv`
    python3 -m venv gcgen_venv

    # Activate virtual environment folder (Linux, MacOS)
    # (see tutorial for windows instructions)
    source gcgen_venv/bin/activate

    # Python-related commands now operate in the virtual
    # environment context.
    (gcgen_venv) pip install gcgen
    (gcgen_venv) pip install some-other-python-package
    # ...


**Note** you have to activate the virtual environment each time you wish to
use gcgen.


Isolated, but global (pipx)
===========================

Another approach is to use the third-party package, pipx, which makes it easy
to install python packages providing command-line programs user-wide, while
still isolating them and their dependencies from one another in separate
virtual environments.


The gist of this approach is the the following:

Install pipx
~~~~~~~~~~~~
See the `Pipx Install guide <https://pypa.github.io/pipx/>`_ for details.

Install gcgen
~~~~~~~~~~~~~

.. code-block:: bash

    pipx install gcgen



(Optional) Install additional packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In pipx parlance, you may _inject_ extra packages into a given program's
virtual environment like so:

.. code-block:: bash

    pipx inject gcgen some-other-python-package


See the `pipx inject documentation <https://pypa.github.io/pipx/docs/#pipx-inject>`_
for more details.