# encoding: utf-8
# Copyright (C) 2015-2016 John Törnblom
'''
Simple linter for the rule-specification language (RSL).
'''
import optparse
import logging
import sys

import xtuml
import rsl


logger = logging.getLogger('rsl.lint')


class Linter(xtuml.Visitor):

    def __init__(self, metamodel):
        self.m = metamodel
        self.functions = dict()
        
    def warn(self, node, msg):
        logger.warning('%s:%s:%s' % (node.filename, node.lineno, msg))

    def enter_FunctionNode(self, node):
        if node.name in self.functions:
            self.warn(node, 'redefinition of function %s' % node.name)
        else:
            self.functions[node.name] = node

    def enter_CreateNode(self, node):
        try:
            self.m.find_metaclass(node.key_letter)
        except xtuml.UnknownClassException as e:
            self.warn(node, 'Undefined class %s' % node.key_letter)
                    
    def enter_SelectAnyInstanceNode(self, node):
        try:
            self.m.find_metaclass(node.key_letter)
        except xtuml.UnknownClassException as e:
            self.warn(node, 'Undefined class %s' % node.key_letter)
            
    def enter_SelectManyInstanceNode(self, node):
        try:
            self.m.find_metaclass(node.key_letter)
        except xtuml.UnknownClassException as e:
            self.warn(node, 'Undefined class %s' % node.key_letter)

    def enter_NavigationNode(self, node):
        try:
            self.m.find_metaclass(node.key_letter)
        except xtuml.UnknownClassException as e:
            self.warn(node, 'Undefined class %s' % node.key_letter)

    
def lint_file(metamodel, filename):
    root = rsl.parse.parse_file(filename)
    w = xtuml.Walker()
    #w.visitors.append(xtuml.NodePrintVisitor())
    w.visitors.append(Linter(metamodel))
    w.accept(root)


    
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

    m = xtuml.load_metamodel(opts.imports)
    for filename in args:
        lint_file(m, filename)


if __name__ == '__main__':
    main()
