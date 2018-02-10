# encoding: utf-8
# Copyright (C) 2018 John Törnblom
'''
Example on how to extend the functionality of rsl.gen_erate by defining a custom
string formatter that invoke clang-format.

Bundle into gen_erate.pyz using the --main flag to setup.py, e.g.
    python setup.py bundle --main=examples/clangformat.py
'''
import sys
import subprocess

from rsl import gen_erate
from rsl import string_formatter


@string_formatter('t')
def format_cpp(s):
    proc = subprocess.Popen('clang-format',
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    proc.stdin.write(s)
    proc.stdin.close()
    res = proc.stdout.read()
    proc.wait()

    if proc.returncode:
        return s
    else:
        return res


print('Running my custom version of gen_erate')
rc = gen_erate.main()
sys.exit(rc)

