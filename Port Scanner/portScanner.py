# -*- coding: utf-8 -*-
import sys
from socket import *

# python3 portScanner.py <host> <start_port>-<end_port>
host = sys.argv[1]
start_port, end_port = map(int, sys.argv[2].split('-'))

target_ip = gethostbyname(host)
logs = []

print("Details:")
for port in range(start_port, end_port + 1):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((target_ip, port))
    if result == 0:
        logs.append("[open] %d " % port)
        print("[open] %d" % port)
    else:
        logs.append("[close] %d " % port)
        print("[close] %d" % port)

with open("log.txt", 'w+') as f:
    for port in logs:
        f.write(port+'\n')
