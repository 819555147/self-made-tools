from time import strftime
from re import sub


def make_cmd(parameter, target_url):
    target = sub('.*?//', '', target_url)
    target = sub('www.', '', target)
    cmd = 'wget'
    for k, v in parameter.items():
        if v == 'True':
            if k == '-o':
                cmd += ' %s %s.log' % (k, target+strftime('__%Y-%m-%d_%H_%M_%S'))
            else:
                cmd += ' ' + k
        else:
            cmd += ' ' + k + ' ' + v
    cmd += ' ' + target_url
    # print(cmd)
    return cmd


# 单元测试
if __name__ == '__main__':
    from lib.utils import loadConfigure
    cmd = make_cmd(loadConfigure.load_config('../../default.conf'), 'www.baidu.com')
    print(cmd)
