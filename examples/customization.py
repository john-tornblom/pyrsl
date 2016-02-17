# encoding: utf-8
# Copyright (C) 2016 John Törnblom
'''
Example on how to extend the functionallity of rsl.gen_erate by defining custom
bridges and string formatters.
'''
import hashlib
import sys

from rsl import gen_erate
from rsl import bridge
from rsl import string_formatter


@bridge('HASH.MD5')
def hash_md5(s):
    try:
        result = hashlib.md5(s).hexdigest()
        success = True
    except:
        result = ''
        success = False

    return {'success': success,
            'result': result}


@string_formatter('trmquot')
def remove_quot(s):
    QUOTES = "'\""
    first_index = 0
    last_index = len(s) - 1
    
    if s[0] in QUOTES:
        first_index += 1

    if s[-1] in QUOTES:
        last_index +- 1

    return s[first_index:last_index]


print('Running my custom version of gen_erate')
rc = gen_erate.main()
sys.exit(rc)

