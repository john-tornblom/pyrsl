# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
High-level runtime behavior for the RSL language, e.g. builtin functions and 
helper functions like 'emit to file'.
'''


import sys
import os
import stat
import string
import subprocess
import datetime
import logging
import re
import difflib
import getpass
from functools import partial

import rsl.version
import xtuml

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
    arch_file_path = ''
    arch_file_line = 0
        
    def __init__(self, metamodel):
        self.metamodel = metamodel
    
    @property
    def arch_file_name(self):
        return os.path.basename(self.arch_file_path)
    
    @property
    def arch_folder_path(self):
        return os.path.dirname(self.arch_file_path)
    
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
        return getpass.getuser()
    
    @property
    def interpreter_version(self):
        return rsl.version.complete_string
    
    @property
    def interpreter_platform(self):
        return os.name


class MetaFragment(type):
    cache = dict()
    attributes = list()
    

class Fragment(xtuml.Class):
    __metaclass__ = MetaFragment
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        xtuml.Class.__init__(self)

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__

    
class Runtime(object):
    bridges = dict()
    string_formatters = dict()
    
    def __init__(self, metamodel, emit=None, force=False, diff=None):
        self.metamodel = metamodel
        self.emit = emit
        self.force_emit = force
        self.diff = diff
        self.functions = dict()
        self.buffer = StringIO()
        self.include_cache = dict()
        self.info = Info(metamodel)
        
    def format_string(self, expr, fmt):

        def apply_formats(s, formats):
            for formatter in formats:
                try:
                    f = self.string_formatters[formatter.lower()]
                except KeyError:
                    raise RuntimeException('%s is not a valid string formatter' % formatter)
                s = f(s)
            return s

        s = '%s' % expr
        
        s = apply_formats(s, [f for f in fmt if f[0] == 't'])
        s = apply_formats(s, [f for f in fmt if f[0] != 't'])
    
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
        sys.stdout.write("%s: %d:  %s:  %s\n" % (self.info.arch_file_name,
                                                 self.info.arch_file_line,
                                                 prefix,
                                                 value))
    
    @staticmethod
    def invoke_exit(exit_code):
        sys.exit(exit_code)
        
    @staticmethod
    def cast_to_set(value):
        if not isinstance(value, xtuml.QuerySet):
            return xtuml.QuerySet([value])
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
            fromdate = str(datetime.datetime.fromtimestamp(fromdate))
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
         
    def select_many_from(self, key_letter, where_cond, order_by):
        return self.metamodel.select_many(key_letter, where_cond, order_by)

    @staticmethod
    def select_many_in(inst_set, where_cond, order_by):
        s = filter(where_cond, inst_set)
        if order_by:
            s = order_by(s)
        
        return xtuml.QuerySet(s)

    @staticmethod
    def select_any_in(inst_set, where_cond):
        for inst in iter(inst_set):
            if where_cond(inst):
                return inst

    @staticmethod
    def select_one_in(inst_set, where_cond):
        inst_set = xtuml.QuerySet(inst_set)
        cardinality = Runtime.cardinality(inst_set)
        if cardinality > 1:
            raise RuntimeException('select one from a set with cardinality %d' % 
                                   cardinality)
        
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
        return isinstance(inst, xtuml.Class)

    def assert_type(self, exptected_type, value):
        value_type = self.type_name(type(value))
        if exptected_type.name.upper() != value_type.upper():
            raise RuntimeException('expected type %s, not %s' % 
                                   (exptected_type.name, value_type))
            
        if not exptected_type.kind:
            return
        
        value_kind = self.type_kind(value)
        if value_kind and exptected_type.kind.upper() != value_kind.upper():
            raise RuntimeException('expected kind %s, not %s' % 
                                   (exptected_type.kind, value_kind))
        
    def type_name(self, ty):
        if   issubclass(ty, bool): return 'boolean'
        elif issubclass(ty, int): return 'integer'
        elif issubclass(ty, float): return 'real'
        elif issubclass(ty, str): return 'string'
        elif issubclass(ty, Fragment): return 'frag_ref'
        elif issubclass(ty, xtuml.Class): return 'inst_ref'
        elif issubclass(ty, type(None)): return 'inst_ref'
        elif issubclass(ty, xtuml.QuerySet): return 'inst_ref_set'
        elif issubclass(ty, type(self.metamodel.id_generator.peek())): return 'unique_id'
        else: raise RuntimeException("Unknown type '%s'" % ty.__name__)
        
    def type_kind(self, value):
        if isinstance(value, xtuml.QuerySet): 
            value = value.first
        
        if isinstance(value, xtuml.Class): 
            return value.__metaclass__.kind
        
        

class Bridge(object):
    '''
    Decorator for adding bridges to the Runtime class.
    '''
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
    
bridge = Bridge


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


class StringFormatter(object):
    '''
    Decorator for adding string formatters to the Runtime class.
    '''
    cls = None
    name = None
    
    def __init__(self, name, cls=None):
        self.name = name
        self.cls = cls
        
    def __call__(self, f):
        cls = self.cls or Runtime
        name = self.name or f.__name__

        cls.string_formatters[name] = f
        
        return f

string_formatter = StringFormatter


@string_formatter('o')
def camelcase(value):
    '''
    Make the first word all lower case, make the first character of each
    following word capitalized and all other characters of the words lower
    case. Characters other than a-Z a-z 0-9 are ignored.
    '''
    whitespace_regexp = re.compile(r'\s+')
    nonword_regexp = re.compile(r'[^\w]')
    
    value = value.replace('_', ' ')
    value = value.title()
    value = re.sub(nonword_regexp, '', value)
    value = re.sub(whitespace_regexp, '', value)
    if value:
        value = value[0].lower() + value[1:]
        
    return value


@string_formatter('u')
def uppercase(value):
    'Make all characters in value upper case'
    return value.upper()


@string_formatter('l')
def lowercase(value):
    'Make all characters in value lower case'
    return value.lower()


@string_formatter('c')
def capitalize(value):
    '''
    Make the first character of each word in value capitalized and all other 
    characters of a word lower case.
    '''
    return string.capwords(value)

@string_formatter('_')
def underscore(value):
    'Change all white space characters in value to underscore characters'
    regexp = re.compile(r'\s+')
    return re.sub(regexp, '_', value)


@string_formatter('r')
def remove_whitespace(value):
    'Remove all white space characters in value'
    regexp = re.compile(r'\s+')
    return re.sub(regexp, '', value)


@string_formatter('t')
def default_user_translator(value):
    '''
    Default user supplied translate format function. No translation is made.
    Generally, this rule is overridden by a user.
    '''
    return value


@string_formatter('tnosplat')
def remove_splat(value):
    '''
    Removes *'s (splats). This can be used to remove the * character found
    in polymorphic events expressed in the BridgePoint meta model.
    '''
    return value.replace('*', '')


@string_formatter('t2tick')
def escape_single_quote(value):
    'Replace all occurrences of a single quote with two single quotes'
    return value.replace("'", "''")


@string_formatter('tnonl')
def linebreak_to_space(value):
    'Replace all occurrences of a line break with a white space'
    return value.replace('\n', ' ')


@string_formatter('tu2d')
def underscore_to_dash(value):
    'Replace all occurrences of an underscore with a dash'
    return value.replace('_', '-')


@string_formatter('td2u')
def dash_to_underscore(value):
    'Replace all occurrences of a dash with an underscore'
    return value.replace('-', '_')


@string_formatter('tstrsep_')
def remove_underscore_suffix(value):
    'Remove all characters following an underscore'
    return value.split('_', 1)[0]


@string_formatter('t_strsep')
def remove_underscore_prefix(value):
    'Remove all characters preceding an underscore'
    try:
        return value.split('_', 1)[1]
    except IndexError:
        return ''


@string_formatter('txmlclean')
def xml_clean(value):
    'Replace reserved XML characters with XML entities'
    return (value.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))


@string_formatter('txmlquot')
def xml_quot(value):
    'Add quotes to a string intended to be used as an xml attribute'
    if "'" in value:
        return '"%s"' % value
    else:
        return "'%s'" % value


@string_formatter('txmlname')
def xml_name(value):
    'Replace illegal characters in an XML name with an underscore'
    regexp = re.compile(r'(^[^\w_])|[^\w_.-]')
    return re.sub(regexp, '_', value)


class NavigationParser(StringFormatter):
    '''
    Decorator for adding navigation formatters to the Runtime class.
    '''
    regexp = re.compile(r"(\s*->\s*([\w]+)\[[Rr](\d+)(?:\.\'([^\']+)\')?\]\s*)") 
    
    def parse_string(self, f, value):
        result = self.regexp.search(value)
        if result:
            return f(result) or ''
        else:
            return ''
    
    def __call__(self, f):
        f = partial(self.parse_string, f)
        return string_formatter.__call__(self, f)

navigation_parser = NavigationParser


@navigation_parser('tcf_kl')
def first_key_letter(result):
    'Get the first key letter in a navigation'
    return result.group(2)


@navigation_parser('tcf_rel')
def first_association_id(result):
    'Get the first association id in a navigation'
    return result.group(3)


@navigation_parser('tcf_phrase')
def first_phrase(result):
    'Get the first phrase in a navigation'
    return result.group(4)


@navigation_parser('tcf_rest')
def remove_first_navigation_step(result):
    'Remove the first step in a navigation'
    return result.string[result.end():]


class BackwardNavigationParser(NavigationParser):
    '''
    Decorator for adding navigation formatters to the Runtime class.
    The parsing is done backwards, i.e. from right to left.
    '''
    regexp = re.compile(r"(\s*->\s*([\w]+)\[[Rr](\d+)(?:\.\'([^\']+)\')?\]\s*)$")
    
backward_navigation_parser = BackwardNavigationParser


@backward_navigation_parser('tcb_kl')
def last_key_letter(result):
    'Get the last key letter in a navigation'
    return result.group(2)


@backward_navigation_parser('tcb_rel')
def last_association_id(result):
    'Get the last association id in a navigation'
    return result.group(3)


@backward_navigation_parser('tcb_phrase')
def last_phrase(result):
    'Get the last phrase in a navigation'
    return result.group(4)


@backward_navigation_parser('tcb_rest')
def remove_last_navigation_step(result):
    'Remove the last step in a navigation'
    return result.string[:result.start(1)]


