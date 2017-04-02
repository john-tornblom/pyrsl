# encoding: utf-8
# Copyright (C) 2017 John Törnblom

from utils import RSLTestCase
from utils import lint_docstring


class TestLinting(RSLTestCase):
    
    def setUp(self):
        RSLTestCase.setUp(self)
        self.metamodel.define_class('Cls', [])
        
    @lint_docstring
    def test_empty_text(self, rc):
        ''
        self.assertEqual(0, rc)

    @lint_docstring
    def test_function(self, rc):
        '''
        .function f
        .end function
        '''
        self.assertEqual(0, rc)

    @lint_docstring
    def test_function_duplication(self, rc):
        '''
        .function f
        .end function
        .function f
        .end function
        '''
        self.assertEqual(1, rc)

    @lint_docstring
    def test_unknown_class(self, rc):
        '''
        .create object instance x of Cls
        .select any x from instances of Cls
        .select many x from instances of Cls

        .create object instance x of Missing_Cls
        .select any x from instances of Missing_Cls
        .select many x from instances of Missing_Cls
        '''
        self.assertEqual(3, rc)

    @lint_docstring
    def test_lowercased_class(self, rc):
        '''
        .create object instance x of cls
        '''
        self.assertEqual(1, rc)

