import os
import socket
'''
下例仅仅嗅探一个数据包，不解码,该数据包应该是ping xxx 的ICMP包
开启混杂模式需要管理员权限，需要以管理员身份打开cmd并执行脚本

在一个管理员cmd 输入: python sniffer.py
另一个cmd 输入: ping 某个主机地址(如127.0.0.1)
'''

# 监听的主机
host = '127.0.0.1'

# 创建原始套接字，然后绑定在公开接口上
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0 ))

# 设置在捕获的数据包中包含IP头
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# 在Windows系统上，我们需要设置IOCTL以启用混杂模式
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# 读取单个数据包
# data = sniffer.recvfrom(65565)
# print(data[0], data[1])
print(sniffer.recv(65565))

# 关闭混杂模式
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)



