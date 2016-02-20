# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring

import rsl


class TestScopeRule(RSLTestCase):

    @evaluate_docstring
    def test_access_global_from_function(self, rc):
        '''
        .assign x = 5
        .function f
            .exit x
        .end function
        .invoke f()
        '''
        self.assertIsInstance(rc, rsl.symtab.SymtabException)
        
    @evaluate_docstring
    def test_recursive_function(self, rc):
        '''
        .function f
          .param integer x
          .assign y = x
          .if (x > 0)
            .invoke res = f(x - 1)
          .end if
          .assign attr_value = y
        .end function
        
        .invoke res = f(3)
        
        .exit res.value
        '''
        self.assertEqual(rc, 3)
        
