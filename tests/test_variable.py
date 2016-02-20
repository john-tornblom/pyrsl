# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestVariable(RSLTestCase):

    @evaluate_docstring
    def test_variable_with_keyword_name_empty(self, rc):
        '''
        .assign empty = 1
        .exit "${empty}"
        '''
        self.assertEqual("1", rc)
        
    @evaluate_docstring
    def test_variable_with_keyword_name_where(self, rc):
        '''
        .assign where = 1
        .exit "${where}"
        '''
        self.assertEqual("1", rc)

    @evaluate_docstring
    def test_variable_with_keyword_name_in(self, rc):
        '''
        .assign in = 1
        .exit "${in}"
        '''
        self.assertEqual("1", rc)

    @evaluate_docstring
    def test_variable_with_type_name(self, rc):
        '''
        .assign string = 1
        .exit "${string}"
        '''
        self.assertEqual("1", rc)

