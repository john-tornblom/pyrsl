# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import unittest
import tempfile
import sys
import os
import logging

try:
    # python2
    from StringIO import StringIO
except ImportError:
    # python3
    from io import StringIO
    
import rsl


class TestCommandLineInterface(unittest.TestCase):
    
    def setUp(self):
        self.temp_files = set()
        logger = logging.getLogger()
        self.log = logging.StreamHandler(StringIO())
        logger.addHandler(self.log)
        
    def tearDown(self):
        logger = logging.getLogger()
        logger.removeHandler(self.log)
        
        for temp in self.temp_files:
            temp.close()
            os.remove(temp.name)

    def temp_file(self, mode='w'):
        temp = tempfile.NamedTemporaryFile(mode=mode, delete=False)
        self.temp_files.add(temp)
        return temp
    
    def test_unsed_arguments(self):
        argv = ['test_unsed_arguments', 
                '-nopersist', #don't save database to disk during testing
                '-d', '1',
                '-priority', '32',
                '-lVHs', '-lSCs', '-l2b', '-l2s', '-l3b', '-l3s',
                '-e', 'some_string',
                '-t', 'some_string',
                '-v', 'STMT',
                '-q',
                '-l',
                '-#', '4']
        rsl.main(argv)

    def test_ignoring_arguments(self):
        argv = ['test_ignoring_arguments', 
                '-nopersist', #don't save database to disk during testing
                '-ignore_rest', 'some', 'more']
        rsl.main(argv)

    def test_invalid_arguments(self):
        argv = ['test_invalid_arguments', 
                'some', 'more']
        self.assertRaises(SystemExit, rsl.main, argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn('ERROR', output)
    
    def test_help(self):
        argv = ['test_help', 
                '-h']
        
        self.assertRaises(SystemExit, rsl.main, argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn('USAGE', output)
    
    def test_version(self):
        argv = ['test_version', 
                '-version']
        
        self.assertRaises(SystemExit, rsl.main, argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn(rsl.version.complete_string, output)
        
    def test_integrity(self):
        schema = self.temp_file(mode='w')
        script = self.temp_file(mode='w')
        
        schema.file.write('CREATE TABLE Cls (Id STRING);')
        schema.file.write('CREATE UNIQUE INDEX I1 ON Cls (Id);')
        schema.file.flush()
        
        script.file.write('.create object instance cls of Cls\n')
        script.file.write('.assign cls.Id = "test"\n')
        
        argv = ['test_integrity', 
                '-nopersist',
                '-integrity',
                '-import', schema.name,
                '-arch', script.name]
        
        self.assertEqual(0, rsl.main(argv))
    
        # expect two uniqueness constrain violations
        script.file.write('.create object instance cls of Cls\n')
        script.file.write('.assign cls.Id = "test"\n')
        script.file.flush()
        self.assertEqual(1, rsl.main(argv))
    
    def test_qim(self):
        schema = self.temp_file(mode='w')
        modeldata = self.temp_file(mode='w')
        script = self.temp_file(mode='w')
        
        schema.file.write('CREATE TABLE Cls (Id STRING, OtherAttr INTEGER);')
        schema.file.write('CREATE UNIQUE INDEX I1 ON Cls (Id);')
        schema.file.flush()
        
        modeldata.file.write('INSERT INTO Cls VALUES ("myid");')
        modeldata.file.flush()
        
        script.file.write('')
        script.file.flush()
        
        argv = ['test_qim', 
                '-nopersist',
                '-import', schema.name,
                '-import', modeldata.name,
                '-arch', script.name]
        rsl.main(argv)
        
        argv = ['test_qim', 
                '-nopersist',
                '-qim',
                '-import', schema.name,
                '-import', modeldata.name,
                '-arch', script.name]
        rsl.main(argv)

        mismatches = self.log.stream.getvalue().count('mismatch')
        self.assertEqual(1, mismatches)
        
    def test_include(self):
        script = self.temp_file(mode='w')
        script.file.write('.print "Hello"\n')
        script.file.write('.include "spam.inc"\n')
        script.file.flush()
        
        argv = ['test_include', 
                '-arch', script.name,
                '-include', 
                os.path.dirname(__file__) + os.path.sep + 'test_files',
                '-nopersist']
        
        rsl.main(argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn('Hello', output)

    def test_nopersist(self):
        db_filename = tempfile.mktemp()
        script = self.temp_file(mode='w')

        script.file.write('.print "Hello"\n')
        script.file.flush()
        
        argv = ['test_nopersist', 
                '-f', db_filename,
                '-arch', script.name,
                '-nopersist']
        
        rsl.main(argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn('Hello', output)
        self.assertFalse(os.path.exists(db_filename))
    
    def test_persist(self):
        db = self.temp_file(mode='r')
        schema = self.temp_file(mode='w')
        script = self.temp_file(mode='w')
        
        schema.file.write('CREATE TABLE Cls (Id UNIQUE_ID);')
        schema.file.flush()
        
        script.file.write('.create object instance cls of Cls\n')
        script.file.write('.print "Hello"\n')
        script.file.flush()
        
        argv = ['test_persist', 
                '-f', db.name,
                '-import', schema.name,
                '-arch', script.name]
        
        rsl.main(argv)
        output = sys.stdout.getvalue().strip()
        self.assertIn('Hello', output)
        
        with open(db.name, 'r') as f:
            s = f.read()
            self.assertIn('CREATE TABLE', s)
            self.assertIn('INSERT INTO', s)
    
    def test_disable_emit(self):
        emit_filename = tempfile.mktemp().replace('\\', '/')
        script = self.temp_file(mode='w')
        script.file.write('Test\n')
        script.file.write('.emit to file "%s"\n' % emit_filename)
        script.file.flush()
        
        argv = ['test_disable_emit', 
                '-arch', script.name,
                '-emit', 'never',
                '-nopersist']
        
        rsl.main(argv)
        self.assertFalse(os.path.exists(emit_filename))

    def test_diff(self):
        diff = self.temp_file(mode='r')
        emit = self.temp_file(mode='r')
        script = self.temp_file(mode='w')
        script.file.write('Hello file\n')
        script.file.write('.emit to file "%s"\n' % emit.name.replace('\\', '/'))
        script.file.flush()
        
        argv = ['test_diff', 
                '-arch', script.name,
                '-diff', diff.name,
                '-nopersist']
        
        rsl.main(argv)
        with open(diff.name, 'r') as f:
            s = f.read()
            self.assertIn('test_diff -arch', s)
            self.assertIn('Hello file', s)
        

if __name__ == "__main__":
    unittest.main()

