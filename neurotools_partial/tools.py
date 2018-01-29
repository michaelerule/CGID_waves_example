#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import division
from __future__ import nested_scopes
from __future__ import generators
from __future__ import unicode_literals
from __future__ import print_function

import neurotools_partial as neurotools

'''
This document has been abridged from the original source
Non-essential functions have been removed
'''

import os
import traceback
import inspect
import numpy as np
import datetime
import time as systime
import sys
from   matplotlib.cbook          import flatten
from   neurotools_partial.jobs.decorator import *
from   scipy.io                  import loadmat

'''
try: 
    # Python 2
    zero_depth_bases = (basestring, Number, xrange, bytearray)
    iteritems = 'iteritems'
except NameError: 
    # Python 3
    zero_depth_bases = (str, bytes, Number, range, bytearray)
    iteritems = 'items'
'''

try:
    from decorator import decorator
    from decorator import decorator as robust_decorator
except Exception as e:
    traceback.print_exc()
    print('Importing decorator failed')
    print('try easy_install decorator')
    print('or  pip  install decorator')

def today():
    '''
    Returns
    -------
    `string` : the date in YYMMDD format
    '''
    return datetime.date.today().strftime('%Y%m%d')
