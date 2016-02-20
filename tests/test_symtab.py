# encoding: utf-8
# Copyright (C) 2015 John Törnblom

import unittest

import rsl.symtab


class TestSymbolTable(unittest.TestCase):


    def test_symbol_store(self):
        symtab = rsl.symtab.SymbolTable()
        handle = "TEST"
        
        symtab.enter_scope()
        symtab.enter_scope()
        
        symtab.install_symbol('Test', handle)
        value = symtab.find_symbol("Test")
        symtab.leave_scope()
        
        self.assertRaises(rsl.symtab.SymtabException, symtab.find_symbol, "Test")
        
        self.assertEqual(handle, value)
        
    def test_global_store(self):
        symtab = rsl.symtab.SymbolTable()

        g1 = "Test1"
        g2 = "Test2"
        
        symtab.enter_scope()
        symtab.install_global("g1", g1)
        
        symtab.enter_scope()
        symtab.install_global("g2", g2)
        symtab.leave_scope()

        self.assertEqual(symtab.find_symbol("g1"), g1)
        self.assertEqual(symtab.find_symbol("g2"), g2)
        
        symtab.leave_scope()
        
        self.assertRaises(rsl.symtab.SymtabException, symtab.find_symbol, "g1")
        self.assertRaises(rsl.symtab.SymtabException, symtab.find_symbol, "g2")
        
    def test_out_of_scope(self):
        symtab = rsl.symtab.SymbolTable()
        self.assertRaises(rsl.symtab.SymtabException, symtab.leave_scope)

    def test_out_of_block(self):
        symtab = rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        symtab.leave_block()
        
        self.assertRaises(rsl.symtab.SymtabException, symtab.leave_block)
        
    def test_symbol_rewrite(self):
        symtab = rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        
        symtab.install_symbol('TEST', 'TEST1')
        symtab.install_symbol('TEST', 'TEST2')
        
        value = symtab.find_symbol("TEST")
        symtab.leave_scope()
        
        self.assertEqual(value, 'TEST2')
        
    def test_get_scope_symbols(self):
        symtab = rsl.symtab.SymbolTable()
        
        symtab.enter_scope()
        self.assertEqual(len(symtab.scope_head.symbols), 0)
        
        symtab.install_symbol('TEST', 'TEST1')
        symtab.install_symbol('TEST', 'TEST2')
        self.assertEqual(len(symtab.scope_head.symbols), 1)
        
        symtab.install_symbol('TEST1', '')
        self.assertEqual(len(symtab.scope_head.symbols), 2)

        symtab.leave_scope()
        
        symtab.enter_scope()
        self.assertEqual(len(symtab.scope_head.symbols), 0)
        
