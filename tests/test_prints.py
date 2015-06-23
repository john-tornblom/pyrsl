# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import sys

from utils import RSLTestCase
from utils import evaluate


class TestIfStatements(RSLTestCase):

    @evaluate
    def testPrintString(self, rc):
        '''
        .print "Hello world!"
        '''
        output = sys.stdout.getvalue().strip()
        self.assertEquals(output, "test_prints.testPrintString: 2:  INFO:  Hello world!")
        
    @evaluate
    def testPrintSubstitusionVariable(self, rc):
        '''
        .assign s = "world"
        .print "Hello ${s}!"
        '''
        output = sys.stdout.getvalue().strip()
        self.assertEquals(output, "test_prints.testPrintSubstitusionVariable: 3:  INFO:  Hello world!")
        
    @evaluate
    def testPrintDoubleDollar(self, rc):
        '''
        .assign s = "$$world"
        .print "Hello ${s}!"
        '''
        output = sys.stdout.getvalue().strip()
        self.assertEquals(output, "test_prints.testPrintDoubleDollar: 3:  INFO:  Hello $world!")
        
        
        

