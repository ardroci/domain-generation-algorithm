#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
from datetime import datetime
import dns.rdatatype
from domain_generation_algorithms import CoreBot, QakBot
from dns_crawler import DNS_Crawler
from exceptions import InvalidArgumentNumberError, ArgumentValidationError

__author__ = 'rcoliveira'

_logger = logging.getLogger(__name__)

def parse_args(args):
    parser = argparse.ArgumentParser(
        description="QakBot's and CoreBot's DGA generator algorithms.")

    ################################################################################################
    ##                                          DGA                                               ##
    ################################################################################################
    parser.add_argument(
        '--sandbox',
        dest="sandbox",
        help="-",
        action='store_true',
        default=True,
        required=False)
    parser.add_argument(
        '--seed-qakbot',
        dest="seed_qakbot",
        help="The seed & date values will be used by the Mersenne Twister 19937 generator and QakBot's DGA generator.",
        type=int,
        choices={0,1},
        default=0,
        required=False)
    parser.add_argument(
        '--seed-corebot',
        dest="seed_corebot",
        help="The seed & date values will be used by CoreBot's DGA generator.",
        type=int,
        default=0x1DB98930,
        required=False)
    parser.add_argument(
        '--nr-domains',
        dest="nr_domains",
        help="-",
        type=int,
        default=1,
        required=False)
    #parser.add_argument(
    #    '--date',
    #    dest="date",
    #    help="The seed & date values will be used by the Mersenne Twister 19937 generator and QakBot's and CoreBot's DGA generators.",
    #    #action='store_const',
    #    type=datetime,
    #    default=datetime.now(),
    #    required=False)
    parser.add_argument(
        '--tld',
        dest="tld",
        help="Top level domain used by QakBot's and CoreBot's DGA generators.",
        type=str,
        default='ardrocir.com',
        required=False)
    ################################################################################################
    ##                                          DNS                                               ##
    ################################################################################################
    #parser.add_argument(
    #    '--dns-rdtype',
    #    dest="dns_rdtype",
    #    help="DNS RDTYPE",
    #    default='dns.rdatatype.ANY',
    #    required=False)
    parser.add_argument(
        '--dns-name-server',
        dest="dns_name_server",
        help="Configure the DNS name server that is going to be used.",
        type=str,
        default='8.8.8.8',
        required=False)
    parser.add_argument(
        '--dns-timeout',
        dest="dns_timeout",
        help="DNS time out.",
        type=float,
        default=5.0,
        required=False)
    parser.add_argument(
        '--dns-source',
        dest="dns_source_ip_address",
        help="DNS source IP address.",
        type=str,
        default='0.0.0.0',
        required=False)
    parser.add_argument(
        '--dns-source-port',
        dest="dns_source_port",
        help="DNS source port.",
        type=int,
        default=0,
        required=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--dns-udp', 
        dest="udp",
        help="Perform DNS queries to the DGA domains over UDP.",
        action='store_true',
        required=False)
    group.add_argument(
        '--dns-https', 
        dest="doh",
        help="Perform DNS queries to the DGA domains over HTTPS.",
        action='store_true',
        required=False)
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel:int) -> None:
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.info("Starting crazy calculations...")

    QakBot_domains = QakBot(date=datetime.now(),
                            tld=args.tld, 
                            nr_domains=args.nr_domains,
                            sandbox=args.sandbox,
                            seed=args.seed_qakbot).dga()
    print('{0} - {1}'.format('QakBot domains', QakBot_domains))
    CoreBot_domains = CoreBot(tld=args.tld,
                            nr_domains=args.nr_domains,
                            year=datetime.now().year,
                            month=datetime.now().month,
                            day=8,
                            group=1,
                            seed=args.seed_qakbot,
                            multiplier=1664525,
                            increment=1013904223,
                            modulus=2**32,
                            length_lower_bound=0xC,
                            length_upper_bound=0x18).dga()
    print('{0} - {1}'.format('CoreBot domains', CoreBot_domains))

    if args.udp:
        dns_destination_port=53
    if args.doh:
        dns_destination_port=443
    if args.udp or args.doh:
        q = DNS_Crawler(qnames=QakBot_domains+CoreBot_domains,
                        rdtype=dns.rdatatype.ANY,
                        name_server=args.dns_name_server,
                        dns_timeout=args.dns_timeout,
                        port=dns_destination_port,
                        source=args.dns_source_ip_address,
                        source_port=args.dns_source_port,
                        udp=args.udp,
                        doh=args.doh)
        if args.udp:
            udp_responses = q.get_udp_responses()
            print('{0} - {1}'.format('UDP responses', udp_responses))

        if args.doh:
            doh_responses = q.get_doh_responses()
            print('{0} - {1}'.format('DoH responses', doh_responses))

    _logger.info("Script ends here")

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()

