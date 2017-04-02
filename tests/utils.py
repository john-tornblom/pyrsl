# encoding: utf-8
# Copyright (C) 2015-2017 John Törnblom

import unittest
import xtuml
import rsl


class RSLTestCase(unittest.TestCase):
    metamodel = None
    runtime = None
    includes = None
    
    def setUp(self):
        id_generator = xtuml.IntegerGenerator()
        self.metamodel = xtuml.MetaModel(id_generator)
        self.runtime = rsl.runtime.Runtime(self.metamodel)
        self.includes = ['./']
        
    def tearDown(self):
        del self.metamodel

    def eval_text(self, text, filename=''):
        ast = rsl.parse_text(text + '\n', filename)
        try:
            rsl.evaluate(self.runtime, ast, self.includes)
        except SystemExit as e:
            return e.code

    def lint_text(self, text, filename=''):
        ast = rsl.parse_text(text + '\n', filename)
        try:
            return rsl.lint_ast(self.metamodel, ast)
        except SystemExit as e:
            return e.code

        
def expect_exception(exception):
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator


def evaluate_docstring(f):
    return lambda self: f(self, self.eval_text(f.__doc__, 
                                               f.__module__ + '.' + f.__name__))


def lint_docstring(f):
    return lambda self: f(self, self.lint_text(f.__doc__, 
                                               f.__module__ + '.' + f.__name__))

