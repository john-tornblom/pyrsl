# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase

from rsl.runtime import RuntimeException


class TestTypeSystem(RSLTestCase):

    def test_invoke_parameter(self):

        def f(ty, val):
            return self.eval_text('''
                .function f
                    .param %s x
                .end function
                .invoke f(%s)
                .exit true''' % (ty, val), 'TestTypeSys.test_invoke_parameter(%s, %s)' % (ty, val))
        
        self.assertTrue(f('boolean', 'true'))
        self.assertTrue(f('boolean', 'false'))
        self.assertTrue(f('integer', '1'))
        self.assertTrue(f('integer', '-1'))
        self.assertTrue(f('string', '""'))
        self.assertTrue(f('string', '"Hello"'))
        self.assertTrue(f('real', '0.0'))
        self.assertTrue(f('real', '-0.1'))
        self.assertTrue(f('real', '1'))
        
        self.assertIsInstance(f('boolean', '1'), RuntimeException)
        self.assertIsInstance(f('integer', '1.1'), RuntimeException)
        self.assertIsInstance(f('string', 'true'), RuntimeException)
        self.assertIsInstance(f('frag_ref', '0'), RuntimeException)

    def test_invoke_fragment_parameter(self):

        def f(ty):
            return self.eval_text('''
                .function g
                    .assign attr_result = True
                .end function
                .function f
                    .param %s x
                .end function
                .invoke value = g()
                .invoke f(value)
                .exit true''' % ty, 
                'TestTypeSys.test_invoke_fragment_parameter(%s)' % ty)
        
        self.assertTrue(f('frag_ref'))
        
        self.assertIsInstance(f('boolean'), RuntimeException)
        self.assertIsInstance(f('integer'), RuntimeException)
        self.assertIsInstance(f('real'), RuntimeException)
        self.assertIsInstance(f('string'), RuntimeException)
