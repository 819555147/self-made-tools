'''
网站目录扫描器，下载网站目录并保存本地
'''

'''
wget -r -p -E -k --convert-links --restrict-file-names=ascii -e robots=off https://www.baidu.com 建立本地目录
wget -r -nc -p -E -k --restrict-file-names=ascii --domain scart.be  www.scart.be
wget -r -p -nc -E -k --convert-links --restrict-file-names=ascii -e robots=off https://www.baidu.com
wget -m -p -nc -E -k --convert-links --restrict-file-names=ascii -e robots=off https://www.baidu.com
'''
from lib.utils import loadConfigure, makeCMD, getDirectorTree
from os import chdir, system, listdir, walk
from re import sub


class DirectorSearch(object):
    def __init__(self, target_url):
        # object.__init__(self)
        self.target_url = target_url
        self.parameter = loadConfigure.load_config('../default.conf')
        self.cmd = makeCMD.make_cmd(self.parameter, self.target_url)
        print(self.cmd)

    def _download_history_list_log(self):
        '''
            一份下载网站的记录（列表）
        '''
        target = sub('.*?//', '', self.target_url)
        target = sub('www.', '', target)
        with open('down_history.list.log', 'a+', encoding='utf-8') as f:
            f.write(target+'\n')

    def download_website(self):
        """
            启动目录下载，must done
        """
        chdir('../thirdpart')
        # system(self.cmd)

        self._download_history_list_log()

    def dir_search(self):
        """"
            目录扫描
        """
        target = sub('.*?//', '', self.target_url)
        target = sub('www.', '', target)
        chdir(target)
        prefix = self.target_url
        dir_tree = getDirectorTree.get_director_tree(prefix)
        # .... 调用目录扫描器
        # .........
        # .....
        print('dir tree: ', dir_tree)
        return dir_tree

    def run(self):
        '''
            启动目录扫描，直接调用这个方法即可
        '''
        self.download_website()
        self.dir_search()
        print('Over!')

    def configure_manager(self):
        raise NotImplementedError


if __name__ == '__main__':
    dirS = DirectorSearch('https://github.com')  # 尾部不要带'/'
    dirS.run()
