# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Abstract syntax tree node definitions for the rule-specification language (RSL).  
'''


class Node(object):
    filename = None
    lineno = 0
    
    def __str__(self):
        return self.__class__.__name__
    
    @property
    def children(self):
        return tuple()
        
#
# Top-level node in a parsed file
#

class BodyNode(Node):
    statement_list = None

    def __init__(self, statement_list):
        self.statement_list = statement_list

    @property
    def children(self):
        return (self.statement_list,)
        
#
# Template-related nodes
#    

class LiteralListNode(Node):
    literals = None
    
    def __init__(self):
        self.literals = list()

    @property
    def children(self):
        return iter(self.literals)
        
class LiteralNode(Node):
    value = None
    
    def __init__(self, value):
        self.value = value


class SubstitutionVariableNode(Node):
    expr = None
    formats = None
    
    def __init__(self, fmt, expr):
        self.formats = fmt
        self.expr = expr

    @property
    def children(self):
        return (self.expr,)


class SubstitutionNavigationNode(Node):
    variable = None
    navigation = None
    
    def __init__(self, variable, navigation):
        self.variable = variable
        self.navigation = navigation
        
    @property
    def children(self):
        return (self.variable,)
        
        
class ParseKeywordNode(Node):
    expr = None
    keyword = None
    
    def __init__(self, expr, keyword):
        self.expr = expr
        self.keyword = keyword
        
    @property
    def children(self):
        return (self.expr, self.keyword)

#
# Function related nodes
#

class FunctionNode(Node):
    name = None
    parameter_list = None
    statement_list = None

    def __init__(self, name, params, body):
        self.name = name
        self.parameter_list = params
        self.statement_list = body

    @property
    def children(self):
        return (self.parameter_list, self.statement_list)


class ParameterNode(Node):
    name = None
    type = None

    def __init__(self, ty, name):
        self.name = name
        self.type = ty

    @property
    def children(self):
        return (self.type,)


class ParameterTypeNode(Node):
    name = None
    kind = None

    def __init__(self, name, kind=None):
        self.name = name
        self.kind = kind


class ParameterListNode(Node):
    parameters = None
    
    def __init__(self):
        self.parameters = list()

    @property
    def children(self):
        return iter(self.parameters)


class ArgumentListNode(Node):
    arguments = None
    
    def __init__(self):
        self.arguments = list()

    @property
    def children(self):
        return iter(self.arguments)
        

class StatementListNode(Node):
    statements = None
    
    def __init__(self):
        self.statements = list()

    @property
    def children(self):
        return iter(self.statements)
        

#
# Function-like statements
#

class ExitNode(Node):
    return_code = None

    def __init__(self, return_code):
        self.return_code = return_code

    @property
    def children(self):
        return (self.return_code,)


class IncludeNode(Node):
    inc_filename = None

    def __init__(self, filename):
        self.inc_filename = filename

    @property
    def children(self):
        return (self.inc_filename,)
        

class PrintNode(Node):
    value_list = None

    def __init__(self, value_list):
        self.value_list = value_list

    @property
    def children(self):
        return (self.value_list,)
        

class EmitNode(Node):
    emit_filename = None

    def __init__(self, filename):
        self.emit_filename = filename

    @property
    def children(self):
        return (self.emit_filename,)


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

    @property
    def children(self):
        return (self.variable, self.expr)


class InvokeNode(Node):
    function_name = None
    argument_list = None
    variable_name = None

    def __init__(self, function_name, argument_list, variable_name=None):
        self.function_name = function_name
        self.argument_list = argument_list
        self.variable_name = variable_name

    @property
    def children(self):
        return (self.argument_list,)
        

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

    @property
    def children(self):
        return (self.instance_chain, self.where)
        

class SelectFromNode(Node):
    variable_name = None
    key_letter = None
    where = None
    
    def __init__(self, variable_name, key_letter, where):
        self.variable_name = variable_name
        self.key_letter = key_letter
        self.where = where

    @property
    def children(self):
        return (self.where,)
        
        
class SelectAnyInstanceNode(SelectFromNode):
    pass


class SelectManyInstanceNode(SelectFromNode):
    order_by = None

    def __init__(self, variable_name, key_letter, where, order_by):
        super(SelectManyInstanceNode, self).__init__(variable_name, key_letter, where)
        self.order_by = order_by

    @property
    def children(self):
        return (self.where, self.order_by)


class SelectOneNode(SelectNode):
    pass


class SelectAnyNode(SelectNode):
    pass


class SelectManyNode(SelectNode):
    order_by = None

    def __init__(self, variable_name, instance_chain, where, order_by):
        super(SelectManyNode, self).__init__(variable_name, instance_chain, where)
        self.order_by = order_by

    @property
    def children(self):
        return (self.where, self.order_by)


class RelateNode(Node):
    from_variable_name = None
    to_variable_name = None
    rel_id = None
    phrase = None
    
    def __init__(self, from_variable_name, to_variable_name, rel_id, phrase):
        self.from_variable_name = from_variable_name
        self.to_variable_name = to_variable_name
        self.rel_id = rel_id
        self.phrase = phrase


class RelateUsingNode(Node):
    from_variable_name = None
    to_variable_name = None
    rel_id = None
    phrase = None
    using_variable_name = None
    
    def __init__(self, from_variable_name, to_variable_name, rel_id, phrase,
                 using_variable_name):
        self.from_variable_name = from_variable_name
        self.to_variable_name = to_variable_name
        self.rel_id = rel_id
        self.phrase = phrase
        self.using_variable_name = using_variable_name


class UnrelateNode(Node):
    from_variable_name = None
    to_variable_name = None
    rel_id = None
    phrase = None
    
    def __init__(self, from_variable_name, to_variable_name, rel_id, phrase):
        self.from_variable_name = from_variable_name
        self.to_variable_name = to_variable_name
        self.rel_id = rel_id
        self.phrase = phrase
        

class UnrelateUsingNode(Node):
    from_variable_name = None
    to_variable_name = None
    rel_id = None
    phrase = None
    using_variable_name = None
    
    def __init__(self, from_variable_name, to_variable_name, rel_id, phrase,
                 using_variable_name):
        self.from_variable_name = from_variable_name
        self.to_variable_name = to_variable_name
        self.rel_id = rel_id
        self.phrase = phrase
        self.using_variable_name = using_variable_name
        

class DeleteNode(Node):
    variable_name = None
    
    def __init__(self, variable_name):
        self.variable_name = variable_name


class WhereNode(Node):
    expr = None
    
    def __init__(self, expr=None):
        self.expr = expr
        
    @property
    def children(self):
        return (self.expr,)
        
class OrderByNode(Node):
    reverse = False
    attributes = None
    
    def __init__(self, reverse=False):
        self.reverse = reverse
        self.attributes = list()

    @property
    def children(self):
        return iter(self.attributes)


class InstanceChainNode(Node):
    variable = None
    navigations = None
    
    def __init__(self, variable):
        self.variable = variable
        self.navigations = list()

    @property
    def children(self):
        l = [self.variable]
        l.extend(self.navigations)
        return l


class NavigationNode(Node):
    key_letter = None
    relation = None
    
    def __init__(self, key_letter, relation):
        self.key_letter = key_letter
        self.relation = relation

    @property
    def children(self):
        return (self.relation,)


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
    elif_list = None
    iffalse = None

    def __init__(self, cond, iftrue, elif_list, iffalse):
        self.cond = cond
        self.iftrue = iftrue
        self.elif_list = elif_list
        self.iffalse = iffalse

    @property
    def children(self):
        return (self.cond, self.iftrue, self.elif_list, self.iffalse)


class ElIfListNode(Node):
    elifs = None
    
    def __init__(self):
        self.elifs = list()

    @property
    def children(self):
        return iter(self.elifs)


class ElIfNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list
    
    @property
    def children(self):
        return (self.cond, self.statement_list)


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

    @property
    def children(self):
        return (self.statement_list,)


class WhileNode(Node):
    cond = None
    statement_list = None

    def __init__(self, cond, statement_list):
        self.cond = cond
        self.statement_list = statement_list

    @property
    def children(self):
        return (self.cond, self.statement_list)


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
    
    @property
    def children(self):
        return (self.left, self.right)
        

class UnaryOpNode(Node):
    sign = None
    value = None
    
    def __init__(self, sign, value):
        self.sign = sign.lower()
        self.value = value
    
    @property
    def children(self):
        return (self.value,)


class VariableAccessNode(Node):
    name = None
    
    def __init__(self, name):
        self.name = name

class VariableAssignmentNode(Node):
    name = None
    
    def __init__(self, name):
        self.name = name
        
class FieldAccessNode(Node):
    variable = None
    field = None
    
    def __init__(self, variable, field):
        self.variable = variable
        self.field = field

    @property
    def children(self):
        return (self.variable,)


class FieldAssignmentNode(Node):
    variable = None
    field = None
    
    def __init__(self, variable, field):
        self.variable = variable
        self.field = field

    @property
    def children(self):
        return (self.variable,)
        

class StringBodyNode(Node):
    values = None
    
    def __init__(self):
        self.values = list()

    @property
    def children(self):
        return iter(self.values)


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

