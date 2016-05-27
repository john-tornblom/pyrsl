# encoding: utf-8
# Copyright (C) 2016 John Törnblom
import string

from utils import RSLTestCase
from utils import evaluate_docstring
from utils import expect_exception

from rsl.parse import ParseException



def buffer_docstring(f):
    tmpl = string.Template('''
        .function f
$value
        .end function
        .invoke res = f()
        .print "$${res.body}"
        .exit res.body
    ''')

    def wrapper(self):
        filename = f.__module__ + '.' + f.__name__
        text = tmpl.substitute(value=f.__doc__)
        rc = self.eval_text(text, filename)

        return f(self, rc)

    return wrapper


class TestLiteral(RSLTestCase):

    @expect_exception(ParseException)
    @buffer_docstring
    def test_dot(self, rc):
        '.'
        pass

    @buffer_docstring
    def test_dotdot(self, rc):
        '..'
        self.assertEqual(".\n", rc)

    @expect_exception(ParseException)
    @buffer_docstring
    def test_dollar(self, rc):
        '$'
        pass

    @buffer_docstring
    def test_dollardollar(self, rc):
        '$$'
        self.assertEqual("$\n", rc)

    @buffer_docstring
    def test_dotdot_comment(self, rc):
        '..comment'
        self.assertEqual(".comment\n", rc)


