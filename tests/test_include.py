# encoding: utf-8
# Copyright (C) 2015 Per Jonsson

import datetime
import os

from utils import RSLTestCase
from utils import evaluate
from utils import expect_exception

import rsl.version


class TestInclude(RSLTestCase):

    @evaluate
    def testReinclude(self, rc):
        '''
        ..assign attr_x = 1
        .emit to file "/tmp/RSLTestCase"
        .function f
          .include "/tmp/RSLTestCase"
        .end function
        .invoke res = f()
        .clear
        .assign attr_x = 2
        .emit to file "/tmp/RSLTestCase"
        .function g
          .include "/tmp/RSLTestCase"
        .end function
        .invoke res2 = g()
        .if (res.x != res2.x)
          .exit 1
        .end if
        .exit 0
        '''
        self.assertEqual(0, rc)

    @evaluate
    def testRelativeInclude(self, rc):
        '''
        .include "tests/test_files/foo.rsl"
        '''
        self.assertEqual(4711, rc)

    @evaluate
    def testInvalidfile(self, rc):
        '''
        .include "tests/test_files/nonexisting_file"
        '''
        self.assertIsInstance(rc, Exception)

