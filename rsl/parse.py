# encoding: utf-8
# Copyright (C) 2015-2017 John Törnblom
'''
Parser for the rule-specification language (RSL). 
Heavily inspired by: 
   - https://github.com/xtuml/mc/blob/master/mcmc/arlan/arlan.l
   - https://github.com/xtuml/mc/blob/master/mcmc/arlan/arlan.y
'''


import os
import logging

from ply import lex
from ply import yacc

from . import ast


logger = logging.getLogger(__name__)


class ParseException(Exception):
    pass


class RSLParser(object):
    
    tokens = ('SELECTONE',
              'SELECTANY',
              'SELECTMANY',
              'CREATEOBJ',
              'DELETEOBJ',
              'RELATE',
              'UNRELATE',
              'ACROSS',
              'FROM',
              'USING',
              'OF',
              'IF',
              'TO',
              'FOR',
              'TYPE',
              'RELATEDBY',
              'ELIF',
              'ENDFOR',
              'FORMAT',
              'FUNCTION',
              'ELSE',
              'BREAKFOR',
              'BAD',
              'PARAM',
              'ENDIF',
              'COMMENT',
              'WHERE',
              'ORDER_BY',
              'REVERSE_ORDER_BY',
              'ENDFUNCTION',
              'FROMINSTOF',
              'TEXT',
              'INCLUDE',
              'ASSIGN',
              'PRINTTOK',
              'EXITTOK',
              'EMIT',
              'CLEARTOK',
              'INVOKE',
              'IN',
              'UOP',
              'RELTRANS',
              'PHRASE',
              'ALXLATE',
              'SPECIALWHERE',
              'WHILE',
              'ENDWHILE',
              'BREAKWHILE',
              'WORD',
              'LITERAL',
              'REALconstant',
              'INTconstant',
              'ARROW',
              'LT',
              'GT',
              'LE',
              'GE',
              'EQEQ',
              'NE',
              'AND',
              'OR',
              'NEWLINE',
              'LPAREN',
              'RPAREN',
              'RCBRAC',
              'LCBRAC',
              'COLON',
              'SEMICOLON',
              'DQUOTE',
              'DOLLAR',
              'PIPE',
              'COMMA',
              'DOT',
              'EQ',
              'UMINUS',
              'SLASH',
              'AMPERSAND',
              'CARET',
              'PROCENT',
              'STAR',
              'PLUS',
              'MINUS',
              'LBRAC',
              'RBRAC')
    
    states = (
       ('literal', 'exclusive'),  # parses literal text (output)
       ('rt', 'exclusive'),  # relationship traversal
       ('psv', 'exclusive'),  # pre-substitution variable (format)
       ('sv', 'inclusive'),  # substitution variable
       ('pc', 'inclusive'),  # pre-control (start of line with control word)
       ('control', 'inclusive'),  # control (action language instruction)
       ('str', 'inclusive'),  # string delimited by quotation marks
    )

    precedence = [('left', 'UOP'),
                  ('left', 'UMINUS')]


    def __init__(self):
        self.filename = ''
        
        self.lexer = lex.lex(debuglog=logger,
                             errorlog=logger,
                             optimize=1,
                             module=self,
                             outputdir=os.path.dirname(__file__),
                             lextab="rsl.__rsl_lextab")
        
        self.parser = yacc.yacc(debuglog=logger,
                                errorlog=logger,
                                optimize=1,
                                module=self,
                                outputdir=os.path.dirname(__file__),
                                tabmodule='rsl.__rsl_parsetab')

    def filename_input(self, filename):
        with open(filename, 'rU') as f:
            return self.text_input(f.read(), filename)
    
    def text_input(self, text, filename=''):
        logger.debug('parsing %s' % filename)
        self.filename = filename
        if not text: text = '\n'
        elif text[-1] != '\n': text += '\n'
        
        return self.parser.parse(lexer=self.lexer, 
                                 input=text,
                                 tracking=1)
    
    def t_literal_INITIAL_pc_control_NEWLINE(self, t):
        r"\n"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.lineno += len(t.value)
        t.lexer.begin('INITIAL')
        return t
    
    def t_LITERAL(self, t):
        r"(?m)^[\s]*(?=\.\.)"
        t.lexer.begin('literal')
        t.lexer.lexpos += 1
        return t
    
    def t_pc(self, t):
        r"(?m)^[\s]*(?=[\.])"
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('pc')
    
    def t_LITERAL_2(self, t):
        r"(?m)^[\s]*(?=[^\.\n])"
        t.lexer.begin('literal')
        t.lexer.lineno += t.value.count('\n')
        t.type = 'LITERAL'
        return t
    
    def t_literal_LITERAL(self, t):
        r"[^\$\n]+|(\$\$)+"
        t.endlexpos = t.lexpos + len(t.value)
        t.value = t.value.replace('$$', '$')
        return t
    
    def t_control_WHITESPACE(self, t):
        r"\s"
        t.endlexpos = t.lexpos + len(t.value)
    
    def t_WHITESPACE(self, t):
        r"\s"
        t.endlexpos = t.lexpos + len(t.value)

    def t_pc_COMMENT(self, t):
        r"(\.//|(?i)\.comment)[^\n]*\n"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        
    def t_control_COMMENT(self, t):
        r"(\.//|(?i)\.comment)[^\n]*\n"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.lineno += t.value.count('\n')
        t.type = 'NEWLINE'
        t.lexer.begin('INITIAL')
        return t

    def t_pc_FUNCTION(self, t):
        r"(?i)\.function"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_PARAM(self, t):
        r"(?i)\.param"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ENDFUNCTION(self, t):
        r"(?i)\.end[\s]+function"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_INVOKE(self, t):
        r"(?i)\.invoke"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_CLEARTOK(self, t):
        r"(?i)\.clear"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_SELECTONE(self, t):
        r"(?i)\.select[\s]+one"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_SELECTANY(self, t):
        r"(?i)\.select[\s]+any"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_SELECTMANY(self, t):
        r"(?i)\.select[\s]+many"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_RELATE(self, t):
        r"(?i)\.relate"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_UNRELATE(self, t):
        r"(?i)\.unrelate"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_IF(self, t):
        r"(?i)\.if"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ELIF(self, t):
        r"(?i)\.elif"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ELSE(self, t):
        r"(?i)\.else"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ENDIF(self, t):
        r"(?i)\.end[\s]+if"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_FOR(self, t):
        r"(?i)\.for[\s]+each"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_BREAKFOR(self, t):
        r"(?i)\.break[\s]+for"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ENDFOR(self, t):
        r"(?i)\.end[\s]+for"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_WHILE(self, t):
        r"(?i)\.while"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_BREAKWHILE(self, t):
        r"(?i)\.break[\s]+while"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ENDWHILE(self, t):
        r"(?i)\.end[\s]+while"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_INCLUDE(self, t):
        r"(?i)\.include"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ASSIGN(self, t):
        r"(?i)\.assign"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_PRINTTOK(self, t):
        r"(?i)\.print"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_EXITTOK(self, t):
        r"(?i)\.exit"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_EMIT(self, t):
        r"(?i)\.emit[\s]+to[\s]+file"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_ALXLATE(self, t):
        r"(?i)\.al_xlate"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_SPECIALWHERE(self, t):
        r"(?i)\.special_where"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_CREATEOBJ(self, t):
        r"(?i)\.create[\s]+object[\s]+instance"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t
    
    def t_pc_DELETEOBJ(self, t):
        r"(?i)\.delete[\s]+object[\s]+instance"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.begin('control')
        return t

    def t_pc_LITERAL(self, t):
        r"\.[^\n]*"
        raise ParseException("invalid control statement at %s:%s" % (self.filename,
                                                                     t.lineno))
    
    def t_control_TO(self, t):
        r"(?i)to(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_ACROSS(self, t):
        r"(?i)across(?=[\s])"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_USING(self, t):
        r"(?i)using(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_WHERE(self, t):
        r"(?i)where(?=[\s\(])"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_ORDER_BY(self, t):
        r"(?i)ordered_by(?=[\s\(])"
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_control_REVERSE_ORDER_BY(self, t):
        r"(?i)reverse_ordered_by(?=[\s\(])"
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_control_RELATEDBY(self, t):
        r"(?i)related[\s]+by(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_FROMINSTOF(self, t):
        r"(?i)from[\s]+instances[\s]+of(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_FROM(self, t):
        r"(?i)from(?=[\s])"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_IN(self, t):
        r"(?i)in(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_OF(self, t):
        r"(?i)of(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_TYPE(self, t):
        r"(?i)(boolean|integer|real|string|unique_id|inst_ref|inst_ref_set|frag_ref)(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_control_TYPE2(self, t):
        r"(?i)(inst_ref|inst_ref_set|frag_ref)(?=<[^>]+>\s)"
        t.endlexpos = t.lexpos + len(t.value)
        t.type = 'TYPE'
        return t
    
    def t_control_AND(self, t):
        r"(?i)and(?=[\s\(])"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_OR(self, t):
        r"(?i)or(?=[\s\(])"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_UOP(self, t):
        r"(?i)(not_empty|not_first|not_last|not|empty|first|last|cardinality)(?=\s)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_REALconstant(self, t):
        r"(((\d*\.\d+)|(\d+\.)([eE][-+]?\d+)?)|(\d+([eE][-+]?\d+)))[FfLl]?"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_INTconstant(self, t):
        r"\d+"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    #<control,str,sv>{word}        {WORD_RETURN(WORD);}
    def t_control_WORD(self, t):
        r"[a-zA-Z][0-9a-zA-Z_]*|[a-zA-Z][0-9a-zA-Z_]*[0-9a-zA-Z_]+"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_str_sv_WORD(self, t):
        r"[a-zA-Z][0-9a-zA-Z_\ ]*[0-9a-zA-Z_]+|[a-zA-Z][0-9a-zA-Z_]*"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_control_DQUOTE(self, t):
        r"\""
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.push_state('str')
        return t
    
    def t_str_TEXT(self, t):
        r"[^\"\$]+|(\"\")+|(\$\$)"
        t.endlexpos = t.lexpos + len(t.value)
        t.value = t.value.replace('""', '"')
        t.value = t.value.replace('$$', '$')
        return t
    
    def t_str_DQUOTE(self, t):
        r"\""
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.pop_state()
        return t
    
    def t_literal_DOLLAR(self, t):
        r"\$"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.push_state('psv')
        return t
    
    def t_DOLLAR(self, t):
        r"\$"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.push_state('psv')
        return t
    
    def t_psv_FORMAT(self, t):
        r"(?i)([oclru_]|t[^\{]*)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_psv_LCBRAC(self, t):
        r"\{"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.pop_state()
        t.lexer.push_state('sv')
        return t
    
    def t_sv_RCBRAC(self, t):
        r"\}"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.pop_state()
        return t
    
    def t_LBRAC(self, t):
        r"\["
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.push_state('rt')
        return t
    
    def t_rt_RELTRANS_1(self, t):
        r"R\d+"
        t.endlexpos = t.lexpos + len(t.value)
        t.type = 'RELTRANS'
        return t
    
    def t_rt_DOT(self, t):
        r"\."
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_rt_RELTRANS_2(self, t):
        r"RI|IR"
        t.endlexpos = t.lexpos + len(t.value)
        t.type = 'RELTRANS'
        return t
    
    def t_rt_PHRASE(self, t):
        r"\'[^\']*\'"
        t.endlexpos = t.lexpos + len(t.value)
        t.value = t.value[1:-1]
        return t
    
    def t_control_PHRASE(self, t):
        r"\'[^\']*\'"
        t.endlexpos = t.lexpos + len(t.value)
        t.value = t.value[1:-1]
        return t
    
    #<rt>{word}           {WORD_RETURN(WORD);}
    def t_rt_WORD(self, t):
        r"[a-zA-Z][0-9a-zA-Z_]*|[a-zA-Z][0-9a-zA-Z_]*[0-9a-zA-Z_]+"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_rt_RBRAC(self, t):
        r"\]"
        t.endlexpos = t.lexpos + len(t.value)
        t.lexer.pop_state()
        return t
    
    def t_ARROW(self, t):
        r"\-\>"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_LE(self, t):
        r"\<\="
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_GE(self, t):
        r"\>\="
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_EQEQ(self, t):
        r"\=\="
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_NE(self, t):
        r"!\="
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_DOT(self, t):
        r"\."
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_COMMA(self, t):
        r","
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_LPAREN(self, t):
        r"\("
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_RPAREN(self, t):
        r"\)"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_LCBRAC(self, t):
        r"\{"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_RCBRAC(self, t):
        r"\}"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_STAR(self, t):
        r"\*"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_PLUS(self, t):
        r"\+"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_MINUS(self, t):
        r"\-"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_PIPE(self, t):
        r"\|"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_SLASH(self, t):
        r"/"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_PROCENT(self, t):
        r"%"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_AMPERSAND(self, t):
        r"\&"
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_CARET(self, t):
        r"\^"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_LT(self, t):
        r"\<"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_GT(self, t):
        r"\>"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_COLON(self, t):
        r":"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_SEMICOLON(self, t):
        r";"
        t.endlexpos = t.lexpos + len(t.value)
        #return t
    
    def t_EQ(self, t):
        r"\="
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_UNDERLINE(self, t):
        r"_"
        t.endlexpos = t.lexpos + len(t.value)
        return t
    
    def t_error(self, t):
        logger.error("%s:%d:illegal character '%s'" % (self.filename,
                                                       t.lineno,
                                                       t.value[0]))
        t.lexer.skip(1)
    
    def t_rt_error(self, t):
        logger.error("%s:%d:illegal character '%s'" % (self.filename,
                                                       t.lineno,
                                                       t.value[0]))
        t.lexer.skip(1)
    
    def t_literal_error(self, t):
        logger.error("%s:%d:illegal character '%s'" % (self.filename,
                                                       t.lineno,
                                                       t.value[0]))
        t.lexer.skip(1)
    
    def t_psv_error(self, t):
        logger.error("%s:%d:illegal character '%s'" % (self.filename,
                                                       t.lineno,
                                                       t.value[0]))
        t.lexer.skip(1)
    
    def p_archetypeprogram_1(self, p):
        """archetypeprogram : archetypebody"""
        p[0] = p[1]
        
    def p_linebreak_1(self, p):
        """lineabreak : NEWLINE"""
        
    def p_archetypebody_1(self, p):
        """archetypebody : code"""
        p[0] = ast.BodyNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_code_1(self, p):
        """code : """
        p[0] = ast.StatementListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_code_2(self, p):
        """code : code statement"""
        p[0] = p[1]
        p[0].statements.append(p[2])
    
    def p_code_4(self, p):
        """code : code literal"""
        p[0] = p[1]
        p[0].statements.append(p[2])
        
    def p_statement_1(self, p):
        """statement : selectstatement lineabreak"""
        p[0] = p[1]
    
    def p_statement_2(self, p):
        """statement : IF condition lineabreak code elifclause elseclause endiffer"""
        p[0] = ast.IfNode(p[2], p[4], p[5], p[6])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_3(self, p):
        """statement : FUNCTION function_identifier lineabreak fparameters fbody ENDFUNCTION lineabreak"""
        p[0] = ast.FunctionNode(p[2], p[4], p[5])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_4(self, p):
        """statement : FOR inst_ref_var IN inst_ref_set_var lineabreak code endforrer"""
        p[0] = ast.ForNode(p[2], p[4], p[6])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_5(self, p):
        """statement : BREAKFOR lineabreak"""
        p[0] = ast.BreakNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_7(self, p):
        """statement : BREAKWHILE lineabreak"""
        p[0] = ast.BreakNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_8(self, p):
        """statement : WHILE condition lineabreak code endwhiler"""
        p[0] = ast.WhileNode(p[2], p[4])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_9(self, p):
        """statement : CLEARTOK lineabreak"""
        p[0] = ast.ClearNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_10(self, p):
        """statement : INCLUDE string lineabreak"""
        p[0] = ast.IncludeNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_11(self, p):
        """statement : PRINTTOK string lineabreak"""
        p[0] = ast.PrintNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_12(self, p):
        """statement : EXITTOK sexpr lineabreak"""
        p[0] = ast.ExitNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_13(self, p):
        """statement : EMIT string lineabreak"""
        p[0] = ast.EmitNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_14(self, p):
        """statement : ASSIGN variable_assignment EQ expr lineabreak"""
        p[0] = ast.AssignNode(p[2], p[4])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_15(self, p):
        """statement : INVOKE function_identifier LPAREN aparameters RPAREN lineabreak"""
        p[0] = ast.InvokeNode(p[2], p[4])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_16(self, p):
        """statement : INVOKE frag_ref_var EQ function_identifier LPAREN aparameters RPAREN lineabreak"""
        p[0] = ast.InvokeNode(p[4], p[6], p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_statement_17(self, p):
        """statement : ALXLATE activity_type inst_ref_var lineabreak"""
        p[0] = ast.AlXlateNode(p[2], p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_statement_18(self, p):
        """statement : SPECIALWHERE WORD WORD lineabreak"""
        # TODO: p_statement_18
    
    def p_statement_19(self, p):
        """statement : CREATEOBJ inst_ref_var OF obj_keyletters lineabreak"""
        p[0] = ast.CreateNode(p[2], p[4])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_delete_statement(self, p):
        """statement : DELETEOBJ inst_ref_var lineabreak"""
        p[0] = ast.DeleteNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_selectstatement_1(self, p):
        """selectstatement : SELECTONE inst_ref_var RELATEDBY inst_chain whereclause"""
        p[0] = ast.SelectOneNode(p[2], p[4], p[5])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_selectstatement_2(self, p):
        """selectstatement : SELECTANY inst_ref_var RELATEDBY inst_chain whereclause"""
        p[0] = ast.SelectAnyNode(p[2], p[4], p[5])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_selectstatement_3(self, p):
        """selectstatement : SELECTMANY inst_ref_set_var RELATEDBY inst_chain whereclause orderby"""
        p[0] = ast.SelectManyNode(p[2], p[4], p[5], p[6])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_selectstatement_4(self, p):
        """selectstatement : SELECTANY inst_ref_var FROMINSTOF obj_keyletters whereclause"""
        p[0] = ast.SelectAnyInstanceNode(p[2], p[4], p[5])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_selectstatement_5(self, p):
        """selectstatement : SELECTMANY inst_ref_set_var FROMINSTOF obj_keyletters whereclause orderby"""
        p[0] = ast.SelectManyInstanceNode(p[2], p[4], p[5], p[6])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_relate_statement_1(self, p):
        """statement : RELATE inst_ref_var TO inst_ref_var ACROSS WORD lineabreak"""
        p[0] = ast.RelateNode(p[2],  p[4], p[6], '')
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_relate_statement_2(self, p):
        """statement : RELATE inst_ref_var TO inst_ref_var ACROSS WORD DOT PHRASE lineabreak"""
        p[0] = ast.RelateNode(p[2], p[4], p[6], p[8])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_relate_using_statement_1(self, p):
        """statement : RELATE inst_ref_var TO inst_ref_var ACROSS WORD USING inst_ref_var lineabreak"""
        p[0] = ast.RelateUsingNode(p[2], p[4], p[6], '', p[8])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_relate_using_statement_2(self, p):
        """statement : RELATE inst_ref_var TO inst_ref_var ACROSS WORD DOT PHRASE USING inst_ref_var lineabreak"""
        p[0] = ast.RelateUsingNode(p[2], p[4], p[6], p[8], p[10])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_unrelate_statement_1(self, p):
        """statement : UNRELATE inst_ref_var FROM inst_ref_var ACROSS WORD lineabreak"""
        p[0] = ast.UnrelateNode(p[2], p[4], p[6], '')
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_unrelate_statement_2(self, p):
        """statement : UNRELATE inst_ref_var FROM inst_ref_var ACROSS WORD DOT PHRASE lineabreak"""
        p[0] = ast.UnrelateNode(p[2], p[4], p[6], p[8])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_unrelate_statement_using_1(self, p):
        """statement : UNRELATE inst_ref_var FROM inst_ref_var ACROSS WORD USING inst_ref_var lineabreak"""
        p[0] = ast.UnrelateUsingNode(p[2], p[4], p[6], '', p[8])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_unrelate_statement_using_2(self, p):
        """statement : UNRELATE inst_ref_var FROM inst_ref_var ACROSS WORD DOT PHRASE USING inst_ref_var lineabreak"""
        p[0] = ast.UnrelateUsingNode(p[2], p[4], p[6], p[8], p[10])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_whereclause_1(self, p):
        """whereclause : """
        p[0] = ast.WhereNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_whereclause_2(self, p):
        """whereclause : WHERE condition"""
        p[0] = ast.WhereNode(p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)

    def p_orderby_1(self, p):
        """orderby : """
        p[0] = ast.OrderByNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_orderby_2(self, p):
        """orderby : ORDER_BY LPAREN orderattrs RPAREN"""
        p[0] = ast.OrderByNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        p[0].attributes += p[3]

    def p_orderby_3(self, p):
        """orderby : REVERSE_ORDER_BY LPAREN orderattrs RPAREN"""
        p[0] = ast.OrderByNode(True)
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        p[0].attributes += p[3]

    def p_orderattrs_1(self, p):
        """orderattrs : WORD """
        p[0] = [p[1]]

    def p_orderattrs_2(self, p):
        """orderattrs : orderattrs COMMA WORD"""
        p[0] = p[1] + [p[3]]
    
    def p_fparameters_1(self, p):
        """fparameters : """
        p[0] = ast.ParameterListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_fparameters_3(self, p):
        """fparameters : fparameters PARAM param_type param_name lineabreak"""
        p[0] = p[1]
        param = ast.ParameterNode(p[3], p[4])
        param.filename = self.filename
        param.lineno = p.lineno(2)
        p[0].parameters.append(param)
    
    def p_param_type_1(self, p):
        '''
        param_type : TYPE
        '''
        p[0] = ast.ParameterTypeNode(p[1])
    
    def p_param_type_2(self, p):
        '''
        param_type : TYPE LT function_identifier GT
        '''
        p[0] = ast.ParameterTypeNode(p[1], p[3])
     
    def p_fbody_0(self, p):
        """fbody : """
        p[0] = ast.StatementListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_fbody_2(self, p):
        """fbody : statement code"""
        p[0] = p[2]
        p[0].statements.insert(0, p[1])
        
    def p_fbody_3(self, p):
        """fbody : literal code"""
        p[0] = p[2]
        p[0].statements.insert(0, p[1])
        
    def p_aparameters_1(self, p):
        """aparameters : """
        p[0] = ast.ArgumentListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_aparameters_2(self, p):
        """aparameters : sexpr aparameters"""
        p[0] = p[2]
        p[0].arguments.append(p[1])
        
    def p_aparameters_3(self, p):
        """aparameters : COMMA sexpr aparameters"""
        p[0] = p[3]
        p[0].arguments.append(p[2])
    
    def p_elifclause_1(self, p):
        """elifclause : """
        p[0] = ast.ElIfListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_elifclause_2(self, p):
        """elifclause : elifclause ELIF condition lineabreak code"""
        p[0] = p[1]
        
        el = ast.ElIfNode(p[3], p[5])
        el.filename = self.filename
        el.lineno = p.lineno(2)
        p[0].elifs.append(el)
    
    def p_elseclause_1(self, p):
        """elseclause : """
        p[0] = ast.StatementListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_elseclause_2(self, p):
        """elseclause : ELSE lineabreak code"""
        p[0] = p[3]
    
    def p_endiffer_1(self, p):
        """endiffer : ENDIF lineabreak"""
    
    def p_endwhiler_1(self, p):
        """endwhiler : ENDWHILE lineabreak"""
    
    def p_endforrer_1(self, p):
        """endforrer : ENDFOR lineabreak"""
    
    def p_condition_1(self, p):
        """condition : LPAREN expr RPAREN"""
        p[0] = p[2]
    
    def p_sexpr_1(self, p):
        """sexpr : UOP term"""
        p[0] = ast.UnaryOpNode(p[1], p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_sexpr_2(self, p):
        """sexpr : MINUS term %prec UMINUS"""
        p[0] = ast.UnaryOpNode(p[1], p[2])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_sexpr_3(self, p):
        """sexpr : term bop expr"""
        p[0] = ast.BinaryOpNode(p[1], p[2], p[3])
        p[0].filename = self.filename
        p[0].lineno = p[1].lineno
        
    def p_sexpr_4(self, p):
        """sexpr : term"""
        p[0] = p[1]
        
    def p_expr_1(self, p):
        """expr : LPAREN expr RPAREN"""
        p[0] = p[2]
    
    def p_expr_2(self, p):
        """expr : UOP LPAREN expr RPAREN"""
        p[0] = ast.UnaryOpNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_expr_3(self, p):
        """expr : LPAREN expr RPAREN bop expr"""
        p[0] = ast.BinaryOpNode(p[2], p[4], p[5])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_expr_4(self, p):
        """expr : sexpr"""
        p[0] = p[1]
        
    def p_term_1(self, p):
        """term : string"""
        p[0] = p[1]
    
    def p_term_2(self, p):
        """term : identifier"""
        p[0] = ast.VariableAccessNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_term_3(self, p):
        """term : substitutionvariable"""
        p[0] = p[1]
    
    def p_term_4(self, p):
        """term : INTconstant"""
        p[0] = ast.IntegerValueNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_term_5(self, p):
        """term : REALconstant"""
        p[0] = ast.RealValueNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_term_6(self, p):
        """term : term ARROW identifier"""
        p[0] = ast.SubstitutionNavigationNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(1)
    
    def p_term_7(self, p):
        """term : term COLON parsekeyword"""
        p[0] = ast.ParseKeywordNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p[1].lineno
    
    def p_term_8(self, p):
        """term : term DOT attribute"""
        p[0] = ast.FieldAccessNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p[1].lineno
    
    def p_reltraversal_1(self, p):
        """reltraversal : RELTRANS"""
        p[0] = ast.RelationNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_reltraversal_2(self, p):
        """reltraversal : RELTRANS DOT PHRASE"""
        p[0] = ast.RelationNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_reltraversal_3(self, p):
        """reltraversal : RELTRANS DOT RELTRANS"""
        # TODO: p_reltraversal_3
        
    def p_attribute_1(self, p):
        """attribute : identifier"""
        p[0] = p[1]
        
    def p_attribute_2(self, p):
        """attribute : keyword"""
        p[0] = p[1]
        
    def p_parsekeyword_1(self, p):
        """parsekeyword : identifier"""
        p[0] = ast.StringValueNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_parsekeyword_2(self, p):
        """parsekeyword : substitutionvariable"""
        p[0] = p[1]
        
    def p_format_1(self, p):
        """format : """
        p[0] = list()
    
    def p_format_2(self, p):
        """format : format FORMAT"""
        p[0] = p[1]
        p[0].append(p[2])
    
    def p_variable_access_1(self, p):
        """variable_access : identifier"""
        p[0] = ast.VariableAccessNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_variable_access_2(self, p):
        """variable_access : identifier DOT attribute"""
        var = ast.VariableAccessNode(p[1])
        var.filename = self.filename
        var.lineno = p.lineno(0)
        
        p[0] = ast.FieldAccessNode(var, p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(3)
    
    def p_variable_access_3(self, p):
        """variable_access : keyword"""
        p[0] = ast.VariableAccessNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_variable_assignment_1(self, p):
        """variable_assignment : identifier"""
        p[0] = ast.VariableAssignmentNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
    
    def p_variable_assignment_2(self, p):
        """variable_assignment : identifier DOT attribute"""
        var = ast.VariableAccessNode(p[1])
        var.filename = self.filename
        var.lineno = p.lineno(0)
        
        p[0] = ast.FieldAssignmentNode(var, p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(3)
    
    def p_variable_assignment_3(self, p):
        """variable_assignment : keyword"""
        p[0] = ast.VariableAssignmentNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_keyword_1(self, p):
        """keyword : UOP"""
        p[0] = p[1]
        
    def p_keyword_2(self, p):
        """keyword : TYPE"""
        p[0] = p[1]
        
    def p_keyword_3(self, p):
        """keyword : WHERE"""
        p[0] = p[1]
        
    def p_keyword_4(self, p):
        """keyword : IN"""
        p[0] = p[1]
         
    def p_keyword_5(self, p):
        """keyword : RELATE"""
        p[0] = p[1]
        
    def p_keyword_6(self, p):
        """keyword : TO"""
        p[0] = p[1]
        
    def p_keyword_7(self, p):
        """keyword : ACROSS"""
        p[0] = p[1]
        
    def p_keyword_8(self, p):
        """keyword : UNRELATE"""
        p[0] = p[1]
        
    def p_keyword_9(self, p):
        """keyword : FROM"""
        p[0] = p[1]
        
    def p_param_name_1(self, p):
        """param_name : WORD"""
        p[0] = p[1]

    def p_param_name_2(self, p):
        """param_name : keyword"""
        p[0] = p[1]
        
    def p_frag_ref_var_1(self, p):
        """frag_ref_var : WORD"""
        p[0] = p[1]
        
    def p_inst_ref_var_1(self, p):
        """inst_ref_var : WORD"""
        p[0] = p[1]
        
    def p_inst_ref_var_2(self, p):
        """inst_ref_var : TYPE"""
        p[0] = p[1]
        
    def p_inst_ref_set_var_1(self, p):
        """inst_ref_set_var : WORD"""
        p[0] = p[1]
    
    def p_inst_chain_1(self, p):
        """inst_chain : variable_access"""
        p[0] = ast.InstanceChainNode(p[1])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_inst_chain_2(self, p):
        """inst_chain : inst_chain ARROW WORD LBRAC reltraversal RBRAC"""
        p[0] = p[1]
        nav = ast.NavigationNode(p[3], p[5])
        nav.filename = self.filename
        nav.lineno = p.lineno(0)
        p[0].navigations.append(nav)
        
    def p_obj_keyletters_1(self, p):
        """obj_keyletters : WORD"""
        p[0] = p[1]
        
    def p_activity_type_1(self, p):
        """activity_type : WORD"""
        p[0] = p[1]
        
    def p_identifier_1(self, p):
        """identifier : WORD"""
        p[0] = p[1]
        
    def p_identifier_2(self, p):
        """identifier : WORD LBRAC reltraversal RBRAC"""
        p[0] = ast.NavigationNode(p[1], p[3])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_function_identifier_1(self, p):
        """function_identifier : WORD"""
        p[0] = p[1]
        
    def p_function_identifier_2(self, p):
        """function_identifier : function_identifier DOT WORD"""
        p[0] = p[1] + p[2] + p[3]
            
    def p_bop_1(self, p):
        """bop : LE"""
        p[0] = p[1]
        
    def p_bop_2(self, p):
        """bop : GE"""
        p[0] = p[1]
        
    def p_bop_3(self, p):
        """bop : EQEQ"""
        p[0] = p[1]
        
    def p_bop_4(self, p):
        """bop : NE"""
        p[0] = p[1]
        
    def p_bop_5(self, p):
        """bop : AND"""
        p[0] = p[1]
        
    def p_bop_6(self, p):
        """bop : OR"""
        p[0] = p[1]
        
    def p_bop_7(self, p):
        """bop : GT"""
        p[0] = p[1]
        
    def p_bop_8(self, p):
        """bop : LT"""
        p[0] = p[1]
        
    def p_bop_9(self, p):
        """bop : PLUS"""
        p[0] = p[1]
        
    def p_bop_10(self, p):
        """bop : MINUS"""
        p[0] = p[1]
        
    def p_bop_11(self, p):
        """bop : STAR"""
        p[0] = p[1]
        
    def p_bop_12(self, p):
        """bop : SLASH"""
        p[0] = p[1]
        
    def p_bop_13(self, p):
        """bop : PIPE"""
        p[0] = p[1]
    
    def p_bop_14(self, p):
        """bop : AMPERSAND"""
        p[0] = p[1]

    def p_bop_15(self, p):
        """bop : PROCENT"""
        p[0] = p[1]
        
    def p_bop_16(self, p):
        """bop : CARET"""
        p[0] = p[1]

    def p_literal_1(self, p):
        """literal : LITERAL literalbody NEWLINE"""
        p[0] = p[2]
        if p[1]:
            lit = ast.LiteralNode(p[1])
            lit.filename = self.filename
            lit.lineno = p.lineno(1)
            p[0].literals.insert(0, lit)
    
    def p_literal_2(self, p):
        """literal : NEWLINE"""
        lit = ast.LiteralNode(p[1])
        lit.filename = self.filename
        lit.lineno = p.lineno(1)
        
        p[0] = ast.LiteralListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(1)
        p[0].literals.insert(0, lit)
    
    def p_literalbody_1(self, p):
        """literalbody : """
        p[0] = ast.LiteralListNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_literalbody_2(self, p):
        """literalbody : literalbody LITERAL"""
        p[0] = p[1]
        if p[2]:
            lit = ast.LiteralNode(p[2])
            lit.filename = self.filename
            lit.lineno = p.lineno(2)
            p[0].literals.append(lit)
        
    def p_literalbody_3(self, p):
        """literalbody : literalbody substitutionvariable"""
        p[0] = p[1]
        p[0].literals.append(p[2])
    
    def p_substitutionvariable_1(self, p):
        """substitutionvariable : DOLLAR format LCBRAC term RCBRAC"""
        p[0] = ast.SubstitutionVariableNode(p[2], p[4])
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_string_1(self, p):
        """string : DQUOTE stringbody DQUOTE"""
        p[0] = p[2]
    
    def p_stringbody_1(self, p):
        """stringbody : """
        p[0] = ast.StringBodyNode()
        p[0].filename = self.filename
        p[0].lineno = p.lineno(0)
        
    def p_stringbody_2(self, p):
        """
        stringbody : stringbody TEXT
                   | stringbody WORD
        """
        s = ast.StringValueNode(p[2])
        s.filename = self.filename
        s.lineno = p.lineno(2)
        p[0] = p[1]
        p[0].values.append(s)
        p[0].filename = self.filename
        p[0].lineno = p[1].lineno
        
    def p_stringbody_4(self, p):
        """stringbody : stringbody substitutionvariable"""
        p[0] = p[1]
        p[0].values.append(p[2])
        
    def p_error(self, p):
        if p:
            raise ParseException("invalid token '%s' at %s:%s" % (p.type, 
                                                                  self.filename,
                                                                  p.lineno))
        else:
            raise ParseException("unknown parsing error in %s" % self.filename)
            
            
def parse_file(filename):
    parser = RSLParser()
    filename = os.path.abspath(filename)
    return parser.filename_input(filename)


def parse_text(text, filename=''):
    parser = RSLParser()
    return parser.text_input(text, filename)


if __name__ == '__main__':
    import sys
    import xtuml
    logging.basicConfig(level=logging.WARN)
    
    print ('Enter the character stream below. Press Ctrl-D to begin parsing.')
    print ('')
    s = sys.stdin.read()
    
    print ('--------- Token Stream ----------')
    parser = RSLParser()
    lexer = lex.lex(module=parser)
    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    print ('--------- Syntax Tree ----------')
    root = parse_text(s)
    w = xtuml.Walker()
    w.visitors.append(xtuml.NodePrintVisitor())
    w.accept(root)

