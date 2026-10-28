#!/usr/bin/env python3
"""Simple multi-threaded TCP echo service for the tcp-detect-lab.

Listens on 0.0.0.0:9999, logs every event to /var/log/session.log and
answers each received line with ``ACK:<line>``.
"""

import datetime
import socket
import threading

LOG = '/var/log/session.log'
HOST = '0.0.0.0'
PORT = 9999


def log(msg):
    ts = datetime.datetime.now().isoformat(timespec='seconds')
    with open(LOG, 'a') as fh:
        fh.write('%s %s\n' % (ts, msg))


def handle(conn, addr):
    log('CONNECT %s' % addr[0])
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            text = data.decode(errors='replace').strip()
            log('RECV %s' % text)
            conn.sendall(b'ACK:' + data)
            log('SENT ACK:%s' % text)
    except Exception as exc:
        log('RESET %s (%s)' % (addr[0], exc.__class__.__name__))
    finally:
        try:
            conn.close()
        except Exception:
            pass
        log('CONNECTION CLOSED %s' % addr[0])


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(16)
    log('LISTEN %s:%d' % (HOST, PORT))
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == '__main__':
    main()
