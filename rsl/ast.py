# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Abstract syntax tree node definitions for the rule-specification language (RSL).  
'''


class Node(object):

    def __str__(self):
        return self.__class__.__name__
    

#
# Top-level node in a parsed file
#

class BodyNode(Node):
    statement_list = None

    def __init__(self, statement_list):
        self.statement_list = statement_list

#
# Template-related nodes
#    

class LiteralListNode(Node):
    literals = None
    
    def __init__(self):
        self.literals = list()


class LiteralNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value


class SubstitutionVariableNode(Node):
    expr = None
    formats = list() 
    
    def __init__(self, fmt, expr):
        self.formats = fmt
        self.expr = expr


class SubstitutionNavigationNode(Node):
    variable = None
    relation = None
    
    def __init__(self, variable, navigation):
        self.variable = variable
        self.navigation = navigation
        

class ParseKeywordNode(Node):
    expr = None
    keyword = None
    
    def __init__(self, expr, keyword):
        self.expr = expr
        self.keyword = keyword
        

#
# FUnction related nodes
#

class FunctionNode(Node):
    name = None
    parameter_list = None
    statement_list = None

    def __init__(self, name, params, body):
        self.name = name
        self.parameter_list = params
        self.statement_list = body


class ParameterNode(Node):
    name = None
    type = None

    def __init__(self, ty, name):
        self.name = name
        self.type = ty


class ParameterListNode(Node):
    parameters = list()
    
    def __init__(self):
        self.parameters = list()


class ArgumentListNode(Node):
    arguments = list()
    
    def __init__(self):
        self.arguments = list()


class StatementListNode(Node):
    statements = list()
    
    def __init__(self):
        self.statements = list()


#
# Function-like statements
#

class ExitNode(Node):
    return_code = None

    def __init__(self, return_code):
        self.return_code = return_code


class IncludeNode(Node):
    inc_filename = None

    def __init__(self, filename):
        self.inc_filename = filename


class PrintNode(Node):
    value_list = None

    def __init__(self, value_list):
        self.value_list = value_list


class EmitNode(Node):
    emit_filename = None

    def __init__(self, filename):
        self.emit_filename = filename

class ClearNode(Node):
    pass


#
# Assignment statements
#

class AssignNode(Node):
    variable = None
    expr = None

    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

class InvokeNode(Node):
    function_name = None
    argument_list = None
    variable_name = None

    def __init__(self, function_name, args, variable_name=None):
        self.function_name = function_name
        self.argument_list = args
        self.variable_name = variable_name


#
# Meta model manipulation statements
#

class CreateNode(Node):
    variable_name = None
    key_letter = None

    def __init__(self, variable_name, key_letter):
        self.variable_name = variable_name
        self.key_letter = key_letter


class SelectNode(Node):
    variable_name = None
    instance_chain = None
    where = None
    
    def __init__(self, variable_name, instance_chain, where):
        self.variable_name = variable_name
        self.instance_chain = instance_chain
        self.where = where
        

class SelectFromNode(Node):
    variable_name = None
    key_letter = None
    where = None
    
    def __init__(self, variable_name, key_letter, where):
        self.variable_name = variable_name
        self.key_letter = key_letter
        self.where = where
        

class SelectAnyInstanceNode(SelectFromNode):
    pass


class SelectManyInstanceNode(SelectFromNode):
    pass


class SelectOneNode(SelectNode):
    pass


class SelectAnyNode(SelectNode):
    pass


class SelectManyNode(SelectNode):
    pass


class WhereNode(Node):
    expr = None
    
    def __init__(self, expr=None):
        self.expr = expr
        

class InstanceChainNode(Node):
    variable = None
    navigations = list()
    
    def __init__(self, variable):
        self.variable = variable
        self.navigations = list()


class NavigationNode(Node):
    key_letter = None
    relation = None
    
    def __init__(self, key_letter, relation):
        self.key_letter = key_letter
        self.relation = relation


class RelationNode(Node):
    rel_id = None
    phrase = ''
    
    def __init__(self, rel_id, phrase=''):
        self.rel_id = rel_id
        self.phrase = phrase


class AlXlateNode(Node):
    activity_type = None
    inst_ref = None

    def __init__(self, activity_type, inst_ref):
        self.activity_type = activity_type
        self.inst_ref = inst_ref

#
# Control flow statements
#

class IfNode(Node):
    cond = None
    iftrue = None
    iffalse = None
    elif_list = None

    def __init__(self, cond, iftrue, elif_list, iffalse):
        self.cond = cond
        self.iftrue = iftrue
        self.elif_list = elif_list
        self.iffalse = iffalse


class ElIfListNode(Node):
    elifs = None
    
    def __init__(self):
        self.elifs = list()


class ElIfNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list
    
    
#
# Loop statements
#
    
class ForNode(Node):
    variable_name = None
    set_name = None
    statement_list = None

    def __init__(self, variable_name, set_name, statement_list):
        self.variable_name = variable_name
        self.set_name = set_name
        self.statement_list = statement_list


class WhileNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list


class BreakNode(Node):
    pass


#
# Expressions
#
    
class BinaryOpNode(Node):
    sign = None
    left = None
    right = None
    
    def __init__(self, left, sign, right):
        self.sign = sign.lower()
        self.left = left
        self.right = right
    

class UnaryOpNode(Node):
    sign = None
    value = None
    
    def __init__(self, sign, value):
        self.sign = sign.lower()
        self.value = value
    

class VariableAccessNode(Node):
    name = None
    
    def __init__(self, name):
        self.name = name


class FieldAccessNode(Node):
    variable = None
    field = None
    
    def __init__(self, variable, field):
        self.variable = variable
        self.field = field


class StringBodyNode(Node):
    values = list()
    
    def __init__(self):
        self.values = list()


class StringValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value


class IntegerValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value


class RealValueNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value

