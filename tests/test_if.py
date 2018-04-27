# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestIf(RSLTestCase):

    @evaluate_docstring
    def test_single_if_true(self, rc):
        '''
        .if ( 0 == 0 )
            .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_single_if_false(self, rc):
        '''
        .if ( 0 == 1 )
            .exit 0
        .end if
        .exit 1
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_if_with_comments(self, rc):
        '''
        .if ( 0 == 0 ) .//
            .exit 1    .//
        .elif (0 == 1) .//
            .exit 2    .//
        .end if        .//
        .exit 0
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_elif_first(self, rc):
        '''
        .assign x = 0
        .if (1 == 0)
            .assign x = 1
        .elif (1 == 1)
            .assign x = 2
        .else
            .assign x = 3
        .end if
        .exit x
        
        '''
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_elif_middle(self, rc):
        '''
        .if ( 0 == 1 )
            .exit 0
        .elif ( 0 == 2)
            .exit 1
        .elif (0 == 0)
            .exit 2
        .elif (0 == 3)
            .exit 3
        .else
            .exit 4
        .end if
        .exit 5
        '''
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_elif_last(self, rc):
        '''
        .if ( 0 == 1 )
            .exit 0
        .elif ( 0 == 2)
            .exit 1
        .elif (0 == 0)
            .exit 2
        .end if
        .exit 3
        '''
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_if_elif_else(self, rc):
        '''
        .if ( 0 == 1 )
            .exit 0
        .elif ( 0 == 2)
            .exit 1
        .elif (0 == 3)
            .exit 2
        .else
            .exit 3
        .end if
        .exit 4
        '''
        self.assertEqual(3, rc)
        
        
