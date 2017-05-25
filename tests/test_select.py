# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import xtuml

from utils import RSLTestCase


class TestSelect(RSLTestCase):

    def test_select_any_empty(self):
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

    def test_select_any_not_empty(self):
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
        
    def test_select_many_empty(self):
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
        
    def test_select_many_not_empty(self):
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
        
    def test_select_many_cardinality(self):
        self.metamodel.define_class('A', [])
        
        text = '''
        .select many a from instances of A
        .exit cardinality a
        '''
        
        for i in range(0, 10):
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
            self.metamodel.new('A')

    def test_select_when_created(self):
        self.metamodel.define_class('A', [])

        text = '''
        .create object instance a of A
        .select any b from instances of A
        .exit empty b
        '''
        rc = self.eval_text(text)
        self.assertFalse(rc)

    def test_select_one_navigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), ('A_Id', 'unique_id')])
        
        self.metamodel.define_association(rel_id='R1',
                                          source_kind='A',
                                          target_kind='B',
                                          source_keys=['Id'],
                                          target_keys=['A_Id'],
                                          source_many=False,
                                          target_many=False,
                                          source_conditional=True,
                                          target_conditional=True,
                                          source_phrase='',
                                          target_phrase='')
        
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

    def test_select_any_navigation(self):
        '''
        |===================|                |======================|  
        |         A         |                |         B            |
        |-------------------| 1           *  |----------------------|
        | Id: unique_id {I} | -------------- | Id: unique_id    {I} |
        |===================|       R1       | A_Id: unique_id {R1} |
                                             |======================|
        '''
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), 
                                          ('A_Id', 'unique_id')])
        
        self.metamodel.define_association(rel_id='R1',
                                          source_kind='B',
                                          target_kind='A',
                                          source_keys=['A_Id'],
                                          target_keys=['Id'],
                                          source_many=True,
                                          target_many=False,
                                          source_conditional=True,
                                          target_conditional=False,
                                          source_phrase='',
                                          target_phrase='')
        
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

    def test_select_many_navigation(self):
        '''
        |===================|                |======================|  
        |         A         |                |         B            |
        |-------------------| 1           *  |----------------------|
        | Id: unique_id {I} | -------------- | Id: unique_id    {I} |
        |===================|       R1       | A_Id: unique_id {R1} |
                                             |======================|
        '''
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), 
                                          ('A_Id', 'unique_id')])
        
        self.metamodel.define_association(rel_id='R1',
                                          source_kind='B',
                                          target_kind='A',
                                          source_keys=['A_Id'],
                                          target_keys=['Id'],
                                          source_many=True,
                                          target_many=False,
                                          source_conditional=True,
                                          target_conditional=False,
                                          source_phrase='',
                                          target_phrase='')
        
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

    def test_select_one_reflexive_navigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id'),
                                          ('Next_Id', 'unique_id'),
                                          ('Name', 'string')])
        
        self.metamodel.define_association(rel_id='R1',
                                          source_kind='A',
                                          target_kind='A',
                                          source_keys=['Id'],
                                          target_keys=['Next_Id'],
                                          source_many=False,
                                          target_many=False,
                                          source_conditional=True,
                                          target_conditional=True,
                                          source_phrase='prev',
                                          target_phrase='next')

        first = self.metamodel.new('A', Name="First")
        second = self.metamodel.new('A', Name="Second")
        xtuml.relate(first, second, 1, 'prev')
        
        text = '''
        .select any first_inst from instances of A where (selected.Name == "First")
        .select one second_inst related by first_inst->A[R1.'prev']
        .exit second_inst.Name
        '''
        rc = self.eval_text(text)
        self.assertEqual(second.Name, rc)

        text = '''
        .select any second_inst from instances of A where (selected.Name == "Second")
        .select one first_inst related by second_inst->A[R1.'next']
        .exit first_inst.Name
        '''
        rc = self.eval_text(text)
        self.assertEqual(first.Name, rc)
        
    def test_select_any_substitution_navigation(self):
        self.metamodel.define_class('A', [('Id', 'unique_id')])
        self.metamodel.define_class('B', [('Id', 'unique_id'), 
                                          ('A_Id', 'unique_id'), 
                                          ('Name', 'string')])
        
        self.metamodel.define_association(rel_id='R1',
                                          source_kind='A',
                                          target_kind='B',
                                          source_keys=[],
                                          target_keys=[],
                                          source_many=False,
                                          target_many=True,
                                          source_conditional=True,
                                          target_conditional=True,
                                          source_phrase='',
                                          target_phrase='')

        a = self.metamodel.new('A')
        b = self.metamodel.new('B', Name='Test')
        xtuml.relate(a, b, 1)
        
        text = '''
        .select any a from instances of A where ("${selected->B[R1].name}" == "Test")
        .exit a.Id
        '''
        
        rc = self.eval_text(text)
        self.assertEqual(a.Id, rc)
        
    def test_select_with_many_spaces(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select       any        a       from          instances       of      A
        .select       many       a_set   from          instances       of      A
        '''
        
        self.eval_text(text)

    def test_select_with_type_name(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select any string from instances of A
        '''
        
        self.eval_text(text)
        
