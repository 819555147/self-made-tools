import socket
import threading
import subprocess
import os

'''
服务器端接收指令或文件
'''

# 全局参数
host, port = '127.0.0.1', 9000
tree = False
command = False
upload = False
download = False


def main():
    # 服务器端逻辑
    server_loop()


def server_loop():
    global command
    global upload
    global download
    global tree

    # 建立TCP套接字
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    # UDP
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((host, port))

    try:
        # 循环监听
        while True:
            # UDP首先接收一段控制信息,即客户端选择服务器端的功能: 指向命令行指令 or 上传文件 or 下载文件
            try:
                data, addr = udp.recvfrom(1024)
                print('[!!] [UDP] Incoming connection from %s:%s' % (addr[0], addr[1]))
                temp = eval(data.decode('utf-8'))
                tree = temp['tree']
                command = temp['command']
                upload = temp['upload']
                download = temp['download']
                # print(command, upload, download)

            except Exception as e:
                print('[*?] [UDP] Error happen:', str(e))

            # 监听TCP连接传输
            client_socket, addr = server.accept()
            print('[!!] [TCP] Incoming connection from from %s:%s' % (addr[0], addr[1]))
            server_handler_thread = threading.Thread(target=server_handler, args=(client_socket, addr))
            server_handler_thread.start()

    except Exception as e:
        print('[*?] Error happend:', str(e))
        server.close()
        udp.close()
        print('[!!] [UDP] Closed connection from %s:%s' % (addr[0], addr[1]))


def server_handler(client_socket: socket.socket, addr):
    global command
    global upload
    global download
    global tree

    # 实现不同的功能,注意执行完后恢复参数!
    # 执行cmd命令功能
    if command:
        print('[==>] command shell')
        while True:
            try:
                # 接收cmd命令
                cmd = client_socket.recv(1024).decode('utf-8')

                # 空命令
                if not len(cmd):
                    return
                print('cmd:', cmd)

                # 执行命令，并返回执行结果
                response = run_command(cmd)
                print('response:', response.decode('gbk'))
                client_socket.send(response)
            except:
                pass

        command = False
        print('[!!] [TCP] Closed connection from from %s:%s' % (addr[0], addr[1]))

    # 上传文件功能
    elif upload:
        print('[==>] upload file')

        try:
            # 接收文件内容
            data = client_socket.recv(2048)
            file_buffer = data
            while len(data) == 2048:
                data = client_socket.recv(2048)
                file_buffer += data

            # 写入服务端文件夹中
            with open(upload, 'wb') as f:
                f.write(file_buffer)
            client_socket.send(b'ok!')
            print('[!!]Upload successfully! [%s]' % upload)

        except Exception as e:
            print('[*?] Error happen: '+str(e))
            client_socket.send(bytes(str(e).encode('utf-8')))

        upload = False

    # 下载服务器端文件
    elif download:
        print('[==>] download file')

        # 检测服务器端要下载的文件是否存在，若不
        if not os.path.exists(download) or not os.path.isfile(download):
            print('[*?]Download Failed! Reason: No such file [%s].' % download)
            client_socket.send(bytes(str('No such file [%s] on service.' % download).encode('utf-8')))
            return

        # 若存在
        try:
            client_socket.send(b'ready!')

            with open(download, 'rb') as f:
                filesize = os.path.getsize(download)

                while f.tell() != filesize:
                    client_socket.send(f.read(2048))

                # 避免出现逻辑漏洞，若文件长度恰好为2048的倍数，导致客户器端死等待，外加一个额外的换行符
                if filesize // 2048 == filesize / 2048:
                    client_socket.send(b'\n')

            # 接收回传状态数据
            status = client_socket.recv(1024).decode('utf-8')
            if status == 'ok!':
                print('[!!]Download successfully! [%s]' % download)
            else:
                print('[!!]Download Failed! Reason:', status)

        except Exception as e:
            print('[*?] Error happen: '+str(e))
            client_socket.send(bytes(str(e).encode('utf-8')))

        download = False

    # 显示服务器端目录树
    elif tree:
        print('[==>] tree [%s]' % tree)
        try:
            data = str(list(os.walk(tree)))
            print(data)
            client_socket.send(bytes(data.encode('utf-8')))

            tree = False

        except Exception as e:
            print('[*?] Error happen: ' + str(e))

    else:
        pass


def run_command(command):
    '''
    :description: 在目标操作系统中指向命令，并返回执行结果
    :param command: 待执行命令
    :return output: 返回命令执行结果
    '''
    # 换行
    command = command.rstrip()

    # 运行命令并将返回输出
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = b"Failed to execute command.\r\n"

    # 并将输出发送
    return bytes(output)


if __name__ == '__main__':
    main()