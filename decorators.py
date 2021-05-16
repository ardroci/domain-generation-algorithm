#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import functools
import datetime
import sys
import logging
from exceptions import ArgumentValidationError, InvalidArgumentNumberError

__author__ = 'rcoliveira'

_logger = logging.getLogger(__name__)

def test_range(**argchecks):                # validate ranges for both+defaults
    def onDecorator(func):                  # onCall remembers func and argchecks
        if not __debug__:                   # True if "python -O main.py args.."
            return func                     # wrap if debugging else use original
        else:
            code = func.__code__ if sys.version_info[0] == 3 else func.func_code
            allargs  = code.co_varnames[:code.co_argcount]
            funcname = func.__name__
            
            @functools.wraps(func)
            def onCall(*pargs, **kargs):
                # all pargs match first N args by position
                # the rest must be in kargs or omitted defaults
                positionals = list(allargs)
                positionals = positionals[:len(pargs)]

                for (argname, (low, high)) in argchecks.items():
                    # for all args to be checked
                    if argname in kargs:
                        # was passed by name
                        if kargs[argname] < low or kargs[argname] > high:
                            errmsg = '{0} argument "{1}" not in {2}..{3}'
                            errmsg = errmsg.format(funcname, argname, low, high)
                            raise TypeError(errmsg)

                    elif argname in positionals:
                        # was passed by position
                        position = positionals.index(argname)
                        if pargs[position] < low or pargs[position] > high:
                            errmsg = '{0} argument "{1}" not in {2}..{3}'
                            errmsg = errmsg.format(funcname, argname, low, high)
                            raise TypeError(errmsg)
                    else:
                        # default value used -> this migth not be true
                        # read https://learning-python.com/rangetest.html for more detail
                        _logger.info('Argument "{0}" defaulted'.format(argname))
                return func(*pargs, **kargs)
            return onCall
    return onDecorator

def test_type(**argchecks):                 # validate ranges for both+defaults
    def onDecorator(func):                  # onCall remembers func and argchecks
        if not __debug__:                   # True if "python -O main.py args.."
            return func                     # wrap if debugging else use original
        else:
            import sys
            code = func.__code__ if sys.version_info[0] == 3 else func.func_code
            allargs  = code.co_varnames[:code.co_argcount]
            funcname = func.__name__
            
            #@functools.wraps(func)
            def onCall(*pargs, **kargs):
                # all pargs match first N args by position
                # the rest must be in kargs or omitted(defaults)
                positionals = list(allargs)
                positionals = positionals[:len(pargs)]

                # for all args to be checked
                for (argname, arg_type) in argchecks.items():
                    # was passed by name
                    if argname in kargs:
                        if not type(kargs[argname]) is arg_type:
                            raise ArgumentValidationError(argname, funcname, arg_type)
                    # was passed by position
                    elif argname in positionals:
                        position = positionals.index(argname)
                        if not type(pargs[position]) is arg_type:
                            raise ArgumentValidationError(argname, funcname, arg_type)
                    # default value used -> this migth not be true
                    # read https://learning-python.com/rangetest.html for more detail
                    else:
                        # default value used -> this migth not be true
                        # read https://learning-python.com/rangetest.html for more detail
                        _logger.info('Argument "{0}" defaulted'.format(argname))
                return func(*pargs, **kargs)
            return onCall
    return onDecorator

def time_this(original_function):
    def new_function(*args,**kwargs):
        before = datetime.datetime.now()
        x = original_function(*args,**kwargs)
        after = datetime.datetime.now()
        print("Elapsed Time = {0}".format(after-before))
        return x
    return new_function

__all__ = [test_range, test_type, time_this]
