'''
加载配置参数
    # 下载整个网站、目录， -r 或 --recursive
    # 镜像，-m 或 --mirror
    # 重试次数，-t 或 --tries=2
    # 不要覆盖已经存在的文件，-nc 或 --no-clobber
    # 只下载比本地新的文件, -N 或 --timestamping
    # 下载显示HTML文件的所有图片，-p 或 --page-requisites
    # 强制建立目录, -x 或 --force-directories
    # 爬虫限制，-e robots=off
    # 断点续传, -c
    # 后台下载，-b
    # 下载限速，--limit-rate=300k
    # 用户代理， --user-agent='...'
    # 表示不下载别的站点的链接， -np
    # 拒绝接受的文件类型， -R 或 --reject=LIST
    # 允许/不允许服务器端的数据缓存(一般情况下允许), -C 或 --cache=on/off
    # 转换非相对链接为相对链接，-k 或 --convert-links
    # 将所有text/html文档以.html扩展名保存，-E 或 --html-extension
    # 记录下载日志，-o xx.log
    # 不检查证书，--no-check-certificate
    # 可以接受的域名,用逗号分隔，-D 或 --domains=LIST
    # 放到指定目录下，-P=/root
'''

from configparser import ConfigParser


def load_config(filename):
    config = ConfigParser()
    config.read(filename)
    result = {}
    sections = config.sections()
    for section in sections:
        options = config.options(section)
        for option in options:
            value = config.get(section, option)
            if value == '[]' or value == 'False':
                continue
            result[option] = value

    return result


# 单元测试
if __name__ == '__main__':
    print(load_config('../../default.conf'))