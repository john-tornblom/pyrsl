pyrsl |Build Status| |Coverage Status|
======================================

pyrsl is an interpreter for a language called RSL (Rule Specification Language).
RSL is commonly used as a template language to express transformations from a
`BridgePoint <https://www.xtuml.org>`__ model into a textual representation,
e.g. when writing model compilers or when generating html documentation from a
model.

Installation
~~~~~~~~~~~~
POSIX users with python available on thier system may grab **gen_erate.pyz**
from `a release <https://github.com/xtuml/pyrsl/releases>`__. The .pyz
file contain pyrsl and all of its dependencises, and may be executed directly
without installing anything:

::

    $ chmod +x gen_erate.pyz
    $ ./gen_erate.pyz -h

Optionally, the .pyz file may be added to your PYTHONPATH:

::

    $ export PYTHONPATH=some/path/gen_erate.pyz
    $ python -m rsl.gen_erate -h

pyrsl is also available from pypi:

::

    $ python -m pip install pyrsl
    $ python -m rsl.gen_erate -h


Windows
*******
Generally, Windows users don't have python installed. However, `pyrsl 
releases <https://github.com/xtuml/pyrsl/releases>`__ include
**gen_erate.exe** that contain pyrsl and all of its dependencies, including
python.

Command Line Options
~~~~~~~~~~~~~~~~~~~~
To remain backwards compatable with `the original RSL interpreter
<https://github.com/xtuml/generator>`__, some command line options are a bit
confusing. Also, some of the options are not used by pyrsl.

pyrsl also contain a few additional command line options not available
in the original RSL interpreter:

  -include    Add a path to list of dirs to search for include files.
  -diff       Save a diff of all emits to a filename.
  -emit       Chose when to emit, i.e. never, on change, or always.
  -force      Make read-only emit files writable.
  -integrity  check the model for integrity violations upon program exit

For more information, see the help text by appending -h to the command line
when executing gen_erate.
    
Language Reference
~~~~~~~~~~~~~~~~~~
See `BridgePoint UML Suite Rule Specification Language
<https://cdn.rawgit.com/xtuml/pyrsl/master/doc/rsl_language_reference.html>`__.

Developer Notes
~~~~~~~~~~~~~~~
pyrsl depend on pyxtuml, see its `github page
<https://github.com/xtuml/pyxtuml>`__ for install instructions.

Test suites
***********
pyrsl contain a set of unit tests that may be executed:

::

    $ git clone https://github.com/xtuml/pyrsl.git
    $ cd pyrsl
    $ python setup.py test

Bundling gen_erate
******************
pyrsl may be bundled into a self contained file with a limited amount of external
dependencies. **gen_erate.exe** may be produced by issuing the following command
on a windows machine where python, ply and pyrsl are installed:

::

    $ python setup.py py2exe -O2 -c -b1 -p xtuml,rsl

Note that binaries produced by py2exe depend on MSVCR90.dll which is distributed
with the `Microsoft Visual C++ 2008 Redistributable Package <https://www.microsoft.com/en-us/download/details.aspx?id=29>`__

To produce **gen_erate.pyz**, a python zip app that is executable and easy to
distribute to POSIX compatable operating systems where python is allready
available, use the setup.py bundle command.

::

    $ python setup.py bundle


Customizing gen_erate
*********************
pyrsl may be extended to include additional builtin functions, i.e. bridges,
and additional string formatters. The extensions may be added to your own pyz
file when invoking the setup.py bundle command:

::

    $ python setup.py bundle -o gen_erate.pyz -m examples/customization.py
    $ ./gen_erate.pyz -nopersist -arch examples/customization_test.arc
    Running my custom version of gen_erate
    customization_test.arc: 4:  INFO:  the md5 of 'hello world' is 619d201e5209d3d52342cc5b6616b0cf
    customization_test.arc: 11:  INFO:  the md5 of hello world is 5eb63bbbe01eeed093cb22bb8f5acdc3

See `customization.py <https://github.com/xtuml/pyrsl/blob/master/examples/customization.py>`__
and `customization_test.arc <https://github.com/xtuml/pyrsl/blob/master/examples/customization_test.arc>`__
for more information.

Reporting bugs
~~~~~~~~~~~~~~
If you encounter problems with pyrsl, please `file a github
issue <https://github.com/xtuml/pyrsl/issues/new>`__. If you plan on
sending pull request which affect more than a few lines of code, please file an
issue before you start to work on you changes. This will allow us to discuss the
solution properly before you commit time and effort.

License
~~~~~~~
pyrsl is licensed under the GPLv3, see LICENSE for more information.

.. |Build Status| image:: https://travis-ci.org/xtuml/pyrsl.svg?branch=master
   :target: https://travis-ci.org/xtuml/pyrsl
.. |Coverage Status| image:: https://coveralls.io/repos/xtuml/pyrsl/badge.svg?branch=master
   :target: https://coveralls.io/r/xtuml/pyrsl?branch=master

