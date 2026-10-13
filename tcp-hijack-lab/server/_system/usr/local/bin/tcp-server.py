#!/usr/bin/env python3
"""Simple TCP service for the tcp-hijack-lab.
Listens on 172.21.0.3:9999, logs every received line to /var/log/session.log
and replies with ACK:<line>. Used to demonstrate TCP session hijacking."""

import socket
import datetime

LOG = '/var/log/session.log'
HOST = '0.0.0.0'
PORT = 9999


def log(msg):
    ts = datetime.datetime.now().isoformat(timespec='seconds')
    with open(LOG, 'a') as f:
        f.write('%s %s\n' % (ts, msg))


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(5)
    print('tcp-server listening on %s:%d' % (HOST, PORT), flush=True)
    while True:
        conn, addr = srv.accept()
        log('CONNECT %s' % addr[0])
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                text = data.decode(errors='replace').strip()
                log('RECV %s' % text)
                conn.sendall(b'ACK:' + data)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
