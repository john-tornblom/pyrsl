# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring


class TestLoop(RSLTestCase):

    @evaluate_docstring
    def test_while_loop(self, rc):
        '''
        .assign x = 10
        .while (x > 0)
            .assign x = x - 1
        .end while
        .exit x
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_while_loop_with_simple_end(self, rc):
        '''
        .assign x = 10
        .while (x > 0)
            .assign x = x - 1
        .end
        .exit x
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_while_loop_break(self, rc):
        '''
        .assign x = 10
        .while (x > 0)
            .if (x == 5)
                .break while
            .end if
            .assign x = x - 1
        .end while
        .exit x
        '''
        self.assertEqual(5, rc)
        
    def test_for_loop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .assign x = x + 1
        .end for
        .exit x
        '''
        
        for i in range(0, 10):
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
            self.metamodel.new('A')

    def test_for_loop_with_simple_end(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .assign x = x + 1
        .end
        .exit x
        '''
        for i in range(0, 10):
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
            self.metamodel.new('A')
            
    def test_for_loop_break(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (x == 3)
                .break for
            .end if
            .assign x = x + 1
        .end for
        .exit x
        '''

        for _ in range(0, 10):
            self.metamodel.new('A')
            
        rc = self.eval_text(text)
        self.assertEqual(3, rc)

    def test_first_in_loop_count(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (first a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(1, rc)

    def test_not_first_in_loop_count(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (not_first a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for i in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
        
    def test_last_in_loop_count(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (last a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(1, rc)
        
    def test_not_last_in_loop_count(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign x = 0
        .for each a in a_set
            .if (not_last a_set)
                .assign x = x + 1
            .end if
        .end for
        .exit x
        '''
        
        for i in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(i, rc)
    
    def test_first_in_loop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign loop_count = 0
        .for each a in a_set
            .if (first a_set)
                .exit loop_count
            .end if
            .assign loop_count = (loop_count + 1)
        .end for
        .exit -1
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(0, rc)
        
    def test_not_first_is_second_in_loop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign loop_count = 0
        .for each a in a_set
            .if (not_first a_set)
                .exit loop_count
            .end if
            .assign loop_count = (loop_count + 1)
        .end for
        .exit loop_count
        '''
        
        for _ in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(1, rc)
        
    def test_last_in_loop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign loop_count = 0
        .for each a in a_set
            .if (last a_set)
                .exit loop_count
            .end if
            .assign loop_count = (loop_count + 1)
        .end for
        .exit -1
        '''
        
        for i in range(0, 10):
            self.metamodel.new('A')
            rc = self.eval_text(text)
            self.assertEqual(i, rc)

    def test_first_element_is_not_last_in_loop(self):
        self.metamodel.define_class('A', [])

        text = '''
        .select many a_set from instances of A
        .assign loop_count = 0
        .for each a in a_set
            .if (not_last a_set)
                .exit loop_count
            .end if
            .assign loop_count = (loop_count + 1)
        .end for
        .exit -1
        '''
        
        for _ in range(0, 5):
            self.metamodel.new('A')
        
        rc = self.eval_text(text)
        self.assertEqual(0, rc)
            
    def test_shadowing_selected(self):
        self.metamodel.define_class('A', [('ID', 'integer')])
        self.metamodel.define_class('B', [('ID', 'integer')])
        
        text = '''
        .select many a_set from instances of A
        .for each a in a_set
          .select many b_set from instances of B where (selected.ID > 5)
          .assign x = 0
          .assign y = 0
          .for each b in b_set
            .assign x = (x + (first b_set))
            .assign y = (y + (first a_set))
          .end for
          .exit "${x} ${y}"
        .end for
        .exit 1
        '''

        self.metamodel.new('A', ID=1);
        self.metamodel.new('A', ID=2);
        self.metamodel.new('A', ID=3);
        
        self.metamodel.new('B', ID=6);
        self.metamodel.new('B', ID=7);
        self.metamodel.new('B', ID=8);

        rc = self.eval_text(text)
        self.assertEqual("1 3", rc)
        
