Domain Generation Algorithm
=======

What is it?
-----------
Several malware families use domain generation algorithms (DGAs) periodically to create a large number of domain names used for command and control purposes.
For this study I have considered two well known banking trojans, QakBot and CoreBot, and created the following content:

 - Pseudo-random Generators
	- Mersenne Twister 19937 generator
	- Linear congruential generator

- Domain generation algorithms
	- QakBot's DGA generators
	- CoreBot's DGA generator

- DNS Crawler
	- Makes a DNS query, sends it and retrieves the reply in json format (RFC8427)

Usage
-----------
You can use the skeleton.py file as a starting point for your work.

```
python3 skeleton.py --help
usage: skeleton.py [-h] [--sandbox] [--seed-qakbot {0,1}] [--seed-corebot SEED_COREBOT] [--nr-domains NR_DOMAINS] [--tld TLD]
                   [--dns-name-server DNS_NAME_SERVER] [--dns-timeout DNS_TIMEOUT] [--dns-source DNS_SOURCE_IP_ADDRESS]
                   [--dns-source-port DNS_SOURCE_PORT] [--dns-udp | --dns-https] [-v] [-vv]

QakBot's and CoreBot's DGA generator algorithms.

optional arguments:
  -h, --help            show this help message and exit
  --sandbox             -
  --seed-qakbot {0,1}   The seed & date values will be used by the Mersenne Twister 19937 generator and QakBot's DGA generator.
  --seed-corebot SEED_COREBOT
                        The seed & date values will be used by CoreBot's DGA generator.
  --nr-domains NR_DOMAINS
                        -
  --tld TLD             Top level domain used by QakBot's and CoreBot's DGA generators.
  --dns-name-server DNS_NAME_SERVER
                        Configure the DNS name server that is going to be used.
  --dns-timeout DNS_TIMEOUT
                        DNS time out.
  --dns-source DNS_SOURCE_IP_ADDRESS
                        DNS source IP address.
  --dns-source-port DNS_SOURCE_PORT
                        DNS source port.
  --dns-udp             Perform DNS queries to the DGA domains over UDP.
  --dns-https           Perform DNS queries to the DGA domains over HTTPS.
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG
```

### And a test using DoH calls to QakBot's and CoreBot's domains
```
$ python3 skeleton.py --dns-https --tld ardroci.com --nr-domains 10
```

TODO
-----------

- finish implementation of RFC8427 in DNS Crawler class