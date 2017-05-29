Getting Started
===============

Installation
------------
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


.. tip:: If you encounter performance issues when using pyrsl, consider the
	 alternative python implementation `pypy <http://pypy.org>`__. Depending
	 on the context in which pyrsl is in use, pypy may provide a significant
	 speedup.

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

