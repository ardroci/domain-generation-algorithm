#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import errno
import os
import random
import socket
import sys
import logging
import traceback

import dns.query
from decorators import test_range, test_type, time_this
from exceptions import ArgumentValidationError, InvalidArgumentNumberError

__author__ = 'rcoliveira'

_logger = logging.getLogger(__name__)

class DNS_Crawler(object):
	'''
	Makes a DNS query, sends it and retrieves the reply.
	'''
	@test_type(qnames=list, name_server=str, dns_timeout=float, port=int, source=str, source_port=int, udp=bool, doh=bool)
	def __init__(self, qnames:list=['ardroci.com'], rdtype:dns.rdatatype=dns.rdatatype.ANY, name_server:str='1.1.1.1',
				dns_timeout:float=5.0, port:int=53, source:str='0.0.0.0', source_port:int=0, udp:bool=True,
				doh:bool=False) -> list:
			'''
			qnames:list: list of DNS queries. The default is ['ardroci.com']
			rqname :str: query name. The default is ardoci.com
			rdtype :dns.rdatatype: rdata type. The default is ANY
			name_server :str: name_server. The default is 1.1.1.1.
			dns_timeout :float: number of seconds to wait before the query times out, if None it will wait forever
			port :int: the port send the message to. The default is 53.
			source :int: IPv4 or IPv6 address, specifying the source address. The default is None.
			source_port :int: the port from which to send the message. The default is 0.
			udp:bool: send the query via UDP. The default is True
			doh:bool: send the query via HTTPS. The default is False
			return:list<dict>: returns two lists of dictionaries according the definition in https://datatracker.ietf.org/doc/html/rfc8427#section-5.2
			'''
			self.udp_responses, self.doh_responses = [], []
			if udp:
				self.udp_responses = [self.__query_udp(qname=qname, rdtype=rdtype, name_server=name_server, dns_timeout=dns_timeout,
								port=port, source=source, source_port=source_port) for qname in qnames]					
			if doh:
				self.doh_responses = [self.__query_doh(qname=qname, rdtype=rdtype, name_server=name_server, dns_timeout=dns_timeout,
								port=443, source=source, source_port=source_port) for qname in qnames]

	def get_udp_responses(self):
		'''
		Get responses from queries made over UDP
		'''
		return self.udp_responses

	def get_doh_responses(self):
		'''
		Get responses from queries made over HTTPS
		'''
		return self.doh_responses

	@test_type(qname=str)
	def __create_query_message(self, qname:str='ardroci.com', rdtype:dns.rdatatype=dns.rdatatype.ANY) -> dns.message.QueryMessage:
		'''
		Make a DNS query
		qname :str: query name. The default is ardoci.com
		rdtype :dns.rdatatype: rdata type. The default is ANY
		return: dns.message.QueryMessage: returns a DNS query if was able to create it, None otherwise.
		'''
		#print('rdtype: ', type(rdtype))
		try:
			query = dns.message.make_query(qname=qname, rdtype=rdtype, #rdclass=<RdataClass.IN: 1>,
		        							use_edns=None, want_dnssec=False, ednsflags=None, payload=None,
		        							request_payload=None, options=None, idna_codec=None)
			return query
		except:
			print('Oops!! Exception in \"{0}\": {1}'.format(traceback.extract_tb(sys.exc_info()[-1], 1)[0][2], sys.exc_info()[1]))
		return None

	@test_type(qname=str, name_server=str, dns_timeout=float, port=int, source=str, source_port=int)
	def __query_udp(self, qname:str='ardroci.com', rdtype:dns.rdatatype=dns.rdatatype.ANY, name_server:str='1.1.1.1',
					dns_timeout:float=5.0, port:int=53, source:str='0.0.0.0', source_port:int=0) -> dict:
		'''
		Send a query via UDP.

		qname :str: query name. The default is ardoci.com
		rdtype :dns.rdatatype: rdata type. The default is ANY
		name_server :str: name_server. The default is 1.1.1.1.
		dns_timeout :float: number of seconds to wait before the query times out, if None it will wait forever
		port :int: the port send the message to. The default is 53.
		source :int: IPv4 or IPv6 address, specifying the source address. The default is None.
		source_port :int: the port from which to send the message. The default is 0.
		return :dict: returns a dictionary with the query name as key an the answer as value.
		'''
		try:
			query = self.__create_query_message(qname=qname, rdtype=rdtype)
			if query is None:
				raise ValueError('Unable to create the query DNS message.')
	        # return the response obtained after sending a query via UDP
			response = dns.query.udp(q=query, where=name_server, timeout=dns_timeout, port=port,
									source=source, source_port=0, ignore_unexpected=False,
									one_rr_per_rrset=True, ignore_trailing=False,
									raise_on_truncation=False, sock=None)
			if len(response.answer) == 0: #response.rcode()
				#print('DNS server {0}: has NO records for {1}'.format(name_server, qname), file=sys.stderr)
				return self.__query_response_to_json(query, None)
			else:
				#print('DNS server {0}: has records for {1}'.format(name_server, qname), file=sys.stderr)
				return self.__query_response_to_json(query, response)
		except:
			print('Oops!! Exception in \"{0}\": {1}'.format(traceback.extract_tb(sys.exc_info()[-1], 1)[0][2], sys.exc_info()[1]))
		return self.__query_response_to_json(query, None)

	@test_type(qname=str, name_server=str, dns_timeout=float, port=int, source=str, source_port=int)
	def __query_doh(self, qname:str='ardroci.com', rdtype:dns.rdatatype=dns.rdatatype.ANY, name_server:str='1.1.1.1',
					dns_timeout:float=5.0, port:int=443, source:str='0.0.0.0', source_port:int=0) -> list:
		'''
		Send a query via DNS-over-HTTPS.

		qname:str:query. The default is ardroci.com
		rdtype :dns.rdatatype: rdata type. The default is ANY
		name_server:str:the nameserver IP address or the full URL. If an IP address is given, the URL will be constructed using the following schema: https://<IP-address>:<port>/<path>. The default is 1.1.1.1
		dns_timeout:float or None: the number of seconds to wait before the query times out. If None, the default, wait forever.
		port:int:the port to send the query to. The default is 443.
		source:str: containing an IPv4 or IPv6 address, specifying the source address. The default is the wildcard address.
		source_port:int:the port from which to send the message. The default is 0.
		path, a str. If where is an IP address, then path will be used to construct the URL to send the DNS query to.
		return :dict: returns a dictionary with the query name as key an the answer as value.
		'''
		try:
			query = self.__create_query_message(qname=qname, rdtype=rdtype)
			response = dns.query.https(q=query, where=name_server, timeout=dns_timeout, port=port, source=source,
									source_port=source_port, one_rr_per_rrset=False, ignore_trailing=False,
									session=None, path='/dns-query', post=True, bootstrap_address=None, verify=True)
			if len(response.answer) == 0: #response.rcode()
				#print('DNS server {0}: has NO records for {1}'.format(name_server, qname), file=sys.stderr)
				return self.__query_response_to_json(query, None)
			else:
				#print('DNS server {0}: has records for {1}'.format(name_server, qname), file=sys.stderr)
				return self.__query_response_to_json(query, response)
		except:
			print('Oops!! Exception in \"{0}\": {1}'.format(traceback.extract_tb(sys.exc_info()[-1], 1)[0][2], sys.exc_info()[1]))
		return self.__query_response_to_json(query, None)

	@test_type(query=dns.message.QueryMessage)
	def __query_response_to_json(self, query:dns.message.QueryMessage, response:dns.message.Message) -> dict:
		'''
		returns:dict: returns the DNS query and response in json format, according to the definition presented
		in https://datatracker.ietf.org/doc/html/rfc8427
		'''
		# The format present below was retrieved from 
		'''
		rfc8427_format = {}
		
		rfc8427_format["queryMessage"] = {}
		rfc8427_format["responseMessage"] = {}
		
		if query is not None:
			rfc8427_format["queryMessage"]["ID"] = "TBD"
			rfc8427_format["queryMessage"]["QR"] = "TBD"
			rfc8427_format["queryMessage"]["Opcode"] = "TBD"
			rfc8427_format["queryMessage"]["AA"] = "TBD"
			rfc8427_format["queryMessage"]["TC"] = "TBD"
			rfc8427_format["queryMessage"]["RD"] = "TBD"
			rfc8427_format["queryMessage"]["RA"] = "TBD"
			rfc8427_format["queryMessage"]["AD"] = "TBD"
			rfc8427_format["queryMessage"]["CD"] = "TBD"
			rfc8427_format["queryMessage"]["RCODE"] = "TBD"
			rfc8427_format["queryMessage"]["QDCOUNT"] = "TBD"
			rfc8427_format["queryMessage"]["ANCOUNT"] = "TBD"
			rfc8427_format["queryMessage"]["NSCOUNT"] = "TBD"
			rfc8427_format["queryMessage"]["ARCOUNT"] = "TBD"
			rfc8427_format["queryMessage"]["QNAME"] = "TBD"
			rfc8427_format["queryMessage"]["QTYPE"] = "TBD"
			rfc8427_format["queryMessage"]["QCLASS"] = "TBD"

		if response is not None:
			rfc8427_format["responseMessage"]["ID"] = "TBD"
			rfc8427_format["responseMessage"]["QR"] = "TBD"
			rfc8427_format["responseMessage"]["AA"] = "TBD"
			#my_format["responseMessage"]["opcode"] = dns.opcode.to_text(response.opcode())
			rfc8427_format["responseMessage"]["RCODE"] = dns.rcode.to_text(response.rcode())
			rfc8427_format["responseMessage"]["QDCOUNT"] = "TBD"
			rfc8427_format["responseMessage"]["ANCOUNT"] = "TBD"
			rfc8427_format["responseMessage"]["NSCOUNT"] = "TBD"
			rfc8427_format["responseMessage"]["ARCOUNT"] = "TBD"
			#my_format["responseMessage"]["flags"] = dns.flags.to_text(response.flags)
			#my_format["responseMessage"]["options"] = [opt.to_text() for opt in response.options]
		
			for (name, which) in response._section_enum.__members__.items():
				rfc8427_format[name] = [rrset.to_text(origin=None, relativize=True) for rrset in response.section_from_number(which)]
			rfc8427_format["responseMessage"]["authorityRRs"] = ["TBD"]
		'''

		# TODO: remove the lines below and work over the template define in the RFC
		rfc8427_format = {}

		rfc8427_format["responseMessage"] = {}

		if response is not None:	
			rfc8427_format["responseMessage"]["RCODE"] = dns.rcode.to_text(response.rcode())
			for (name, which) in response._section_enum.__members__.items():
				rfc8427_format[name] = [rrset.to_text(origin=None, relativize=True) for rrset in response.section_from_number(which)]
				
		return rfc8427_format

__all__ = [DNS_Crawler]

