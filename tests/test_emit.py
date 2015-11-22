# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import os
import time

from utils import RSLTestCase
from utils import evaluate


class TestEmit(RSLTestCase):

    @evaluate
    def testEmitHelloWorld(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertRegexpMatches(f.read(), "Hello world\n")
        
    def testEmitWithoutLinebreak_Case1(self):
        text = 'Hello ' + '\\' + '\n' + 'world' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\n")
            
    def testEmitWithoutLinebreak_Case2(self):
        text = 'Hello world' + '\\' + '\\' + '\\' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\\n")
    
    def testEmitEscapedBackslash(self):
        text = 'Hello world' + '\\' + '\\' + '\n' 
        text+= 'Test\n'
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\\nTest\n")
    
    @evaluate
    def testEmitComment(self, rc):
        '''.//Hello world
        .comment No comment
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate
    def testEmitFlush(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate
    def testIncludeAfterEmit(self, rc):
        '''..exit 1
        .emit to file "/tmp/RSLTestCase"
        .include "/tmp/RSLTestCase"
        .exit 0
        '''
        self.assertEqual(1, rc)
            
    @evaluate
    def testEmitAfterClear(self, rc):
        '''
        Hello world
        .clear
        .emit to file "/tmp/RSLTestCase"
        '''
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
    
    @evaluate
    def testEmitFromFunction(self, rc):
        '''.function f
Hello world!
        .end function
        .invoke rc = f()
        .emit to file "/tmp/RSLTestCase"
        .exit rc.body
        '''
        
        self.assertEqual("Hello world!\n", rc)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")

    def testSupressEmit(self):
        self.runtime.emit = 'never'
        code = '''
        Test
        .emit to file "/tmp/RSLTestCase"
        '''
        path = "/tmp/RSLTestCase"
        if os.path.exists(path):
            os.remove(path)
        
        rc = self.eval_text(code, 'testSupressEmit')
        self.assertFalse(rc)
        
        self.assertFalse(os.path.exists(path))
        
    def testEmitOnChange(self):
        self.runtime.emit = 'change'
        code = '''
        Test
        .emit to file "/tmp/RSLTestCase"
        '''
        path = "/tmp/RSLTestCase"
        if os.path.exists(path):
            os.remove(path)
        
        rc = self.eval_text(code, 'testEmitOnChange')
        self.assertFalse(rc)
        self.assertTrue(os.path.exists(path))
        
        t = os.path.getmtime(path)
        self.eval_text('test' + code, 'testEmitOnChange')
        self.assertNotEqual(t, os.path.getmtime(path))
        
        t = os.path.getmtime(path)
        self.eval_text('test' + code, 'testEmitOnChange')
        self.assertEqual(t, os.path.getmtime(path))
        
        