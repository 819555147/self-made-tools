import sys
import os
import queue
import requests
import time
import threading

q=queue.Queue()


def scan():
    while not q.empty():  # 只要字典里不为空，就一直循环
        dir = q.get()        # 把存储的payload取出来
        urls = url+dir       # url+payload就是一个payload
        urls = urls.replace('\n','')  # 利用回车来分割开来，不然打印的时候不显示
        code = requests.get(urls).status_code  # 把拼接的url发起http请求
    if code == 200 or code == 403:   # 如果返回包状态码为200或者403，就打印url+状态码
       print(urls+'|'+str(code))
       f = open('result_ok.txt', 'a+')
       f.write(urls)
       f.close()
    else:  # 不然就打印url+状态码，并延时一秒
       print(urls+'|'+str(code))
       time.sleep(1)


def show():
   print("使用方法：网址+字典文件+线程数,例如:python DisScanner.py http://www.xxx.cn dic.txt 5")


if __name__ == '__main__':
   path = os.path.dirname(os.path.realpath(__file__))
   if len(sys.argv) < 4:  # 小于4的话，打印banner
       show()
       sys.exit()
   url = sys.argv[1]  # 用户输入的url
   txt = sys.argv[2]  # 用户输入的字典
   xc = sys.argv[3]   # 用户输入的线程
   for dir in open(path+"/"+txt):  # 当前路径加上字典名就是绝对路径，然后循环字典里的payload
        q.put(dir)
   for i in range(int(xc)):
       t = threading.Thread(target=scan)
       t.start()
