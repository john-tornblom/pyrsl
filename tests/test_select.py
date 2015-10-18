# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import xtuml.model

from utils import RSLTestCase


class TestSelect(RSLTestCase):

    def testSelectAny_Empty(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select any a from instances of A
        .exit empty a
        '''
        
        rc = self.eval_text(text)
        self.assertTrue(rc)
        
        self.metamodel.new('A')
        
        rc = self.eval_text(text)
        self.assertFalse(rc)

    def testSelectAny_Not_Empty(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select any a from instances of A
        .exit not_empty a
        '''
        
        rc = self.eval_text(text)
        self.assertFalse(rc)
        
        self.metamodel.new('A')
        
        rc = self.eval_text(text)
        self.assertTrue(rc)
        
    def testSelectMany_Empty(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a from instances of A
        .exit empty a
        '''
        
        rc = self.eval_text(text)
        self.assertTrue(rc)
        
        self.metamodel.new('A')
        
        rc = self.eval_text(text)
        self.assertFalse(rc)
        
    def testSelectMany_Not_Empty(self):
        self.metamodel.define_class('A', [])
        
        text = '''
        .select many a from instances of A
        .exit not_empty a
        '''
        
        rc = self.eval_text(text)
        self.assertFalse(rc)
        
        self.metamodel.new('A')
                
        rc = self.eval_text(text)
        self.assertTrue(rc)
        
    def testSelectMany_Cardinality(self):
        self.metamodel.define_class('A', [])
        
        text = '''
        .select many a from instances of A
        .exit cardinality a
        '''
        
        for i in range(0, 10):
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
            self.metamodel.new('A')

    def testSelectWhenCreated(self):
        self.metamodel.define_class('A', [])

        text = '''
        .create object instance a of A
        .select any b from instances of A
        .exit empty b
        '''
        rc = self.eval_text(text)
        self.assertFalse(rc)

    def testSelectOneNavigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'), ('B_Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id')])
        a_endpint = xtuml.model.SingleAssociationLink('A')
        b_endpint = xtuml.model.SingleAssociationLink('B')
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B')
        xtuml.relate(a, b, 1)

        text = '''
        .select any a from instances of A
        .select one b related by a->B[R1]
        .exit b.Id
        '''
        rc = self.eval_text(text)
        self.assertEqual(b.Id, rc)

    def testSelectAnyNavigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id')])
        a_endpint = xtuml.model.SingleAssociationLink('A')
        b_endpint = xtuml.model.ManyAssociationLink('B')
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B')
        xtuml.relate(a, b, 1)
        
        text = '''
        .select any a from instances of A
        .select any b related by a->B[R1]
        .exit b.Id
        '''
        
        rc = self.eval_text(text)
        self.assertEqual(b.Id, rc)

    def testSelectManyNavigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id')])
        a_endpint = xtuml.model.SingleAssociationLink('A')
        b_endpint = xtuml.model.ManyAssociationLink('B')
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        xtuml.relate(a, self.metamodel.new('B'), 1)
        xtuml.relate(a, self.metamodel.new('B'), 1)
        xtuml.relate(a, self.metamodel.new('B'), 1)

        text = '''
        .select any a from instances of A
        .select many bs related by a->B[R1]
        .exit cardinality bs
        '''
        
        rc = self.eval_text(text)
        self.assertEqual(3, rc)

    def testSelectOneReflexiveNavigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'),
                                          ('Next_Id', 'unique_id'),
                                          ('Name', 'string')])
        
        endpint1 = xtuml.model.SingleAssociationLink('A', ids=['Id'], phrase='prev')
        endpint2 = xtuml.model.SingleAssociationLink('A', ids=['Next_Id'], phrase='next')
        self.metamodel.define_relation('R1', endpint1, endpint2)

        first = self.metamodel.new('A', Name="First")
        second = self.metamodel.new('A', Name="Second")
        xtuml.relate(first, second, 1, 'prev')
        
        text = '''
        .select any first_inst from instances of A where (selected.Name == "First")
        .select one second_inst related by first_inst->A[R1.'next']
        .exit second_inst.Name
        '''
        rc = self.eval_text(text)
        self.assertEqual(second.Name, rc)

        text = '''
        .select any second_inst from instances of A where (selected.Name == "Second")
        .select one first_inst related by second_inst->A[R1.'prev']
        .exit first_inst.Name
        '''
        rc = self.eval_text(text)
        self.assertEqual(first.Name, rc)
        
    
    def testSelectAnySubstituionNavigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id'), ('Name', 'string')])
        a_endpint = xtuml.model.SingleAssociationLink('A')
        b_endpint = xtuml.model.ManyAssociationLink('B')
        
        self.metamodel.define_relation('R1', a_endpint, b_endpint)
        
        a = self.metamodel.new('A')
        b = self.metamodel.new('B', Name='Test')
        xtuml.relate(a, b, 1)
        
        text = '''
        .select any a from instances of A where ("${selected->B[R1].name}" == "Test")
        .exit a.Id
        '''
        
        rc = self.eval_text(text)
        self.assertEqual(a.Id, rc)
        
        
    def testSelectWithManySpaces(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select       any        a       from          instances       of      A
        .select       many       a_set   from          instances       of      A
        '''
        
        self.eval_text(text)

