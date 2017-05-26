Developer Notes
===============

Bundling gen_erate
******************
pyrsl may be bundled into a self-contained file with a limited amount of external
dependencies. **gen_erate.exe** may be produced by issuing the following command
on a windows machine where python, ply and pyrsl are installed:

::

    $ python setup.py py2exe -O2 -c -b1 -p xtuml,rsl

Note that binaries produced by py2exe depend on MSVCR90.dll which is distributed
with the `Microsoft Visual C++ 2008 Redistributable Package
<https://www.microsoft.com/en-us/download/details.aspx?id=29>`__

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

.. code-block:: console

    $ python setup.py bundle -o gen_erate.pyz -m examples/customization.py
    $ ./gen_erate.pyz -nopersist -arch examples/customization_test.arc
    Running my custom version of gen_erate
    customization_test.arc: 4:  INFO:  the md5 of 'hello world' is 619d201e5209d3d52342cc5b6616b0cf
    customization_test.arc: 11:  INFO:  the md5 of hello world is 5eb63bbbe01eeed093cb22bb8f5acdc3

See `customization.py <https://github.com/xtuml/pyrsl/blob/master/examples/customization.py>`__
and `customization_test.arc <https://github.com/xtuml/pyrsl/blob/master/examples/customization_test.arc>`__
for more information.
