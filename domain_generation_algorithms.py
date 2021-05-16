#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import binascii
from datetime import datetime
from ctypes import c_uint
import logging
from generators import MT19937, LCG
from decorators import test_range, test_type, time_this
from exceptions import ArgumentValidationError, InvalidArgumentNumberError

__author__ = 'rcoliveira'

_logger = logging.getLogger(__name__)

class CoreBot(object):
    '''
    '''
    @test_type(tld=str, nr_domains=int, year=int, month=int, day=int,
                group=int, seed=int, multiplier=int, increment=int,
                modulus=int, length_lower_bound=int, length_upper_bound=int)
    def __init__(self,  tld:str = 'com', nr_domains:int = 5000, year:int=datetime.now().year,
                month:int=datetime.now().month, day:int=datetime.now().day, group:int=1,
                seed:int=0x1DB98930, multiplier:int=1664525, increment:int=1013904223,
                modulus:int=2**32, length_lower_bound:int=0xC, length_upper_bound:int=0x18,
                ):
        self.tld = tld
        self.nr_domains = nr_domains
        self.year = year
        self.month = month
        self.day = day
        self.group = group
        # r: this is the random number, initialized to the hardcoded seed 1DB98930.
        # Other samples of CoreBot use a different hardcoded seeds, see Section Samples in the Wild.
        self.seed = seed
        self.multiplier = multiplier
        self.increment = increment
        self.modulus = modulus
        # len_l: this is the inclusive lower bound on the length of the subdomains of ddns.net.
        self.length_lower_bound = length_lower_bound
        #len_u: this is the exclusive upper bound on the length of the subdomains of ddns.net
        self.length_upper_bound = length_upper_bound

    def __date_to_seed(self):
        '''
        The DGA is time dependent. The time is determined by making an HTTP request to www.google.com
        and querying the date and time with the WinHTTP function WinHttpQueryHeaders.

        Apart from the year, month, and day (set to 8), there is a fourth value used for seeding.
        This value is stored as a configuration value core.dga.group.
        In my sample the returned value was NULL, and the group was set to 1.
        I have yet to see a sample that uses the core.dga.group config value.

        The year, month, day (set to 8) and the core.dga.group are then applied to the random number:
        
        r = r + year + ((group << 16) + (month << 8) | day)
        '''
        return (self.seed + self.year + ((self.group << 16) + (self.month << 8) | self.day)) % self.modulus

    def __charset(self) -> list:
        '''
        This is the charset list containing ASCII characters used for the CoreBot DGA.
        '''
        charset = [chr(x) for x in range(ord('a'), ord('z'))] + [chr(x) for x in range(ord('0'), ord('9'))]
        return charset

    def dga(self) -> list:
        '''
        The itself is very simple. It generates up to 40 subdomains (configurable with core.dga.domains_count)
        using the common linear congruential generator with multiplier 1664525 and increment 1013904223.

        r = (1664525*r + 1013904223) & 0xFFFFFFFF
        domain_len = len_l + r % (len_u - len_l)
        domain = ""
        for i in range(domain_len):
                r = ((1664525 * r) + 1013904223) & 0xFFFFFFFF
                domain += charset[r % charset_size]
        '''
        generated_domains = []
        lcg = LCG(m=self.modulus, a=self.multiplier, c=self.increment, x_0=self.__date_to_seed())
        r = lcg.random_int()
        charset = self.__charset()
        for j in range(self.nr_domains):
            domain_length = self.length_lower_bound + next(r) % (self.length_upper_bound - self.length_lower_bound)
            domain = ''
            for i in range(domain_length, 0, -1):
                domain += charset[next(r) % len(charset)] 
            domain += '.'+ self.tld
            generated_domains.append(domain)
            #print(generated_domains[j])
        _logger.info('{0} - {1}'.format(__class__.__name__,'Successfully generated n domains.'))
        return generated_domains

class QakBot(object):
    '''
    QBot is a modular information stealer also known as Qakbot or Pinkslipbot. It has been active for years since 2007.
    It has historically been known as a banking Trojan, meaning that it steals financial data from infected systems,
    and a loader using C2 servers for payload targeting and download.

    References: https://malpedia.caad.fkie.fraunhofer.de/details/win.qakbot
    '''
    @test_type(date=datetime, tld=str, nr_domains=int, sandbox=bool, seed=int)
    def __init__(self,
                date:datetime = datetime.now(),
                tld:str = 'com',
                nr_domains:int = 5,
                sandbox:bool = False,
                seed:int = 0):
        _logger.info('{0} - {1}'.format(__class__.__name__,'Initialized QakBot domain generation algorithm.'))

        self.date = date
        self.tld = tld
        self.nr_domains = nr_domains
        self.sandbox = sandbox
        self.seed = self.date_to_seed(date = date, seed = seed).value + self.sandbox

    def dga(self) -> list:
        generated_domains = []
        MT = MT19937(seed = self.seed)
        for i in range(self.nr_domains):
            #tld_nr = self.random_int(MT = MT, lower = 0, upper = len(self.tlds) - 1)
            length = self.random_int(MT = MT,lower = 8, upper = 25)
            domain = ""
            for l in range(length):
                domain += chr(self.random_int(MT = MT, lower = 0, upper = 25) + ord('a'))
            domain += '.'+ self.tld
            generated_domains.append(domain)
        _logger.info('{0} - {1}'.format(__class__.__name__,'Successfully generated n domains.'))
        return generated_domains

    @test_type(date=datetime, seed=int)
    def date_to_seed(self, date:datetime, seed:int) -> c_uint:
        _logger.info('{0} - {1}'.format(__class__.__name__,'Setting seed form date.'))

        dx = (date.day-1) // 10 
        data = "{}.{}.{}.{:08x}".format(
                dx if dx <= 2 else 2,
                date.strftime("%b").lower(), 
                date.year, 
                seed)
        crc = c_uint(binascii.crc32(data.encode('ascii')))
        return crc

    @test_type(MT=MT19937, lower=int, upper=int)
    def random_int(self, MT:MT19937, lower:int, upper:int) -> int:
        '''
        return random int between [lower, upper]
        '''
        _logger.info('{0} - {1}'.format(__class__.__name__,'Generating random number.'))

        r = MT.extract_number() & MT.get_lower_mask()

        return int(lower + float(r) / (2**28)*(upper - lower + 1) )

__all__ = [CoreBot, QakBot]
