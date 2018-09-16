import sys
import socket
import getopt
import os

'''
客户端

'''
# 参数
target_host, target_port = '', ''
tree = False
command = False
upload = False
download = False


def usage():
    print("My Net Tool")
    print()
    print("Usage: python Aclent.py -i host -p port")
    print("-t --tree=path                 : file tree of service path")
    print("-c --command              : initialize a command shell")
    print("-u --upload=destination   : upload local file and write to service [destination]")
    print("-d --download=target_path : download file from service [target_path]")
    print()
    print("Examples:")
    print(".py -i 192.168.0.1 -p 9000 -t ./")
    print(".py -i 192.168.0.1 -p 9000 -c")
    print(".py -i 192.168.0.1 -p 9000 -u=c:\\target.exe")
    print(".py -i 192.168.0.1 -p 9000 -d=c:\\target.rar")
    sys.exit(0)


def main():
    global target_host, target_port
    global tree
    global command
    global upload
    global download

    # 获取输入选项
    if len(sys.argv[1:]) <= 4:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:p:t:cu:d:",
                                  ["host=", "port=", "tree=", "command", "upload=", "download="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    # print(opts, args)

    for o, a in opts:
        if o in ("--host", "-i"):
            target_host = a
        elif o in ("--port", "-p"):
            target_port = a
        elif o in ("--tree", "-t"):
            tree = a
        elif o in ("--command", "-c"):
            command = True
        elif o in ("--upload", "-u"):
            upload = a.lstrip('=')
        elif o in ("--download", "-d"):
            download = a.lstrip('=')

    # print(target_host, target_port, command, upload, download)

    # 首先发送一段控制信息,即客户端选择服务器端的功能: 指向命令行指令 or 上传文件 or 下载文件
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        data = {'tree': tree, 'command': command, 'upload': upload, 'download': download}
        udp.sendto(bytes(str(data).encode('utf-8')), (target_host, int(target_port)))
    except Exception as e:
        print('[*?] Error happen:', str(e))
        sys.exit(0)

    udp.close()

    # 建立TCP连接
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((target_host, int(target_port)))

    # 若是要求服务器端执行命令
    if command:
        while True:
            try:
                command_shell(client)
            except KeyboardInterrupt:
                client.close()
                sys.exit(0)

    # 上传文件到服务器端
    elif upload:
        try:
            upload_file(client)
        except KeyboardInterrupt:
            client.close()
            sys.exit()

    # 从服务器下载文件
    elif download:
        try:
            download_file(client)
        except KeyboardInterrupt:
            client.close()
            sys.exit()

    # 显示服务器端目录树
    elif tree:
        data = eval(client.recv(4096).decode('utf-8'))
        for i in data:
            print(i)

    else:
        pass


def command_shell(client: socket.socket):
    '''
    :param client: 客户端TCP套接字
    实现在服务器端指向命令行指令功能
    '''
    buffer = input("[==>]请输入指令:(目录操作等涉及文件的指令不可使用)\n") + '\n'
    if buffer in ('\n', 'exit\n', 'exit()\n') or buffer.startswith('cd '):
        print('[*?]不支持的指令!retry!')
        return
    client.send(bytes(buffer.encode('utf-8')))
    response = client.recv(65535).decode('gbk')
    print(response)


def upload_file(client: socket.socket):
    '''
    :param client: 客户端TCP套接字
    实现上传本地文件到服务器端功能
    '''
    filename = input('[==>]请输入要上传到服务器端的本地文件名：')
    if not os.path.exists(filename):
        print('[*?]不存在该文件！！！')
        return
    if not os.path.isfile(filename):
        print('[*?]上传的内容不应该是目录！！！')
        return

    # 发送文件内容
    with open(filename, 'rb') as f:
        filesize = os.path.getsize(filename)

        while f.tell() != filesize:
            client.send(f.read(2048))

        # 避免出现逻辑漏洞，若文件长度恰好为2048的倍数，导致服务器端死等待，外加一个额外的换行符
        if filesize // 2048 == filesize / 2048:
            client.send(b'\n')

    # 接收回传状态数据
    status = client.recv(1024).decode('utf-8')
    if status == 'ok!':
        print('[!!]Upload successfully! local file [%s] to service [%s]' % (filename, upload))
    else:
        print('[!!]Upload Failed! Reason:', status)


def download_file(client: socket.socket):
    '''
    :param client: 客户端TCP套接字
    实现下载服务器端文件的功能
    '''
    try:
        # 接收状态消息
        status = client.recv(100).decode('utf-8')
        if not status == 'ready!':
            raise Exception(status)

        # 接收文件内容
        data = client.recv(2048)
        file_buffer = data
        while len(data) == 2048:
            data = client.recv(2048)
            file_buffer += data

        filename = input('请输入文件下载的目的目录：')
        # 写入客户端文件夹中
        with open(filename, 'wb') as f:
            f.write(file_buffer)
        client.send(b'ok!')
        print('[!!]Download successfully! local file [%s] from service [%s]' % (filename, download))

    except Exception as e:
        print('[*?] Download Failed! Reason: ' + str(e))


if __name__ == '__main__':
    main()

'''
服务端:
python server.py

客户端:
python Aclient.py -i localhost -p 9000 -c
'''

