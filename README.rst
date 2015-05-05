pyrsl |Build Status| |Coverage Status|
======================================

pyrsl is an interpreter for a language called RSL (Rule Specification
Language). RSL is commonly used as a template language to express
transformations from a `BridgePoint <https://www.xtuml.org>`__ model
into a textual representation, e.g. when writing model compilers or
when generating html documentation from a model.

Dependencies
~~~~~~~~~~~~
pyrsl depend on pyxtuml, see its `github page
<https://github.com/john-tornblom/pyxtuml>`__ for install instructions.

Installation
~~~~~~~~~~~~

Install from pypi:

::

    $ python -m pip install pyrsl

Or fetch the source from github:

::

    $ git clone https://github.com/john-tornblom/pyrsl.git
    $ cd pyrsl
    $ python setup.py prepare
    $ python setup.py install
   
Optionally, you can also execute a test suite:

::

    $ python setup.py test

Usage
~~~~~
The command line usage is as follows:

::
   
    $ python -m rsl.gen_erate [options] script.arc


where script.arc is an RSL template, also known as a archetype. [options]
may be a combination of the following:


::
   
    --version               show program's version number and exit
    --help, -h              show this help message and exit
    --import=PATH, -i PATH  import model information from PATH
    --include=PATH, -I PATH
                            add PATH to list of dirs to search for include files
    --emit=WHEN, -e WHEN    choose when to emit (never, change, always)
    --force, -f             make read-only emit files writable
    --diff=PATH, -d PATH    save a diff of all emits to PATH
    --verbosity, -v         increase debug logging level

    
Reporting bugs
~~~~~~~~~~~~~~
If you encounter problems with pyrsl, please `file a github
issue <https://github.com/john-tornblom/pyrsl/issues/new>`__. If you
plan on sending pull request which affect more than a few lines of code,
please file an issue before you start to work on you changes. This will
allow us to discuss the solution properly before you commit time and
effort.

License
~~~~~~~
pyrsl is licensed under the GPLv3, see LICENSE for more information.

.. |Build Status| image:: https://travis-ci.org/john-tornblom/pyrsl.svg?branch=master
   :target: https://travis-ci.org/john-tornblom/pyrsl
.. |Coverage Status| image:: https://coveralls.io/repos/john-tornblom/pyrsl/badge.svg?branch=master
   :target: https://coveralls.io/r/john-tornblom/pyrsl?branch=master

