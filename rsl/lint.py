# encoding: utf-8
# Copyright (C) 2017 John Törnblom
'''
Simple linter for the rule-specification language (RSL).
'''
import optparse
import logging
import sys

import xtuml
import rsl


logger = logging.getLogger('rsl.lint')


def find_link(metaclass, key_letter, rel_id, phrase):
    key_letter = key_letter.upper()
    for link in metaclass.links.values():
        if link.kind.upper() != key_letter:
            continue
        
        if link.rel_id != rel_id:
            continue
    
        if link.phrase == phrase:
            return link


class Linter(xtuml.Visitor):
    count = 0
    
    def __init__(self, metamodel):
        self.m = metamodel
        self.functions = dict()
        self.count = 0
        
    def warn(self, node, msg):
        self.count += 1
        logger.warning('%s:%s:%s' % (node.filename, node.lineno, msg))

    def check_key_letter(self, node, key_letter):
        try:
            cls = self.m.find_metaclass(key_letter)
            if cls.kind != key_letter:
                self.warn(node, 'Key letter case mismatch (%s != %s)' % (key_letter, cls.kind))
            
        except xtuml.UnknownClassException as e:
            self.warn(node, 'Undefined class %s' % key_letter)
            
    def enter_FunctionNode(self, node):
        if node.name in self.functions:
            self.warn(node, 'redefinition of function %s' % node.name)
        else:
            self.functions[node.name] = node

    def enter_CreateNode(self, node):
        self.check_key_letter(node, node.key_letter)
                    
    def enter_SelectAnyInstanceNode(self, node):
        self.check_key_letter(node, node.key_letter)
            
    def enter_SelectManyInstanceNode(self, node):
        self.check_key_letter(node, node.key_letter)
        
    def enter_NavigationNode(self, node):
        self.check_key_letter(node, node.key_letter)

    def enter_InstanceChainNode(self, node):
        prev = None
        for nav in node.navigations:
            if not prev:
                prev = nav
                continue

            try:
                metaclass = self.m.find_metaclass(prev.key_letter)
            except xtuml.UnknownClassException as e:
                continue
                
            link = find_link(metaclass, nav.key_letter, nav.relation.rel_id,
                             nav.relation.phrase)
            
            if link is None:
                if nav.relation.phrase:
                    phrase = ".'%s'" % nav.relation.phrase
                else:
                    phrase = ''
                    
                self.warn(node, "Undefined association %s->%s[%s%s]"
                          % (prev.key_letter, nav.key_letter,
                             nav.relation.rel_id, phrase))

            prev = nav

            
def lint_ast(metamodel, root):
    w = xtuml.Walker()
    l = Linter(metamodel)
    #w.visitors.append(xtuml.NodePrintVisitor())
    w.visitors.append(l)
    w.accept(root)

    return l.count


def main():
    '''
    Parse command line options and launch the RSL linter.
    '''
    parser = optparse.OptionParser(usage="%prog [options] script.arc [another_script.arc]",
                                   version=rsl.version.complete_string,
                                   formatter=optparse.TitledHelpFormatter())
    
    parser.add_option("-i", "--import", dest="imports", metavar="PATH", action="append",
                      default=[], help="import model information from PATH", )
    
    parser.add_option("-I", "--include", dest="includes", metavar="PATH", action="append",
                      default=['./'], help="add PATH to list of dirs to search for include files")
    
    parser.add_option("-v", "--verbosity", dest='verbosity', action="count", default=1,
                      help="increase debug logging level")
    
    (opts, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
        
    levels = {
              0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG,
    }
    logging.basicConfig(level=levels.get(opts.verbosity, logging.DEBUG))

    rc = 0
    m = xtuml.load_metamodel(opts.imports)
    for filename in args:
        root = rsl.parse_file(filename)
        rc |= lint_ast(m, root)

    return rc

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
