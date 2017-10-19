# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate_docstring

from rsl.runtime import RuntimeException


class TestInvoke(RSLTestCase):

    @evaluate_docstring
    def test_invoke_empty_function(self, rc):
        '''
        .function f
        .end function
        .invoke f()
        .exit 1
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_invoke_dot_named_function(self, rc):
        '''
        .function module.f
        .exit 1
        .end function
        .invoke module.f()
        .exit 0
        '''
        self.assertEqual(1, rc)
    
    @evaluate_docstring
    def test_invoke_with_exit(self, rc):
        '''
        .function f
            .exit 1
        .end function
        .invoke f()
        .exit 0
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_invoke_with_parameter(self, rc):
        '''
        .function f
            .param integer x
            .exit x + 1
        .end function
        .invoke f(1)
        .exit 0
        '''
        self.assertEqual(2, rc)


    @evaluate_docstring
    def test_parameter_named_from(self, rc):
        '''
        .function f
            .param string from
            .assign from = "f"
            .exit "${from}"
        .end function
        .invoke f("from")
        .exit 0
        '''
        self.assertEqual("f", rc)

    @evaluate_docstring
    def test_parameter_named_cardinality(self, rc):
        '''
        .function f
            .param integer cardinality
            .assign cardinality = (cardinality cardinality)
            .exit "${cardinality}"
        .end function
        .invoke f(3)
        .exit 0
        '''
        self.assertEqual('0', rc)
        
    @evaluate_docstring
    def test_invoke_with_parameter_and_comments(self, rc):
        '''
        .function f .// integer
            .param integer x .// some comment
            .// begin body
            .exit x + 1
        .end function
        .invoke f(1)
        .exit 0
        '''
        self.assertEqual(2, rc)
        
    @evaluate_docstring
    def test_parameter_order(self, rc):
        '''
        .function f
            .param integer x
            .param integer y
            .param integer z
            .exit x
        .end function
        .invoke f(1, 2, 3)
        .exit 0
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_missing_parameter(self, rc):
        '''
        .function f
            .param integer x
            .param integer y
            .param integer z
            .exit x
        .end function
        .invoke f(1)
        .exit 0
        '''
        self.assertIsInstance(rc, RuntimeException)

    @evaluate_docstring
    def test_superfluous_argument(self, rc):
        '''
        .function f
            .param integer x
            .param integer y
            .param integer z
            .exit x
        .end function
        .invoke f(1,2,3,4)
        .exit 0
        '''
        self.assertIsInstance(rc, RuntimeException)
        
    @evaluate_docstring
    def test_invoke_with_return_value(self, rc):
        '''
        .function f
            .assign attr_value = 1
        .end function
        .invoke res = f()
        .exit res.value
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_invoke_dot_named_function_with_return_value(self, rc):
        '''
        .function module.f
            .assign attr_value = 1
        .end function
        .invoke res = module.f()
        .exit res.value
        '''
        self.assertEqual(1, rc)

    @evaluate_docstring
    def test_invoke_with_return_values(self, rc):
        '''
        .function f
            .assign attr_x = 1
            .assign attr_y = 2
        .end function
        .invoke res = f()
        .if (res.x != 1)
            .exit 1
        .end if
        .if (res.y != 2)
            .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_invoke_from_other_body(self, rc):
        '''
        ..function f
            ..assign attr_x = 1
            ..assign attr_y = 2
        ..end function
        .emit to file "/tmp/RSLTestCase"
        .include "/tmp/RSLTestCase"
        .invoke res = f()
        .if (res.x != 1)
            .exit 1
        .end if
        .if (res.y != 2)
            .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(0, rc)

    @evaluate_docstring
    def test_invoke_undefined_function(self, rc):
        '''
        .invoke res = f()
        .exit 0
        '''
        self.assertIsInstance(rc, RuntimeException)
        
