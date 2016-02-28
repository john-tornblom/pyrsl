# encoding: utf-8
# Copyright (C) 2016 John Törnblom

import xtuml

from utils import RSLTestCase


class TestRelate(RSLTestCase):

    def test_relate(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'), ('B_Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id')])
        a_endpint = xtuml.SingleAssociationLink('A', ids=['B_Id'])
        b_endpint = xtuml.SingleAssociationLink('B', ids=['Id'])
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        text = '''
        .create object instance a of A
        .create object instance b of B
        .relate a to b across R1
        '''
        self.eval_text(text)

        a = self.metamodel.select_any('A')
        b = xtuml.navigate_one(a).B[1]()
        self.assertTrue(b)

    def test_unrelate(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'), ('B_Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id')])
        a_endpint = xtuml.SingleAssociationLink('A', ids=['B_Id'])
        b_endpint = xtuml.SingleAssociationLink('B', ids=['Id'])
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B')
        xtuml.relate(a, b, 1)

        text = '''
        .select any a from instances of A
        .select any b from instances of B
        .print "${a}"
        .print "${b}"
        .unrelate a from b across R1
        '''
        self.eval_text(text)
        
        a = self.metamodel.select_any('A')
        b = xtuml.navigate_one(a).B[1]()
        self.assertFalse(b)
        
    def test_relate_reflexive(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'),
                                          ('Next_Id', 'unique_id'),
                                          ('Name', 'string')])
        
        endpint1 = xtuml.SingleAssociationLink('A', ids=['Id'], phrase='prev')
        endpint2 = xtuml.SingleAssociationLink('A', ids=['Next_Id'], phrase='next')
        self.metamodel.define_relation('R1', endpint1, endpint2)
        
        text = '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "First"
        .assign a2.Name = "Second"
        .relate a2 to a1 across R1.'next'
        '''
        
        self.eval_text(text)
        a1 = self.metamodel.select_any('A', lambda sel: sel.Name == "First")
        a2 = xtuml.navigate_one(a1).A[1, 'next']()
        self.assertTrue(a2)
        self.assertEqual(a2.Name, 'Second')

    def test_unrelate_reflexive(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'),
                                          ('Next_Id', 'unique_id'),
                                          ('Name', 'string')])
        
        endpint1 = xtuml.SingleAssociationLink('A', ids=['Id'], phrase='prev')
        endpint2 = xtuml.SingleAssociationLink('A', ids=['Next_Id'], phrase='next')
        self.metamodel.define_relation('R1', endpint1, endpint2)

        first = self.metamodel.new('A', Name="First")
        second = self.metamodel.new('A', Name="Second")
        xtuml.relate(first, second, 1, 'prev')
        
        text = '''
        .select any first_inst from instances of A where (selected.Name == "First")
        .select one second_inst related by first_inst->A[R1.'next']
        .unrelate first_inst from second_inst across R1.'prev'
        '''
        
        self.eval_text(text)
        a1 = self.metamodel.select_any('A', lambda sel: sel.Name == "First")
        a2 = xtuml.navigate_one(a1).A[1, 'next']()
        self.assertFalse(a2)

