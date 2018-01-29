#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import division
from __future__ import print_function

'''
Parallel tools
==============
'''

from multiprocessing import Process, Pipe, cpu_count, Pool
import traceback, warnings
import sys
import signal
import threading
import functools

import inspect
import neurotools_partial.jobs.decorator
import neurotools_partial.jobs.closure

import numpy as np

if sys.version_info<(3,0):
    from itertools import imap as map

__N_CPU__ = cpu_count()

reference_globals = globals()

def parmap(f,problems,leavefree=1,debug=False,verbose=False,show_progress=1):
    '''
    Parallel implmenetation of map using multiprocessing

    Parameters
    ----------
    f : function to apply, takes one argument and returns a tuple
        (i,result) where i is the index into the problems
    problems : list of arguments to f to evaulate in parallel
    leavefree : number of cores to leave open
    debug : if True, will run on a single core so exceptions get 
            handeled correctly
    verbose : set to True to print out detailed logging information
    
    Returns
    -------
    list of results
    '''
    global mypool
    problems = list(problems)
    njobs    = len(problems)

    if njobs==0:
        if verbose: 
            print('NOTHING TO DO?')
        return []

    if not debug and (not 'mypool' in globals() or mypool is None):
        if verbose: 
            print('NO POOL FOUND. RESTARTING.')
        mypool = Pool(cpu_count()-leavefree)

    enumerator = map(f,problems) if debug else mypool.imap(f,problems)
    results = {}
    if show_progress:
        sys.stdout.write('\n')
    lastprogress = 0.0
    for i,result in enumerator:
        if show_progress:
            thisprogress = ((i+1)*100./njobs)
            if (thisprogress - lastprogress)>0.5:
                sys.stdout.write('\rdone %0.1f%% '%thisprogress)
                sys.stdout.flush()
                lastprogress = thisprogress
        # if it is a one element tuple, unpack it automatically
        if isinstance(result,tuple) and len(result)==1:
            result=result[0]
        results[i]=result
        if verbose and type(result) is RuntimeError:
            print('ERROR PROCESSING',problems[i])
    if show_progress:
        sys.stdout.write('\r            \r')
    return [results[i] if i in results else None \
        for i,k in enumerate(problems)]

def pararraymap(function,problems,debug=False):
    '''
    Parmap wrapper for common use-case with Numpy
    '''
    # Ensures that all workers can see the newly-defined helper function
    reset_pool()
    return np.array(parmap(function,enumerate(problems),debug=debug))

def reset_pool(leavefree=1,context=None,verbose=False):
    '''
    Safely halts and restarts the worker-pool. If worker threads are stuck, 
    then this function will hang. On the other hand, it avoids doing 
    anything violent to close workers. 
    
    Other Parameters
    ----------------
    leavefree : `int`, default 1
        How many cores to "leave free"; The pool size will be the number of
        system cores minus this value
    context : python context, default None
        This context will be used for all workers in the pool
    verbose : `bool`, default False
        Whether to print logging information.
    '''
    global mypool, reference_globals

    # try to see what the calling function sees
    if not context is None:
        reference_globals = context

    if not 'mypool' in globals() or mypool is None:
        if verbose:
            print('NO POOL FOUND. STARTING')
        mypool = Pool(cpu_count()-leavefree)
    else:
        if verbose:
            print('POOL FOUND. RESTARTING')
            print('Attempting to terminate pool, may become unresponsive')
        # http://stackoverflow.com/questions/16401031/python-multiprocessing-pool-terminate
        def close_pool():
            global mypool
            if not 'mypool' in globals() or mypool is None:
                return
            mypool.close()
            mypool.terminate()
            mypool.join()
        def term(*args,**kwargs):
            sys.stderr.write('\nStopping...')
            stoppool=threading.Thread(target=close_pool)
            stoppool.daemon=True
            stoppool.start()
        signal.signal(signal.SIGTERM, term)
        signal.signal(signal.SIGINT,  term)
        signal.signal(signal.SIGQUIT, term)
        del mypool
        mypool = Pool(cpu_count()-leavefree)

def parallel_error_handling(f):
    '''
    A wrapper to catch and print errors within workers.
    '''
    def parallel_helper(args):
        try:
            return f(*args)
        except Exception as exc:
            traceback.print_exc()
            info = traceback.format_exc()
            return RuntimeError(info, exc)
    return parallel_helper
