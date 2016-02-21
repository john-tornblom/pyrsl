# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import os

from utils import RSLTestCase
from utils import evaluate_docstring

from rsl.runtime import RuntimeException


class TestIntrinsic(RSLTestCase):

    @evaluate_docstring
    def test_get_env_var(self, rc):
        '''
        .invoke rc = GET_ENV_VAR("PATH")
        .exit rc.result
        '''
        self.assertEqual(os.environ['PATH'], rc)

    @evaluate_docstring
    def test_get_env_var_failure(self, rc):
        '''
        .invoke rc = GET_ENV_VAR("UNKNOWN_PATH")
        .exit rc.success
        '''
        self.assertFalse(rc)

    @evaluate_docstring
    def test_put_env_var(self, rc):
        '''
        .invoke rc = PUT_ENV_VAR("MY_PATH", "test")
        .exit rc.success
        '''
        self.assertTrue(rc)
        self.assertEqual(os.environ["MY_PATH"], "test")
    
    @evaluate_docstring
    def test_file_read_write(self, rc):
        '''
        .invoke rc = FILE_WRITE("/tmp/RSLTestCase", "Hello world!")
        .if ( not rc.success )
            .exit ""
        .end if
        .invoke rc = FILE_READ("/tmp/RSLTestCase")
        .if ( not rc.success )
            .exit ""
        .end if
        .exit rc.result
        '''
        self.assertEqual(rc, "Hello world!\n")
    
    @evaluate_docstring
    def test_file_read_error(self, rc):
        '''
        .invoke rc = FILE_READ("/")
        .exit rc.success
        '''
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_file_write_error(self, rc):
        '''
        .invoke rc = FILE_WRITE("/", "TEST")
        .exit rc.success
        '''
        self.assertFalse(rc)
        
    @evaluate_docstring
    def test_shell_command_exit_0(self, rc):
        '''
        .invoke rc = SHELL_COMMAND("exit 0")
        .exit rc.result
        '''
        self.assertEqual(0, rc)
    
    @evaluate_docstring
    def test_shell_command_exit_1(self, rc):
        '''
        .invoke rc = SHELL_COMMAND("exit 1")
        .exit rc.result
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_integer_to_string(self, rc):
        '''
        .invoke rc = INTEGER_TO_STRING(1)
        .exit rc.result
        '''
        self.assertEqual("1", rc)
        
    @evaluate_docstring
    def test_real_to_string(self, rc):
        '''
        .invoke rc = REAL_TO_STRING(1.1)
        .exit rc.result
        '''
        self.assertEqual("1.1", rc)
    
    @evaluate_docstring
    def test_boolean_to_string(self, rc):
        '''
        .invoke rc = BOOLEAN_TO_STRING(False)
        .exit rc.result
        '''
        self.assertEqual("FALSE", rc)
    
    @evaluate_docstring
    def test_string_to_integer(self, rc):
        '''
        .invoke rc = STRING_TO_INTEGER("1")
        .exit rc.result
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_string_to_integer_invalid(self, rc):
        '''
        .invoke rc = STRING_TO_INTEGER("test")
        '''
        self.assertIsInstance(rc, RuntimeException)
        
    @evaluate_docstring
    def test_string_to_integer_with_spaces(self, rc):
        '''
        .invoke rc = STRING_TO_INTEGER(" 1 ")
        .exit rc.result
        '''
        self.assertEqual(1, rc)
        
    @evaluate_docstring
    def test_string_to_real(self, rc):
        '''
        .invoke rc = STRING_TO_REAL("1.1")
        .exit rc.result
        '''
        self.assertEqual(1.1, rc)
    
    @evaluate_docstring
    def test_string_to_real_invalid(self, rc):
        '''
        .invoke rc = STRING_TO_REAL("test")
        '''
        self.assertIsInstance(rc, RuntimeException)
        
    @evaluate_docstring
    def test_string_to_real_with_spaces(self, rc):
        '''
        .invoke rc = STRING_TO_REAL(" 1.1 ")
        .exit rc.result
        '''
        self.assertEqual(1.1, rc)

