# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestParseKeyword(RSLTestCase):

    @evaluate_docstring
    def test_simple_keyword(self, rc):
        '''
        .assign s = "TEST:Hello world!"
        .exit "${s:TEST}"
        '''
        self.assertEqual("Hello world!", rc)

    @evaluate_docstring
    def test_keyword_as_variable(self, rc):
        '''
        .assign kw = "KEYWORD"
        .assign s = "KEYWORD:Hello!"
        .exit "${s:${kw}}"
        '''
        self.assertEqual("Hello!", rc)

    @evaluate_docstring
    def test_keyword_missmatch(self, rc):
        '''
        .assign s = "TEST:Hello world!"
        .exit "${s:test}"
        '''
        self.assertEqual("", rc)
        
    @evaluate_docstring
    def test_keyword_with_spaces(self, rc):
        '''
        .assign kw = "KEYWORD"
        .assign s = "KEYWORD: Hello!   "
        .exit "${s:${kw}}"
        '''
        self.assertEqual("Hello!", rc)
        