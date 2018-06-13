# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Evaluation of syntax trees constructed from the rule-specification language (RSL).  
'''


import sys
import os
import logging

import xtuml

from . import symtab
from . import parse
from . import runtime

logger = logging.getLogger(__name__)


class BreakException(Exception):
    pass


class EvalWalker(xtuml.Walker):
    
    def __init__(self, rt, includes):
        xtuml.Walker.__init__(self)
        self.runtime = rt
        self.includes = includes
        self.callstack = list()
        self.symtab = symtab.SymbolTable()
        
        self.symtab.install_global('true', True)
        self.symtab.install_global('false', False)
        self.symtab.install_global('info', self.runtime.info)
                
        self.symtab.enter_scope()
                    
    def accept(self, node, **kwargs):
        self.runtime.info.arch_file_path = node.filename
        self.runtime.info.arch_file_line = node.lineno

        try:
            return xtuml.Walker.accept(self, node, **kwargs)
        except BreakException as e:
            raise e
        except Exception as e:
            self.runtime.invoke_print(e, 'ERROR')
            print('Traceback  (most recent call last):')
            for n in self.callstack + [node]:
                print('    File "%s", line %d' % (n.filename, n.lineno))
            #print(traceback.format_exc())
            sys.exit(e)
    
    def default_accept(self, node, **kwargs):
        print ('> %s' % node.__class__.__name__)
            
    def accept_BodyNode(self, node):
        self.accept(node.statement_list)
        
    def accept_FunctionNode(self, node):
        def _(fn, *args):
            self.symtab.enter_scope()
            
            self.accept(fn.parameter_list, args=reversed(args))
            for stmt in fn.statement_list.statements:
                self.accept(stmt)

            return self.symtab.leave_scope()
        
        self.runtime.define_function(node.name, lambda *args: _(node, *args))
    
    def accept_ParameterListNode(self, node, args):
        args = list(args)
        if len(args) != len(node.parameters):
            raise runtime.RuntimeException('wrong number of arguments')
        
        for param, arg in zip(node.parameters, args):
            self.accept(param, arg=arg)

    def accept_ParameterNode(self, node, arg):
        self.runtime.assert_type(node.type, arg)
        self.symtab.install_symbol(node.name, arg)

    def accept_InvokeNode(self, node):
        args = self.accept(node.argument_list)
        args = [arg.fget() for arg in args]
        
        self.callstack.append(node)
        value = self.runtime.invoke_function(node.function_name, args)
        self.callstack.pop()
        
        if node.variable_name:
            self.symtab.install_symbol(node.variable_name, value)
    
    def accept_ArgumentListNode(self, node):
        return [self.accept(arg) for arg in node.arguments]

    def accept_StatementListNode(self, node):
        for stmt in node.statements:
            self.accept(stmt)
            
    def accept_AssignNode(self, node):
        value = self.accept(node.expr).fget()
        variable = self.accept(node.variable)
        variable.fset(value)
        
    def accept_StringBodyNode(self, node):
        s = ''
        for value in node.values:
            s += self.accept(value).fget()
            
        return property(lambda: s)
    
    def accept_StringValueNode(self, node):
        s = node.value
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        
        return property(lambda: s)
        
    def accept_IntegerValueNode(self, node):
        i = int(node.value)
        
        return property(lambda: i)
        
    def accept_RealValueNode(self, node):
        i = float(node.value)
        
        return property(lambda: i)
        
    def accept_VariableAccessNode(self, node):
        return property(lambda: self.symtab.find_symbol(node.name))
    
    def accept_VariableAssignmentNode(self, node):
        setter = lambda val: self.symtab.install_symbol(node.name, val)

        return property(fset=setter)
        
    def accept_FieldAccessNode(self, node):
        variable = self.accept(node.variable).fget()
        
        return property(lambda: getattr(variable, node.field))
    
    def accept_FieldAssignmentNode(self, node):
        variable = self.accept(node.variable).fget()
        
        return property(fset=lambda val: setattr(variable, node.field, val))
        
    def accept_SubstitutionVariableNode(self, node):
        value = self.accept(node.expr).fget()
        value = self.runtime.format_string(value, node.formats)

        return property(lambda: value)
    
    def accept_SubstitutionNavigationNode(self, node):
        variable = self.accept(node.variable).fget()
        chain = self.runtime.chain(variable)
        
        key_letter = node.navigation.key_letter
        rel_id = node.navigation.relation.rel_id
        phrase = node.navigation.relation.phrase
        
        inst_set = chain.nav(key_letter, rel_id, phrase)()
        value = self.runtime.select_any_in(inst_set, lambda selected: True)
        
        return property(lambda: value)
    
    def accept_ParseKeywordNode(self, node):
        keyword = self.accept(node.keyword).fget()
        value = self.accept(node.expr).fget()
        value = self.runtime.parse_keyword(value, keyword)
        
        return property(lambda: value)
    
    def accept_PrintNode(self, node):
        value = self.accept(node.value_list).fget()
        self.runtime.invoke_print(value)

    def accept_ExitNode(self, node):
        value = self.accept(node.return_code).fget()
        self.runtime.invoke_exit(value)
        
    def accept_IfNode(self, node):
        try:
            self.symtab.enter_block()
            if self.accept(node.cond).fget():
                self.accept(node.iftrue)
            elif not self.accept(node.elif_list).fget():
                self.accept(node.iffalse)
            self.symtab.leave_block()
        except BreakException as e:
            self.symtab.leave_block()
            raise e
                        
    def accept_ElIfListNode(self, node):
        b = False
        for _elif in node.elifs:
            b = self.accept(_elif).fget()
            if b: break
            
        return property(lambda: b)
    
    def accept_ElIfNode(self, node):
        b = self.accept(node.cond).fget()
        if b:
            self.accept(node.statement_list)

        return property(lambda: b)
    
    def accept_WhileNode(self, node):
        try:
            self.symtab.enter_block()
            while self.accept(node.cond).fget():
                self.accept(node.statement_list)
            self.symtab.leave_block()
        except BreakException:
            self.symtab.leave_block()
        
    def accept_ForNode(self, node):
        try:
            self.symtab.enter_block()
            handle = self.symtab.find_symbol(node.set_name)
            for value in iter(handle):
                iterator_name = '_%d' % id(handle)
                self.symtab.install_symbol(iterator_name, value)
                self.symtab.install_symbol(node.variable_name, value)
                self.accept(node.statement_list)
            self.symtab.leave_block()
        except BreakException:
            self.symtab.leave_block()

    def accept_BreakNode(self, node):
        raise BreakException()

    def accept_BinaryOpNode(self, node):
        ops = {
            '|':   lambda lhs, rhs: (lhs | rhs),
            '&':   lambda lhs, rhs: (lhs & rhs),
            '+':   lambda lhs, rhs: (lhs + rhs),
            '-':   lambda lhs, rhs: (lhs - rhs),
            '*':   lambda lhs, rhs: (lhs * rhs),
            '^':   lambda lhs, rhs: (lhs ^ rhs),
            '%':   lambda lhs, rhs: (lhs % rhs),
            '/':   lambda lhs, rhs: (lhs / rhs),
            '<':   lambda lhs, rhs: (lhs < rhs),
            '<=':  lambda lhs, rhs: (lhs <= rhs),
            '>':   lambda lhs, rhs: (lhs > rhs),
            '>=':  lambda lhs, rhs: (lhs >= rhs),
            '!=':  lambda lhs, rhs: (lhs != rhs),
            '==':  lambda lhs, rhs: (lhs == rhs),
            'or':  lambda lhs, rhs: (lhs or  rhs),
            'and': lambda lhs, rhs: (lhs and rhs),
        }

        lhs = self.accept(node.left).fget()

        if node.sign == 'or' and lhs == True:
            return property(lambda: True)
        elif node.sign == 'and' and lhs == False:
            return property(lambda: False)

        rhs = self.accept(node.right).fget()
        
        if node.sign in ['|', '&', '^'] and self.runtime.is_instance(lhs):
            lhs = self.runtime.cast_to_set(lhs)
            
        if self.runtime.is_set(lhs):
            rhs = self.runtime.cast_to_set(rhs)

        if self.runtime.is_set(rhs):
            lhs = self.runtime.cast_to_set(lhs)
            
        value = ops[node.sign](lhs, rhs)
        
        return property(lambda: value)
    
    def accept_UnaryOpNode(self, node):
        ops = {
            '-':           lambda value:-value,
            'not':         lambda value: not value,
            'cardinality': lambda value: self.runtime.cardinality(value),
            'empty':       lambda value: self.runtime.empty(value),
            'first':       lambda value: self.runtime.first(self.symtab.find_symbol('_%d' % id(value)), value),
            'last':        lambda value: self.runtime.last(self.symtab.find_symbol('_%d' % id(value)), value),
            'not_empty':   lambda value: self.runtime.not_empty(value),
            'not_first':   lambda value: self.runtime.not_first(self.symtab.find_symbol('_%d' % id(value)), value),
            'not_last':    lambda value: self.runtime.not_last(self.symtab.find_symbol('_%d' % id(value)), value),
        }

        value = self.accept(node.value).fget()
        value = ops[node.sign](value)
        
        return property(lambda: value)
    
    def accept_LiteralNode(self, node):
        s = node.value
        
        return property(lambda: s)
    
    def accept_LiteralListNode(self, node):
        s = ''
        for literal in node.literals:
            s += self.accept(literal).fget()
         
        self.runtime.buffer_literal(s)
        
    def accept_EmitNode(self, node):
        filename = self.accept(node.emit_filename).fget()
        self.runtime.emit_buffer(filename)
    
    def accept_ClearNode(self, node):
        self.runtime.clear_buffer()
            
    def accept_IncludeNode(self, node):
        filename = self.accept(node.inc_filename).fget()
        root = None
        
        # check cache
        if filename in self.runtime.include_cache:
            root = self.runtime.include_cache[filename]
        
        # check absolute path
        elif os.path.isabs(filename):
            root = parse.parse_file(filename)
            self.runtime.include_cache[filename] = root

        # search relative include paths
        else:
            paths_to_search = [self.runtime.info.arch_folder_path]
            paths_to_search.extend(self.includes)
            paths_to_search = filter(None, paths_to_search)
            
            for path in paths_to_search:
                abs_path = '%s/%s' % (path, filename)
                if os.path.exists(abs_path):
                    root = parse.parse_file(abs_path)
                    self.runtime.include_cache[filename] = root
                    break
            
        if root is None:
            raise Exception("unable to find '%s'" % filename)
        
        self.callstack.append(node)
        self.accept(root)
        self.callstack.pop()
        
    def accept_CreateNode(self, node):
        inst = self.runtime.new(node.key_letter)
        self.symtab.install_symbol(node.variable_name, inst)
        
        return property(lambda: inst)
        
    def accept_SelectAnyInstanceNode(self, node):
        where = self.accept(node.where)
        value = self.runtime.select_any_from(node.key_letter, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)
        
    def accept_SelectManyInstanceNode(self, node):
        where = self.accept(node.where)
        order_by = self.accept(node.order_by)
        value = self.runtime.select_many_from(node.key_letter, where, order_by)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_SelectOneNode(self, node):
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        value = self.runtime.select_one_in(inst_set, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_SelectAnyNode(self, node):
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        value = self.runtime.select_any_in(inst_set, where)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)
        
    def accept_SelectManyNode(self, node):
        inst_set = iter(self.accept(node.instance_chain).fget())
        where = self.accept(node.where)
        order_by = self.accept(node.order_by)
        value = self.runtime.select_many_in(inst_set, where, order_by)
        
        self.symtab.install_symbol(node.variable_name, value)
        
        return property(lambda: value)

    def accept_WhereNode(self, node):
        def where(expr, selected):
            if node.expr is None:
                return True
            
            self.symtab.enter_block()
            self.symtab.install_symbol('selected', selected)
            value = self.accept(expr).fget()
            self.symtab.leave_block()
            
            return value
            
        return lambda selected: where(node.expr, selected)

    def accept_OrderByNode(self, node):
        if len(node.attributes):
            if node.reverse:
                return xtuml.reverse_order_by(*node.attributes)
            else:
                return xtuml.order_by(*node.attributes)
        
    def accept_InstanceChainNode(self, node):
        inst = self.accept(node.variable).fget()
        chain = self.runtime.chain(inst)
        
        for nav in node.navigations:
            rel_id = nav.relation.rel_id
            phrase = nav.relation.phrase
            chain = chain.nav(nav.key_letter, rel_id, phrase)
        
        result = chain()
        
        return property(lambda: result)
    
    def accept_RelateNode(self, node):
        from_inst = self.symtab.find_symbol(node.from_variable_name)
        to_inst = self.symtab.find_symbol(node.to_variable_name)
        
        xtuml.relate(from_inst, to_inst, node.rel_id, node.phrase)
        
    def accept_RelateUsingNode(self, node):
        from_inst = self.symtab.find_symbol(node.from_variable_name)
        to_inst = self.symtab.find_symbol(node.to_variable_name)
        using_inst = self.symtab.find_symbol(node.using_variable_name)
        
        xtuml.relate(from_inst, using_inst, node.rel_id, node.phrase)
        xtuml.relate(using_inst, to_inst, node.rel_id, node.phrase)
        
    def accept_UnrelateNode(self, node):
        from_inst = self.symtab.find_symbol(node.from_variable_name)
        to_inst = self.symtab.find_symbol(node.to_variable_name)
        
        xtuml.unrelate(from_inst, to_inst, node.rel_id, node.phrase)
        
    def accept_UnrelateUsingNode(self, node):
        from_inst = self.symtab.find_symbol(node.from_variable_name)
        to_inst = self.symtab.find_symbol(node.to_variable_name)
        using_inst = self.symtab.find_symbol(node.using_variable_name)
        
        xtuml.unrelate(from_inst, using_inst, node.rel_id, node.phrase)
        xtuml.unrelate(using_inst, to_inst, node.rel_id, node.phrase)
        
    def accept_DeleteNode(self, node):
        inst = self.symtab.find_symbol(node.variable_name)
        xtuml.delete(inst)

        
def evaluate(rt, ast, includes):
    w = EvalWalker(rt, includes)
    return w.accept(ast)
    
