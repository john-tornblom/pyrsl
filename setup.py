#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import logging
import unittest
import sys

from distutils.core import setup
from distutils.core import Command

import rsl


logging.basicConfig(level=logging.DEBUG)


class PrepareCommand(Command):
    description = "Prepare the source code by generating lexers and parsers"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        rsl.parse_text('', '')


class TestCommand(Command):
    description = "Execute unit tests"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestLoader().discover('tests')
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        exit_code = not runner.run(suite).wasSuccessful()
        sys.exit(exit_code)

long_desc = "pyrsl is an interpreter for the Rule Specification Language (RSL)"

setup(name='pyrsl',
      version=rsl.version.release,
      description='pyrsl',
      long_description=long_desc,
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/pyrsl',
      license='GPLv3',
      platforms=["Linux"],
      packages=['rsl'],
      requires=['ply', 'xtuml'],
      cmdclass={'prepare': PrepareCommand, 'test': TestCommand}
      )

