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

    def test_invoke_instref_with_kind(self):
        self.metamodel.define_class('My_Class1', [('Name', 'string')])
        self.metamodel.define_class('My_Class2', [('Name', 'string')])
        self.metamodel.new('My_Class1', Name='1')
        self.metamodel.new('My_Class2', Name='2')
        
        text = '''
            .function f
                .param inst_ref<My_Class1> inst
                .exit 1
            .end function
            .select any inst from instances of My_Class1
            .invoke res = f(inst)
            .exit 0
        '''
        rc = self.eval_text(text)
        self.assertEqual(rc, 1)
        
    def test_invoke_instref_with_wrong_kind(self):
        self.metamodel.define_class('My_Class1', [('Name', 'string')])
        self.metamodel.define_class('My_Class2', [('Name', 'string')])
        self.metamodel.new('My_Class1', Name='1')
        self.metamodel.new('My_Class2', Name='2')
        
        text = '''
            .function f
                .param inst_ref<My_Class2> inst
                .exit 1
            .end function
            .select any inst from instances of My_Class1
            .invoke res = f(inst)
            .exit 0
        '''
        rc = self.eval_text(text)
        self.assertIsInstance(rc, RuntimeException)
        
    def test_invoke_instrefset_with_kind(self):
        self.metamodel.define_class('My_Class1', [('Name', 'string')])
        self.metamodel.define_class('My_Class2', [('Name', 'string')])
        self.metamodel.new('My_Class1', Name='1')
        self.metamodel.new('My_Class2', Name='2')
        
        text = '''
            .function f
                .param inst_ref_set<My_Class1> insts
                .exit 1
            .end function
            .select many insts from instances of My_Class1
            .invoke res = f(insts)
            .exit 0
        '''
        rc = self.eval_text(text)
        self.assertEqual(rc, 1)
        
    def test_invoke_instrefset_with_wrong_kind(self):
        self.metamodel.define_class('My_Class1', [('Name', 'string')])
        self.metamodel.define_class('My_Class2', [('Name', 'string')])
        self.metamodel.new('My_Class1', Name='1')
        self.metamodel.new('My_Class2', Name='2')
        
        text = '''
            .function f
                .param inst_ref_set<My_Class2> insts
                .exit 1
            .end function
            .select many insts from instances of My_Class1
            .invoke res = f(insts)
            .exit 0
        '''
        rc = self.eval_text(text)
        self.assertIsInstance(rc, RuntimeException)
        
        
        
        
