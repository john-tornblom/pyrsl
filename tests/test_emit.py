# encoding: utf-8
# Copyright (C) 2015 John Törnblom
import os
import time

from utils import RSLTestCase
from utils import evaluate_docstring


class TestEmit(RSLTestCase):

    @evaluate_docstring
    def test_emit_hello_world(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertRegexpMatches(f.read(), "Hello world\n")
        
    def test_emit_without_linebreak_case1(self):
        text = 'Hello ' + '\\' + '\n' + 'world' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\n")
            
    def test_emit_without_linebreak_case2(self):
        text = 'Hello world' + '\\' + '\\' + '\\' + '\n' 
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\\n")
    
    def test_emit_escaped_backslash(self):
        text = 'Hello world' + '\\' + '\\' + '\n' 
        text+= 'Test\n'
        text+= '.emit to file "/tmp/RSLTestCase"' 
        
        self.eval_text(text)
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "Hello world\\\nTest\n")
    
    @evaluate_docstring
    def test_emit_comment(self, rc):
        '''.//Hello world
        .comment No comment
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate_docstring
    def test_emit_flush(self, rc):
        '''Hello world
        .emit to file "/tmp/RSLTestCase"
        .emit to file "/tmp/RSLTestCase"'''
        
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
        
    @evaluate_docstring
    def test_include_after_emit(self, rc):
        '''..exit 1
        .emit to file "/tmp/RSLTestCase"
        .include "/tmp/RSLTestCase"
        .exit 0
        '''
        self.assertEqual(1, rc)
            
    @evaluate_docstring
    def test_emit_after_clear(self, rc):
        '''
        Hello world
        .clear
        .emit to file "/tmp/RSLTestCase"
        '''
        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "")
    
    @evaluate_docstring
    def test_emit_from_function(self, rc):
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

    def test_supress_emit(self):
        self.runtime.emit = 'never'
        code = '''
        Test
        .emit to file "/tmp/RSLTestCase"
        '''
        path = "/tmp/RSLTestCase"
        if os.path.exists(path):
            os.remove(path)
        
        rc = self.eval_text(code, 'test_supress_emit')
        self.assertFalse(rc)
        
        self.assertFalse(os.path.exists(path))
        
    def test_emit_on_change(self):
        self.runtime.emit = 'change'
        code = '''
        Test
        .emit to file "/tmp/RSLTestCase"
        '''
        path = "/tmp/RSLTestCase"
        if os.path.exists(path):
            os.remove(path)
        
        rc = self.eval_text(code, 'test_emit_on_change')
        self.assertFalse(rc)
        self.assertTrue(os.path.exists(path))
        
        t = os.path.getmtime(path)
        time.sleep(0.05)
        self.eval_text('test' + code, 'test_emit_on_change')
        self.assertTrue(t < os.path.getmtime(path))
        
        t = os.path.getmtime(path)
        self.eval_text('test' + code, 'test_emit_on_change')
        self.assertEqual(t, os.path.getmtime(path))
        
    def test_parse_cp1252(self):
        rc = self.eval_text('.include "tests/test_files/cp1252.data"',
                            'test_parse_cp1252')
        self.assertIsNone(rc)

    def test_emit_cp1252(self):
        code = '''.include "tests/test_files/cp1252.data"
        .emit to file "/tmp/RSLTestCase"
        '''
        
        rc = self.eval_text(code, 'test_emit_cp1252')
        self.assertIsNone(rc)

        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "���\n")

    def test_parse_cp932(self):
        rc = self.eval_text('.include "tests/test_files/cp932.data"',
                            'test_parse_cp932')
        self.assertIsNone(rc)

    def test_emit_cp932(self):
        code = '''.include "tests/test_files/cp932.data"
        .emit to file "/tmp/RSLTestCase"
        '''
        
        rc = self.eval_text(code, 'test_emit_cp932')
        self.assertIsNone(rc)

        with open("/tmp/RSLTestCase") as f:
            self.assertEqual(f.read(), "���{��\n")
