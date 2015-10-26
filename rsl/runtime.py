# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
High-level runtime behavior for the RSL language, e.g. builtin functions and 
helper functions like 'emit to file'.
'''


import sys
import os
import stat
import subprocess
import datetime
import logging
import re
import difflib

import rsl.version
import xtuml.model

from functools import partial

try:
    from future_builtins import filter
except ImportError:
    pass

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


logger = logging.getLogger(__name__)


class RuntimeException(Exception):
    pass


class Info(object):
    '''
    Helper class for providing access to the built-in
    substitution variables "${info.date}" et.al.
    '''
    def __init__(self, metamodel):
        self.metamodel = metamodel
        self.arch_file_name = ''
        self.arch_file_line = 0
        
    @property
    def date(self):
        now = datetime.datetime.now()
        now = datetime.datetime.ctime(now)
        return now
    
    @property
    def unique_num(self):
        return next(self.metamodel.id_generator)
    
    @property
    def user_id(self):
        return os.getlogin()
    
    @property
    def interpreter_version(self):
        return rsl.version.complete_string
    
    @property
    def interpreter_platform(self):
        return os.name


class Fragment(xtuml.model.BaseObject):
    __r__ = dict()
    __q__ = dict()
    __c__ = dict()
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        xtuml.model.BaseObject.__init__(self)


class Runtime(object):

    bridges = dict()
    
    def __init__(self, metamodel, emit=None, force=False, diff=None):
        self.metamodel = metamodel
        self.emit = emit
        self.force_emit = force
        self.diff = diff
        self.functions = dict()
        self.buffer = StringIO()
        self.include_cache = dict()
        self.info = Info(metamodel)
        
    @staticmethod
    def format_string(expr, fmt):
        whitespace_regexp = re.compile(r'\s+')
        nonword_regexp = re.compile(r'[^\w]')

        def not_implemented(value):
            raise RuntimeException('Not implemented')
        
        def chain_item(direction, item, value):
            regexp = {
                'back': re.compile(r"(\s*->\s*([\w]+)\[[Rr](\d+)(?:\.\'([^\']+)\')?\]\s*)$"),
                'front': re.compile(r"(\s*->\s*([\w]+)\[[Rr](\d+)(?:\.\'([^\']+)\')?\]\s*)")
            }
            group_num = {
                'kl': 2,
                'rel': 3,
                'phrase': 4
            }
            result = regexp[direction].search(value)
            if not result:
                return ''
            
            if direction == 'front' and item == 'rest':
                return value[result.end():]
            
            elif direction == 'back' and item == 'rest':
                return value[:result.start(1)]
            else:
                return result.group(group_num[item]) or ''

        def o(value):
            value = value.replace('_', ' ')
            value = value.title()
            value = re.sub(nonword_regexp, '', value)
            value = re.sub(whitespace_regexp, '', value)
            if value:
                value = value[0].lower() + value[1:]
            return value
            
        ops = {
                'u':          lambda value: value.upper(),
                'c':          lambda value: value.title(),
                'l':          lambda value: value.lower(),
                '_':          lambda value: re.sub(whitespace_regexp, '_', value),
                'r':          lambda value: re.sub(whitespace_regexp, '', value),
                'o':          o,
                'tnosplat':   lambda value: value.replace('*', ''),
                'tstrsep_':   lambda value: next(value.split('_', 1)),
                't_strsep':   not_implemented,
                't2tick':     lambda value: value.replace('\\', '\\\\'),
                'tnonl':      lambda value: value.replace('\n', ' '),
                'txmlclean':  not_implemented,
                'txmlquot':   not_implemented,
                'txmlname':   not_implemented,
                'tu2d':       not_implemented,
                'td2u':       not_implemented,
                'tcf_kl':     partial(chain_item, 'front', 'kl'),
                'tcf_rel':    partial(chain_item, 'front', 'rel'),
                'tcf_phrase': partial(chain_item, 'front', 'phrase'),
                'tcf_rest':   partial(chain_item, 'front', 'rest'),
                'tcb_kl':     partial(chain_item, 'back', 'kl'),
                'tcb_rel':    partial(chain_item, 'back', 'rel'),
                'tcb_phrase': partial(chain_item, 'back', 'phrase'),
                'tcb_rest':   partial(chain_item, 'back', 'rest')
        }
        
        s = '%s' % expr
        for ch in fmt:
            s = ops[ch.lower()](s)
    
        return s
    
    @staticmethod
    def parse_keyword(expr, keyword):
        regexp = re.compile(keyword + ":([^\n]*)")
        result = regexp.search(expr)
        
        if result:
            return result.groups()[0].strip()
        else:
            return ''
    
    def define_function(self, name, fn):
        self.functions[name] = fn
        
    def invoke_function(self, name, args):
        if name in self.functions:
            fn = self.functions[name]
        elif name in self.bridges:
            fn = self.bridges[name]
        else:
            raise RuntimeException("Function '%s' is undefined" % name)
        
        previous_buffer = self.buffer
        self.buffer = StringIO()
        
        d = fn(*args)
        return_values = dict({'body': self.buffer.getvalue()})
        
        self.buffer.close()
        self.buffer = previous_buffer
        
        for key, value in d.items():
            if key.lower().startswith("attr_"):
                key = key.split("_", 1)[1]
                return_values[key] = value
        
        return Fragment(**return_values)
    
    def invoke_print(self, value, prefix='INFO'):
        sys.stdout.write("%s: %d:  %s:  %s\n" % (os.path.basename(self.info.arch_file_name),
                                                   self.info.arch_file_line,
                                                   prefix,
                                                   value))
    
    @staticmethod
    def invoke_exit(exit_code):
        sys.exit(exit_code)
        
    @staticmethod
    def cast_to_set(value):
        if not isinstance(value, xtuml.model.QuerySet):
            return xtuml.model.QuerySet([value])
        else:
            return value
        
    def buffer_literal(self, literal):
        if   literal.endswith('\\' * 3):
            self.buffer.write(literal[:-2])
        
        elif literal.endswith('\\' * 2):
            self.buffer.write(literal[:-1])
            self.buffer.write('\n')
            
        elif literal.endswith('\\'):
            self.buffer.write(literal[:-1])
            
        elif literal.endswith('\n'):
            self.buffer.write(literal)
            
        else:
            self.buffer.write(literal)
            self.buffer.write('\n')
    
    def append_diff(self, filename, org, buf):
        org = org.splitlines(1)
        buf = buf.splitlines(1)
        
        fromfile = filename
        tofile = filename
        
        if os.path.exists(filename):
            fromdate = os.path.getctime(filename)
            fromdate = datetime.datetime.fromtimestamp(fromdate)
            todate = str(datetime.datetime.now())
        else:
            fromdate = ''
            todate = ''
        
        diff = difflib.unified_diff(org, buf, fromfile, tofile, fromdate, todate)

        with open(self.diff, 'a') as f:
            f.write(''.join(diff))

    def emit_buffer(self, filename):
        org = ''
        buf = self.buffer.getvalue()
        
        self.clear_buffer()
        
        if buf and not buf.endswith('\n'):
            buf += '\n'
            
        filename = os.path.normpath(filename)
        if os.path.exists(filename):
            with open(filename, 'rU') as f:
                org = f.read()
        
        if self.emit == 'never':
            do_write = False 
            
        elif self.emit == 'change' and org == buf:
            do_write = False
        
        else:
            do_write = True
                
        if self.diff:
            self.append_diff(filename, org, buf)

        if do_write and self.force_emit and os.path.exists(filename):
            st = os.stat(filename)
            os.chmod(filename, st.st_mode | stat.S_IWRITE)

        if do_write:
            dirname = os.path.dirname(filename)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)

            if os.path.exists(filename):
                self.invoke_print("File '%s' REPLACED" % filename)
            else:
                self.invoke_print("File '%s' CREATED" % filename)

            with open(filename, 'w+') as f:
                f.write(buf)
    
    def clear_buffer(self):
        self.buffer.close()
        self.buffer = StringIO()

    def new(self, key_letter):
        return self.metamodel.new(key_letter)
    
    def chain(self, inst):
        return xtuml.navigate_many(inst)
    
    def select_any_from(self, key_letter, where_cond):
        return self.metamodel.select_any(key_letter, where_cond)
         
    def select_many_from(self, key_letter, where_cond):
        return self.metamodel.select_many(key_letter, where_cond)

    @staticmethod
    def select_many_in(inst_set, where_cond):
        s = filter(where_cond, inst_set)
        return xtuml.QuerySet(s)

    @staticmethod
    def select_any_in(inst_set, where_cond):
        for inst in iter(inst_set):
            if where_cond(inst):
                return inst

    @staticmethod
    def select_one_in(inst_set, where_cond):
        cardinality = Runtime.cardinality(inst_set)
        if cardinality > 1:
            raise RuntimeException('select one from a set with cardinality %d' % cardinality)
        
        return Runtime.select_any_in(inst_set, where_cond)
                
    @staticmethod
    def cardinality(arg):
        if Runtime.is_set(arg): 
            return len(arg) 
        
        if Runtime.is_instance(arg): 
            return 1
        
        return 0
    
    @staticmethod
    def empty(arg):
        return Runtime.cardinality(arg) == 0
    
    @staticmethod
    def not_empty(arg):
        return Runtime.cardinality(arg) != 0
    
    @staticmethod
    def first(inst, inst_set):
        if Runtime.is_instance(inst) and Runtime.is_set(inst_set):
            return inst == inst_set.first
    
    @staticmethod
    def not_first(inst, inst_set):
        if Runtime.is_instance(inst) and Runtime.is_set(inst_set):
            return inst != inst_set.first
    
    @staticmethod
    def last(inst, inst_set):
        if Runtime.is_instance(inst) and Runtime.is_set(inst_set):
            return inst == inst_set.last
    
    @staticmethod
    def not_last(inst, inst_set):
        if Runtime.is_instance(inst) and Runtime.is_set(inst_set):
            return inst != inst_set.last
    
    @staticmethod
    def is_set(inst):
        return isinstance(inst, xtuml.QuerySet)

    @staticmethod
    def is_instance(inst):
        return isinstance(inst, xtuml.BaseObject)

    def assert_type(self, exptected_type, value):
        value_type = self.type_name(type(value))
        if exptected_type.upper() != value_type.upper():
            raise RuntimeException('expected type %s, not %s' % (exptected_type, value_type))
        
    def type_name(self, ty):
        if   issubclass(ty, bool): return 'boolean'
        elif issubclass(ty, int): return 'integer'
        elif issubclass(ty, float): return 'real'
        elif issubclass(ty, str): return 'string'
        elif issubclass(ty, Fragment): return 'frag_ref'
        elif issubclass(ty, xtuml.BaseObject): return 'inst_ref'
        elif issubclass(ty, type(None)): return 'inst_ref'
        elif issubclass(ty, xtuml.QuerySet): return 'inst_ref_set'
        elif issubclass(ty, type(self.metamodel.id_generator.peek())): return 'unique_id'
        else: raise RuntimeException("Unknown type '%s'" % ty.__name__)
        

class bridge(object):
    cls = None
    name = None
    
    def __init__(self, name, cls=None):
        self.name = name
        self.cls = cls
        
    def __call__(self, f):
        cls = self.cls or Runtime
        name = self.name or f.__name__
        
        def wrapper(*args):
            res = {}
            rc = f(*args) or {}
            for key, value in rc.items():
                res['attr_%s' % key] = value
            return res
        
        cls.bridges[name] = wrapper
        
        return f
    
    
@bridge('GET_ENV_VAR')
def get_env_var(name):
    if name in os.environ:
        result = os.environ[name]
        success = True
    else:
        result = ''
        success = False
        
    return {'success': success,
            'result': result}


@bridge('PUT_ENV_VAR')
def put_env_var(value, name):
    os.environ[name] = value
    return {'success': name in os.environ}


@bridge('SHELL_COMMAND')
def shell_command(cmd):
    return {'result': subprocess.call(cmd, shell=True)}


@bridge('FILE_READ')
def file_read(filename):
    try:
        with open(filename, 'r') as f:
            result = f.read()
            success = True
    except:
        success = False
        result = ''
            
    return {'success': success,
            'result': result}


@bridge('FILE_WRITE')
def file_write(contents, filename):
    try:
        with open(filename, 'w') as f:
            f.write('%s\n' % contents)
            success = True
    except:
        success = False
        
    return {'success': success}


@bridge('STRING_TO_INTEGER')
def string_to_integer(value):
    try:
        return {'result': int(value.strip())}
    except:
        raise RuntimeException('Unable to convert the string "%s" to an integer' % value)

    
@bridge('STRING_TO_REAL')
def string_to_real(value):
    try:
        return {'result': float(value.strip())}
    except:
        raise RuntimeException('Unable to convert the string "%s" to a real' % value)

    
@bridge('INTEGER_TO_STRING')
def integer_to_string(value):
    return {'result': str(value)}


@bridge('REAL_TO_STRING')
def real_to_string(value):
    return {'result': str(value)}


@bridge('BOOLEAN_TO_STRING')
def boolean_to_string(value):
    return {'result': str(value).upper()}  

