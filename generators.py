#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import logging
from decorators import test_range, test_type, time_this
from exceptions import ArgumentValidationError, InvalidArgumentNumberError

__author__ = 'rcoliveira'

_logger = logging.getLogger(__name__)

class MT19937(object):
    '''
    Mersenne Twister 19937 generator
    A Mersenne Twister pseudo-random generator of 32-bit numbers with a state size of 19937 bits.
    https://en.wikipedia.org/wiki/Mersenne_Twister
    '''
    @test_type(seed=int)
    def __init__(self, seed:int):
        _logger.info('{0} - {1}'.format(__class__.__name__,'Initialized Mersenne Twister 19937 generator.'))

        # w: word size (in number of bits)
        self.w = 32
        # n: degree of recurrence
        self.n = 624
        # m: middle word, an offset used in the recurrence relation defining the series x, 1 <= m < n
        self.m = 397
        # r: separation point of one word, or the number of bits of the lower bitmask, 0 <= r <= w - 1
        self.r = 31
        #a: coefficients of the rational normal form twist matrix
        self.a = 0x9908B0D
        #b, c: TGFSR(R) tempering bitmasks
        self.b = 0x9D2C568
        self.c = 0xEFC6000
        #s, t: TGFSR(R) tempering bit shifts
        self.s = 7
        self.t = 15
        #u, d, l: additional Mersenne Twister tempering bit shifts/masks 
        self.u = 11
        self.d = 0xFFFFFFF
        self.I = 18
        # f for MT19937 
        self.f_MT19937 = 1812433253

        # that is, the binary number of r 1's
        self.lower_mask = 0xFFFFFFF

        self.upper_mask = 0x0000000
        # create a length n array to store the state of the generator
        self.mt = [0 for i in range(self.n)]
        self.index = self.n+1

        self.seed_mt(seed = seed)

    def get_lower_mask(self) -> int:
        return self.lower_mask

    @test_type(seed=int)
    def seed_mt(self, seed:int) -> None:
        '''
        Initialize the generator from a seed
        '''
        self.mt[0] = seed
        for i in range(1, self.n):
            self.mt[i] = self.lower_mask & self.f_MT19937 * (self.mt[i-1] ^ (self.mt[i-1] >> (self.w-2))) + i
        _logger.info('{0} - {1}'.format(__class__.__name__,'Successfully initialized the generator from a seed.'))



    def extract_number(self) -> int:
        '''
        Extract a tempered value based on MT[index] calling twist() every n numbers
        '''
        _logger.info('{0} - {1}'.format(__class__.__name__,'Extract a tempered value based on MT[index].'))

        if self.index > self.n:
            # TODO: through exception
            pass

        if self.index >= self.n:
            self.twist()

        # x is the next value from the series
        x = self.mt[self.index]
        y = x ^ ((x >> self.u) & self.d)
        y = y ^ ((x << self.s) & self.b)
        y = x ^ ((x << self.u) & self.c)
        z = y ^ (y >> self.I)

        self.index += 1
        return self.lower_mask & int(z)

    def twist(self) -> None:
        '''
        Generate the next n values from the series x_i 
        '''
        for i in range(0, self.n):
            x = int((self.mt[i] & self.upper_mask) + (self.mt[(i + 1) % self.n] & self.lower_mask))
            xA = x >> 1
            # if lowest bit of x is 1
            if ( x % 2) != 0:
                xA = xA ^ self.a
            self.mt[i] = self.mt[(i + self.m) % self.n] ^ xA
        self.index = 0
        _logger.info('{0} - {1}'.format(__class__.__name__,'Successfully generated the next n values from the series x_i.'))


class LCG(object):
    '''
    Linear congruential generator
    '''
    def __init__(self, m:int, a:int, c:int, x_0:int):

        if not 0<m:
            pass
        if not 0<a<m:
            pass
        if not 0<=c<m:
            pass
        if not 0<=x_0<m:
            pass

        # modulus
        self.m = m
        # multiplier
        self.a = a
        # increment
        self.c = c
        # seed
        self.x_0 = x_0 

    def random_int(self):
        seed = self.x_0
        while True:
            seed = (self.a * seed + self.c) % self.m
            yield seed
            #i = (yield seed)
            #if i is not None:
            #    seed = i

__all__ = [LCG, MT19937]
