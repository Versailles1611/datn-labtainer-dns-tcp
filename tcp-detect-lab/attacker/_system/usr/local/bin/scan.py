#!/usr/bin/env python3
"""Live TCP SYN port scan used as the detection exercise.

The attacker host scans ports 1-100 of the analyst host roughly every
8 seconds.  The student captures the SYNs on the analyst and identifies
the scanner.
"""
import random
import time

from scapy.all import IP, TCP, send

TARGET = '172.22.0.2'
PORTS = range(1, 101)


def main():
    print('live SYN scan of %s ports 1-100' % TARGET, flush=True)
    while True:
        for port in PORTS:
            try:
                send(IP(dst=TARGET) /
                     TCP(sport=random.randint(20000, 60000),
                         dport=port,
                         flags='S',
                         seq=random.randint(1, 2 ** 32 - 1)),
                     verbose=False)
            except Exception as exc:
                print('send error: %s' % exc, flush=True)
            time.sleep(0.03)
        time.sleep(5)


if __name__ == '__main__':
    main()
