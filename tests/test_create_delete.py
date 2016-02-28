# encoding: utf-8
# Copyright (C) 2016 John Törnblom


from xtuml import where_eq as where

from utils import RSLTestCase

class TestCreateDelete(RSLTestCase):

    def test_not_first_in_loop(self):
        self.metamodel.define_class('A', [('Name', 'string')])

        self.assertEqual(len(self.metamodel.select_many('A')), 0)
        self.eval_text('.create object instance a of A')
        self.assertEqual(len(self.metamodel.select_many('A')), 1)
        
        self.metamodel.new('A', Name='1')
        self.metamodel.new('A', Name='2')
        self.metamodel.new('A', Name='3')
        self.metamodel.new('A', Name='4')
        
        tmpl = '''
        .select any a from instances of A where (selected.Name == "%s")
        .delete object instance a
        '''
        
        self.eval_text(tmpl % '2')
        
        self.assertTrue(self.metamodel.select_any('A', where(Name='1')))
        self.assertFalse(self.metamodel.select_any('A', where(Name='2')))
        self.assertTrue(self.metamodel.select_any('A', where(Name='3')))
        self.assertTrue(self.metamodel.select_any('A', where(Name='4')))
        
        self.eval_text(tmpl % '4')
        
        self.assertTrue(self.metamodel.select_any('A', where(Name='1')))
        self.assertFalse(self.metamodel.select_any('A', where(Name='2')))
        self.assertTrue(self.metamodel.select_any('A', where(Name='3')))
        self.assertFalse(self.metamodel.select_any('A', where(Name='4')))
        
        self.eval_text(tmpl % '1')
        
        self.assertFalse(self.metamodel.select_any('A', where(Name='1')))
        self.assertFalse(self.metamodel.select_any('A', where(Name='2')))
        self.assertTrue(self.metamodel.select_any('A', where(Name='3')))
        self.assertFalse(self.metamodel.select_any('A', where(Name='4')))
        
        