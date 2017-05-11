#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2015 John Törnblom
'''
rule-specification language (RSL) interpreter.
'''

import sys
import logging
import os
import xtuml

import rsl.version
 

complete_usage = '''
USAGE: 

   %s  [-arch <string>] ... [-import <string>] ... [-include <string>] ... [-d <integer>] ... [-diff <string>] [-emit <string>] [-priority <integer>] [-lVHs] [-lSCs] [-l2b] [-l2s] [-l3b] [-l3s] [-nopersist] [-force] [-integrity] [-e <string>] [-t <string>] [-v <string>] [-qim] [-q] [-l] [-f <string>] [-# <integer>] [//] [-version] [-h]


Where: 

   -arch <string>  (accepted multiple times)
     (value required)  Archetype file name(s)

   -import <string>  (accepted multiple times)
     (value required)  Data file name(s)

   -include <string>  (accepted multiple times)
     (value required) add a path to list of dirs to search for include files

   -d <integer>  (accepted multiple times)
     (value required)  The domain code.  This argument must immediately precede the "-import" argument that it applies to.

   -diff <string>
     (value required)  save a diff of all emits to a filename

   -priority <integer>
     (value required)  Set process priority.  Acceptable values are:

             NORMAL_PRIORITY_CLASS = 32

             IDLE_PRIORITY_CLASS = 64

             HIGH_PRIORITY_CLASS = 128

             REALTIME_PRIORITY_CLASS = 256

             BELOW_NORMAL_PRIORITY_CLASS = 16384 (default)

             ABOVE_NORMAL_PRIORITY_CLASS =
     32768

   -emit <string>
     (value required) Chose when to emit. Acceptable values are:

             never = never emit to disk

             change = only emit to disk when files differ (default)

             always = always emit to disk, even when the content in memory is the same as the content on disk

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

   -force
     make read-only emit files writable

    -integrity
     check the model for integrity violations upon program exit

   -e <string>
     (value required)  Enable specified feature

   -t <string>
     (value required)  Full-blast logging

   -v <string>
     (value required)  Verbose mode (STMT, COMP, or SYS)

   -qim
     Quiet insert mismatches. Do not print warnings if insert data doesn't populate all attributes.

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
   %s  [-arch <string>] ... [-import <string>] ... [-include <string>] ... [-d <integer>] ... [-diff <string>] [-emit <string>] [-priority <integer>] [-lVHs] [-lSCs] [-l2b] [-l2s] [-l3b] [-l3s] [-nopersist] [-force] [-integrity] [-e <string>] [-t <string>] [-v <string>] [-qim] [-q] [-l] [-f <string>] [-# <integer>] [//] [-version] [-h]

For complete USAGE and HELP type: 
   %s -h
'''


def main(argv=None):
    loglevel = logging.INFO
    database_filename = 'mcdbms.gen'
    enable_persistance = True
    force_overwrite = False
    emit_when = 'change'
    diff_filename = None
    inputs = list()
    includes = ['.']
    check_integrity = False
    argv = argv or sys.argv
    quiet_insert_mismatch = False
    
    i = 1
    while i < len(argv):
        if argv[i] == '-arch':
            i += 1
            inputs.append((argv[i], 'arc'))

        elif argv[i] == '-import':
            i += 1
            inputs.append((argv[i], 'sql'))

        elif argv[i] == '-include':
            i += 1
            includes.append(argv[i])

        elif argv[i] == '-emit':
            i += 1
            emit_when = argv[i]
    
        elif argv[i] == '-f':
            i += 1
            database_filename = argv[i]

        elif argv[i] == '-force':
            force_overwrite = True

        elif argv[i] == '-integrity':
            check_integrity = True
            
        elif argv[i] == '-diff':
            i += 1
            diff_filename = argv[i]
            
        elif argv[i] == '-nopersist':
            enable_persistance = False
            
        elif argv[i] == '-v':
            i += 1
            loglevel = logging.DEBUG
            
        elif argv[i] == '-qim':
            quiet_insert_mismatch = True
            
        elif argv[i] == '-version':
            print(rsl.version.complete_string)
            sys.exit(0)
            
        elif argv[i] == '-h':
            print(complete_usage % argv[0])
            sys.exit(0)
            
        elif argv[i] in ['//', '-ignore_rest']:
            break

        # ignore these options
        elif argv[i] in ['-lVHs', '-lSCs', '-l2b', '-l2s', '-l3b', '-l3s',
                             '-q', '-l']:
            pass
            
        # ignore these options (which expects a following value)
        elif argv[i] in ['-d', '-priority', '-e', '-t', '-#']:
            i += 1
            
        else:
            print("PARSE ERROR: Argument: %s" % argv[i])
            print("Couldn't find match for argument")
            print(brief_usage % (argv[0], argv[0]))
            sys.exit(1)
            
        i += 1
        
    logging.basicConfig(stream=sys.stdout, level=loglevel)
    
    id_generator = xtuml.IntegerGenerator()
    metamodel = xtuml.MetaModel(id_generator)
    loader = xtuml.ModelLoader()
    
    if quiet_insert_mismatch:
        load_logger = logging.getLogger(xtuml.load.__name__)
        load_logger.setLevel(logging.ERROR)

    if diff_filename:
        with open(diff_filename, 'w') as f:
            f.write(' '.join(argv))
            f.write('\n')
            
    if enable_persistance and os.path.isfile(database_filename):
        loader.filename_input(database_filename)
        
    for filename, kind in inputs:
        if kind == 'sql':
            loader.filename_input(filename)
            
        elif kind == 'arc':
            loader.populate(metamodel)
            rt = rsl.Runtime(metamodel, emit_when, force_overwrite, diff_filename)
            ast = rsl.parse_file(filename)
            rsl.evaluate(rt, ast, includes)
            loader = xtuml.ModelLoader()
            
        else:
            #should not happen
            print("Unknown %s is of unknown kind '%s', skipping it" % (filename, kind))

    errors = 0
    if check_integrity:
        errors += xtuml.check_association_integrity(metamodel)
        errors += xtuml.check_uniqueness_constraint(metamodel)
        
    if enable_persistance:
        xtuml.persist_database(metamodel, database_filename)

    return errors


if __name__ == '__main__':
    num_errors = main()
    sys.exit(num_errors > 0)
