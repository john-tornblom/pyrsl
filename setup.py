#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import logging
import unittest
import os
import sys
import stat
import zipfile

try:
    from setuptools import setup
    from setuptools import Command
    from setuptools.command.build_py import build_py
except ImportError:
    from distutils.core import setup
    from distutils.core  import Command
    from distutils.command.build_py import build_py


logger = logging.getLogger('setup')
logging.basicConfig(level=logging.DEBUG)


class BuildCommand(build_py):
    
    def run(self):
        import rsl

        rsl.parse_text('', '')
        build_py.run(self)


class TestCommand(Command):
    description = "Execute unit tests"
    user_options = [('name=', None, 'Limit testing to a single test case or test method')]

    def initialize_options(self):
        self.name = None
    
    def finalize_options(self):
        if self.name and not self.name.startswith('tests.'):
            self.name = 'tests.' + self.name

    def run(self):
        if self.name:
            suite = unittest.TestLoader().loadTestsFromName(self.name)
        else:
            suite = unittest.TestLoader().discover('tests')
        
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        exit_code = not runner.run(suite).wasSuccessful()
        sys.exit(exit_code)


class BundleCommand(Command):
    description = "Bundle pyrsl into a self-contained and executable pyz archive"
    user_options = [('main=', 'm', 'Path to a customized entry point'),
                    ('output=', 'o', 'Output path for the bundled pyz file')]

    def initialize_options(self):
        import rsl
        
        rsl.parse_text('', '')
        self.main = None
        self.output = 'gen_erate.pyz'
        
    def finalize_options(self):
        pass

    def run(self):
        import ply
        import rsl
        import xtuml

        logger.info('Using ply v%s', ply.__version__)
        logger.info('Using pyxtuml v%s', xtuml.version.release)
        logger.info('Using pyrsl v%s', rsl.version.release)
        
        dirname = os.path.dirname(self.output) or os.getcwd()
        dirname = os.path.abspath(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(self.output, 'wb') as outfile:
            outfile.write(b'#!/usr/bin/env python\n')
        
        with zipfile.PyZipFile(self.output, mode='a') as zf:
            if self.main:
                with open(self.main, 'r') as f:
                    main = f.read()
            else:
                main = ('from rsl import gen_erate\n'
                        'gen_erate.main()\n')
            
            zf.writestr('__main__.py', main)
            for mod in [ply, xtuml, rsl]:
                dirname = os.path.dirname(mod.__file__)
                for filename in os.listdir(dirname):
                    if filename.endswith('.py'):
                        path = dirname + os.path.sep + filename
                        zipname = mod.__name__ + os.path.sep + filename
                        zf.write(path, zipname)
                        logger.debug('Added %s', path)
                        
        st = os.stat(self.output)
        os.chmod(self.output, st.st_mode | stat.S_IEXEC)
        
        logger.info('Bundle successfully saved to %s', self.output)


opts = dict(name='pyrsl',
            version='2.1.0', # ensure that this is the same as in rsl.version
            description='Interpreter for the Rule Specification Language (RSL)',
            author='John Törnblom',
            author_email='john.tornblom@gmail.com',
            url='https://github.com/xtuml/pyrsl',
            license='GPLv3',
            classifiers=[
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Topic :: Software Development :: Interpreters',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6'],
            keywords='rsl xtuml bridgepoint',
            packages=['rsl'],
            data_files = [('share/gtksourceview-3.0/language-specs',
                           ['editors/gtksourceview/rsl.lang'])],
            requires=['ply', 'xtuml'],
            cmdclass={'build_py': BuildCommand,
                      'bundle': BundleCommand,
                      'test': TestCommand})


try:
    import py2exe
    opts['console'] = ['rsl/gen_erate.py']
    opts['zipfile'] = None
except:
    pass


setup(**opts)
