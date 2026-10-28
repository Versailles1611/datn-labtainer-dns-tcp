TCP ATTACK DETECTION - CAPTURE EVIDENCE
=======================================

Topology (LAN 172.22.0.0/24):

  Host       IP            MAC
  ------------------------------------------------------
  analyst    172.22.0.2    02:42:ac:16:00:02
  victim     172.22.0.3    02:42:ac:16:00:03
  server     172.22.0.4    02:42:ac:16:00:04
  attacker   172.22.0.5    02:42:ac:16:00:05

  server runs a TCP echo service on port 9999.

Files:

  01-syn-flood.pcap       Capture of a TCP SYN flood.
  02-rst-injection.pcap   Capture of a TCP session reset by a spoofed RST.
  03-session-hijack.pcap  Capture of data injected into a live TCP session.

Useful tcpdump options:

  -nn     do not resolve names or ports
  -e      show Ethernet (MAC) addresses
  -S      show absolute TCP sequence numbers
  -A      show packet payload as ASCII

Examples:

  tcpdump -nn -r 01-syn-flood.pcap
  tcpdump -nn -e -S -r 02-rst-injection.pcap 'tcp[tcpflags] & tcp-rst != 0'
  tcpdump -nn -e -S -A -r 03-session-hijack.pcap 'tcp port 9999'
