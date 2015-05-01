# encoding: utf-8
# Copyright (C) 2014 John Törnblom

import sys

from utils import RSLTestCase
from utils import evaluate


class TestIfStatements(RSLTestCase):

    @evaluate
    def testPrintString(self, rc):
        '''
        .print "Hello world!"
        '''
        output = sys.stderr.getvalue().strip()
        self.assertEquals(output, "Hello world!")
        
    @evaluate
    def testPrintSubstitusionVariable(self, rc):
        '''
        .assign s = "world"
        .print "Hello ${s}!"
        '''
        output = sys.stderr.getvalue().strip()
        self.assertEquals(output, "Hello world!")
        
    @evaluate
    def testPrintDoubleDollar(self, rc):
        '''
        .assign s = "$$world"
        .print "Hello ${s}!"
        '''
        output = sys.stderr.getvalue().strip()
        self.assertEquals(output, "Hello $world!")
        
        
        

