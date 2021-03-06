#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

__author__ = 'rcoliveira'

class ArgumentValidationError(ValueError):
    '''
    Raised when the type of an argument to a function is not what it should be.
    '''
    def __init__(self, arg_name, func_name, arg_type):
        self.error = 'The argument {0} of {1}() is not a {2}'.format(arg_name, func_name, arg_type)

    def __str__(self):
        return self.error

class InvalidArgumentNumberError(ValueError):
    '''
    Raised when the number of arguments supplied to a function is incorrect.
    Note that this check is only performed from the number of arguments
    specified in the validate_accept() decorator. If the validate_accept()
    call is incorrect, it is possible to have a valid function where this
    will report a false validation.
    '''
    def __init__(self, func_name):
        self.error = 'Invalid number of arguments for {0}()'.format(func_name)

    def __str__(self):
        return self.error

class InvalidReturnType(ValueError):
    '''
    As the name implies, the return value is the wrong type.
    '''
    def __init__(self, return_type, func_name):
        self.error = 'Invalid return type {0} for {1}()'.format(return_type, func_name)

    def __str__(self):
        return self.error

__all__ = [ArgumentValidationError, InvalidArgumentNumberError, InvalidReturnType]
