#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
Legacy cli option parser from old gen_erate.exe
'''

import sys
import os
import logging

import xtuml

import rsl.version


current_id = 0
def next_id():
    '''
    Use integers as unique_id
    '''
    global current_id
    current_id += 1
    return current_id
    

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
    archetypes = list()
    imports = list()
    loglevel = 2
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-arch':
            i += 1
            archetypes.append(sys.argv[i])

        elif sys.argv[i] == '-import':
            i += 1
            imports.append(sys.argv[i])

        elif sys.argv[i] == '-v':
            loglevel = max(loglevel, 3)
                    
        elif sys.argv[i] == '-f':
            i += 1
            
        elif sys.argv[i] == '-version':
            print(rsl.version.complete_string)
            sys.exit(0)
            
        elif sys.argv[i] == '-h':
            print(complete_usage % sys.argv[0])
            sys.exit(0)
            
        elif sys.argv[i] in ['//', '-ignore_rest']:
            break
            
        # ignore these options
        elif sys.argv[i] in ['-d', '-priority', '-lVHs', '-lSCs', '-l2b',
                             '-l2s', '-l3b', '-l3s', '-e', '-q', '-#', '-t',
                             '-l','-nopersist', ]:
            i += 1

        else:
            print("PARSE ERROR: Argument: %s" % sys.argv[i])
            print("Couldn't find match for argument")
            print(brief_usage % (sys.argv[0], sys.argv[0]))
            sys.exit(1)
            
        i += 1

    if len(archetypes) == 0:
        print(complete_usage % sys.argv[0])
        sys.exit(1)
        
    levels = {
              0: logging.ERROR,
              1: logging.WARNING,
              2: logging.INFO,
              3: logging.DEBUG,
    }
    logging.basicConfig(stream=sys.stdout, level=levels.get(loglevel, logging.DEBUG))
    
    loader = xtuml.load.ModelLoader()
    loader.build_parser()

    for filename in imports:
        loader.filename_input(filename)

    id_generator = xtuml.IdGenerator(next_id)
    metamodel = loader.build_metamodel(id_generator)
    
    rt = rsl.Runtime(metamodel, emit='change')
    for archetype in archetypes:
        ast = rsl.parse_file(archetype)
        rsl.evaluate(rt, ast, ['.'])
        

if __name__ == '__main__':
    main()

