# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import datetime
import os

from utils import RSLTestCase
from utils import evaluate_docstring

import rsl.version


class TestInfo(RSLTestCase):

    @evaluate_docstring
    def test_date(self, rc):
        '.exit "${info.date}"'
        now = datetime.datetime.now()
        now = datetime.datetime.ctime(now)
        now = str(now)
        self.assertEqual(now, rc)

    @evaluate_docstring
    def test_user_id(self, rc):
        '.exit "${info.user_id}"'
        self.assertEqual(os.getlogin(), rc)

    @evaluate_docstring
    def test_uuid(self, rc):
        '.exit "${info.unique_num}"'
        self.assertEqual("1", rc)
        
    @evaluate_docstring
    def test_arch_file_name(self, rc):
        '.exit "${info.arch_file_name}"'
        self.assertEqual("test_info.test_arch_file_name", rc)
        
    @evaluate_docstring
    def test_arch_file_line(self, rc):
        '''
        .// No comment
        .exit "${info.arch_file_line}"
        '''
        self.assertEqual("3", rc)

    @evaluate_docstring
    def test_version(self, rc):
        '.exit "${info.interpreter_version}"'
        self.assertEqual(rsl.version.complete_string, rc)

    @evaluate_docstring
    def test_platform(self, rc):
        '.exit "${info.interpreter_platform}"'
        self.assertEqual(os.name, rc)
        


