# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestBinaryOperation(RSLTestCase):

    def setUp(self):
        RSLTestCase.setUp(self)
        self.metamodel.define_class('A', [('Name', 'string')])
        
    @evaluate_docstring
    def test_plus(self, rc):
        '.exit 1 + 1'
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_minus(self, rc):
        '.exit 1 - 1'
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_minus_with_unary_minus(self, rc):
        '.exit 1 - -1'
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_multiplication(self, rc):
        '.exit 2 * 2'
        self.assertEqual(4, rc)
        
    @evaluate_docstring
    def test_division(self, rc):
        '.exit 10 / 2'
        self.assertEqual(5, rc)
        
    @evaluate_docstring
    def test_less_true(self, rc):
        '.exit 0 < 1'
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_less_false(self, rc):
        '.exit 0 < 0'
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_less_equal_true(self, rc):
        '.exit 1 <= 1'
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_less_equal_false(self, rc):
        '.exit 2 <= 1'
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_not_equal_false(self, rc):
        '.exit 1 != 1'
        self.assertFalse(rc)
    
    @evaluate_docstring
    def test_great_equal_false(self, rc):
        '.exit 1 >= 2'
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_great_equal_true(self, rc):
        '.exit 3 >= 2'
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_not_equal_true(self, rc):
        '.exit 0 != 1'
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_equal_false(self, rc):
        '.exit 0 == 1'
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_equal_true(self, rc):
        '.exit 1 == 1'
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_grouped(self, rc):
        '''
        .assign x = (1 + 1)
        .exit x
        '''
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_chained(self, rc):
        '''
        .assign x = (1 + 1) + 1
        .exit x
        '''
        self.assertEqual(3, rc)

    @evaluate_docstring
    def test_chained_with_unary(self, rc):
        '''
        .assign x = not (1 == 1)
        .exit x
        '''
        self.assertEqual(False, rc)

    @evaluate_docstring
    def test_and_true(self, rc):
        '''
        .exit True and True
        '''
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_and_false(self, rc):
        '''
        .exit True and False
        '''
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_or_true(self, rc):
        '''
        .exit True or False
        '''
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_or_false(self, rc):
        '''
        .exit False or False
        '''
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_or_without_spaces(self, rc):
        '''
        .assign x = (True)or(False)
        .exit x
        '''
        self.assertTrue(rc)
        
    @evaluate_docstring
    def test_and_without_spaces(self, rc):
        '''
        .assign x = (True)AND(True)
        .exit x
        '''
        self.assertTrue(rc)

    @evaluate_docstring
    def test_procent(self, rc):
        '''
        .assign x = 5 % 3
        .exit x
        '''
        self.assertEqual(rc, 2)

    @evaluate_docstring
    def test_pipe_with_instances(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a_set = a1 | a2
        .exit cardinality a_set
        '''
        self.assertEqual(2, rc)

    @evaluate_docstring
    def test_pipe_with_instance_and_set(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .create object instance a3 of A
        .select many a_set from instances of A
        
        .assign a_set = a1 | a_set
        .exit cardinality a_set
        '''
        self.assertEqual(3, rc)

    @evaluate_docstring
    def test_caret(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .create object instance a3 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        .assign a3.Name = "A3"
        
        .select many a23_set from instances of A where (selected.Name != "A1")
        .select many a13_set from instances of A where (selected.Name != "A2")
        
        .assign a_set = a23_set ^ a13_set
        .exit cardinality a_set .// should not contain a3
        '''
        self.assertEqual(2, rc)

    @evaluate_docstring
    def test_ampesand_with_instances(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a_set = a1 & a2
        .exit cardinality a_set
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_ampesand_with_sets(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .create object instance a3 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        .assign a3.Name = "A3"

        .select many not_a1_set from instances of A where (selected.Name != "A1")
        .select many not_a2_set from instances of A where (selected.Name != "A2")

        .assign a3_set = not_a1_set & not_a2_set
        .exit cardinality a3_set
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_instance_plus_instance(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        
        .assign a_set = a1 + a2
        .exit cardinality a_set
        '''
        self.assertEqual(2, rc)

    @evaluate_docstring
    def test_instance_minus_instance(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        
        .assign a_set = a1 - a2
        .exit cardinality a_set
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_instance_minus_same_instance(self, rc):
        '''
        .create object instance a1 of A
        .assign a1.Name = "A1"
        
        .assign a_set = a1 - a1
        .exit cardinality a_set
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_short_circuit_or(self, rc):
        '''
        .create object instance a1 of A
        .assign a1.Name = "A1"

        .select any a2 from instances of A where ( false )
        .assign cond = ( ( empty a2 ) or ( a2.Name == "a2" ) )
        .exit cond
        '''
        self.assertEqual(True, rc)

    @evaluate_docstring
    def test_short_circuit_and(self, rc):
        '''
        .create object instance a1 of A
        .assign a1.Name = "A1"

        .select any a2 from instances of A where ( false )
        .assign cond = ( ( not_empty a2 ) and ( a2.Name == "a2" ) )
        .exit cond
        '''
        self.assertEqual(False, rc)

    @evaluate_docstring
    def test_instance_set_minus_instance_set(self, rc):
        '''
        .create object instance a1 of A
        .create object instance a2 of A
        .assign a1.Name = "A1"
        .assign a2.Name = "A2"
        .select many an_set from instances of A
        .select many a0_set from instances of A where (false)

        .if ((cardinality (an_set - a0_set)) != 2)
          .exit 1
        .end if

        .if ((cardinality (a0_set - an_set)) != 0)
          .exit 2
        .end if

        .if ((cardinality (an_set - a1)) != 1)
          .exit 3
        .end if

        .if ((cardinality (a1 - an_set)) != 0)
          .exit 4
        .end if

        .if ((cardinality (a0_set - a1)) != 0)
          .exit 5
        .end if

        .if ((cardinality (a1 - a0_set)) != 1)
          .exit 6
        .end if

        .exit 0
        '''
        self.assertEqual(0, rc)

