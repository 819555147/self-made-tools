# -*- coding: utf-8 -*-
import sys
import _thread as thread
from socket import *


def tcp_test(port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((target_ip, port))
    lock.acquire()
    if result == 0:
        print("[ Opened Port ]:", port)
    else:
        print("[ Closed] Port ]:", port)
    lock.release()


# python3 port_scan_threads.py <host> <start_port>-<end_port>
lock = thread.allocate_lock()
host = sys.argv[1]
start_port, end_port = map(int, sys.argv[2].split('-'))
target_ip = gethostbyname(host)


if __name__ == '__main__':
    for port in range(start_port, end_port):
        thread.start_new_thread(tcp_test, (port,))
