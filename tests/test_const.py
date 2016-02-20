# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestConstants(RSLTestCase):

    @evaluate_docstring
    def test_positive_integer(self, rc):
        '.exit 1'
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_negative_integer(self, rc):
        '.exit -1'
        self.assertEqual(-1, rc)

    @evaluate_docstring
    def test_positive_real(self, rc):
        '''
        .exit 1.1
        '''
        self.assertEqual(1.1, rc)
        
    @evaluate_docstring
    def test_negative_real(self, rc):
        '''
        .exit -1.1
        '''
        self.assertEqual(-1.1, rc)

    @evaluate_docstring
    def test_true(self, rc):
        '''
        .exit true
        '''
        self.assertEqual(True, rc)
        
    @evaluate_docstring
    def test_false(self, rc):
        '''
        .exit false
        '''
        self.assertEqual(False, rc)
        
    @evaluate_docstring
    def test_string(self, rc):
        '.exit "Hello"'
        self.assertEqual("Hello", rc)


    @evaluate_docstring
    def test_empty_string(self, rc):
        '''
        .exit ""
        '''
        self.assertEqual("", rc)
        
