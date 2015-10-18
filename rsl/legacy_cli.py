#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Legacy cli option parser from old gen_erate.exe
'''

import sys
import logging
import os
import xtuml

import rsl.version
 

complete_usage = '''
USAGE: 

   %s  [-arch <string>] ...  [-import <string>] ...  [-d <integer>] ...  [-priority <integer>] [-lVHs] [-lSCs] [-l2b] [-l2s] [-l3b] [-l3s] [-nopersist] [-e <string>] [-t <string>] [-v <string>] [-q] [-l] [-f <string>] [-# <integer>] [//] [-version] [-h]


Where: 

   -arch <string>  (accepted multiple times)
     (value required)  Archetype file name(s)

   -import <string>  (accepted multiple times)
     (value required)  Data file name(s)

   -d <integer>  (accepted multiple times)
     (value required)  The domain code.  This argument must immediately precede the "-import" argument that it applies to.

   -priority <integer>
     (value required)  Set process priority.  Acceptable values are:

             NORMAL_PRIORITY_CLASS = 32

             IDLE_PRIORITY_CLASS = 64

             HIGH_PRIORITY_CLASS = 128

             REALTIME_PRIORITY_CLASS = 256

             BELOW_NORMAL_PRIORITY_CLASS = 16384 (default)

             ABOVE_NORMAL_PRIORITY_CLASS =
     32768


   -lVHs
     Use VHDL source license

   -lSCs
     Use SystemC source license

   -l2b
     Use MC-2020 binary license

   -l2s
     Use MC-2020 source license

   -l3b
     Use MC-3020 binary license

   -l3s
     Use MC-3020 source license

   -nopersist
     Disable persistence

   -e <string>
     (value required)  Enable specified feature

   -t <string>
     (value required)  Full-blast logging

   -v <string>
     (value required)  Verbose mode (STMT, COMP, or SYS)

   -q
     Quit on error

   -l
     Use log file

   -f <string>
     (value required)  Generated file name (database)

   -# <integer>
     (value required)  Number of files to generate

   //,  -ignore_rest
     Ignores the rest of the labeled arguments following this flag.

   -version
     Displays version information and exits.

   -h
     Displays usage information and exits.


   gen_erate
'''

brief_usage = '''
Brief USAGE: 
   %s  [-arch <string>] ...  [-import <string>] ...  [-d <integer>] ...  [-priority <integer>] [-lVHs] [-lSCs] [-l2b] [-l2s] [-l3b] [-l3s] [-nopersist] [-e <string>] [-t <string>] [-v <string>] [-q] [-l] [-f <string>] [-# <integer>] [//] [-version] [-h]

For complete USAGE and HELP type: 
   %s -h
'''


def main():
    loglevel = 2
    database_filename = 'mcdbms.gen'
    enable_persistance = True
    inputs = list()
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-arch':
            i += 1
            inputs.append((sys.argv[i], 'arc'))

        elif sys.argv[i] == '-import':
            i += 1
            inputs.append((sys.argv[i], 'sql'))

        elif sys.argv[i] == '-f':
            i += 1
            database_filename = sys.argv[i]
            
        elif sys.argv[i] == '-nopersist':
            enable_persistance = False
            
        elif sys.argv[i] == '-v':
            loglevel = max(loglevel, 3)
            
        elif sys.argv[i] == '-version':
            print(rsl.version.complete_string)
            sys.exit(0)
            
        elif sys.argv[i] == '-h':
            print(complete_usage % sys.argv[0])
            sys.exit(0)
            
        elif sys.argv[i] in ['//', '-ignore_rest']:
            break

        # ignore these options
        elif sys.argv[i] in ['-lVHs', '-lSCs', '-l2b', '-l2s', '-l3b', '-l3s',
                             '-nopersist', '-q', '-l']:
            pass
            
        # ignore these options (which expects a following value)
        elif sys.argv[i] in ['-d', '-priority', '-e', '-t', '-t', '-f', '#']:
            i += 1
            
        else:
            print("PARSE ERROR: Argument: %s" % sys.argv[i])
            print("Couldn't find match for argument")
            print(brief_usage % (sys.argv[0], sys.argv[0]))
            sys.exit(1)
            
        i += 1
        
    levels = {
              0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG,
    }
    logging.basicConfig(stream=sys.stdout, level=levels.get(loglevel, logging.DEBUG))
    
    id_generator = xtuml.IntegerGenerator()
    metamodel = xtuml.MetaModel(id_generator)
    
    if enable_persistance and os.path.isfile(database_filename):
        loader = xtuml.ModelLoader()
        loader.filename_input(database_filename)
        loader.populate(metamodel)
        
    for filename, kind in inputs:
        if kind == 'sql':
            loader = xtuml.ModelLoader()
            loader.filename_input(filename)
            loader.populate(metamodel)
        
        elif kind == 'arc':
            rt = rsl.Runtime(metamodel, emit='change')
            ast = rsl.parse_file(filename)
            rsl.evaluate(rt, ast, ['.'])
            
        else:
            #should not happen
            print("Unknown %s is of unknown kind '%s', skipping it" % (filename, kind))
        
    if enable_persistance:
        xtuml.persist_database(metamodel, database_filename)


if __name__ == '__main__':
    main()

