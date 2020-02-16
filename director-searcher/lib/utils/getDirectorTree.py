'''
获取文件目录
'''
from os import listdir
from os.path import isdir, isfile
from queue import Queue


def get_director_tree(prefix):
    dirs = Queue()
    dir_tree = []

    current_path = '.'
    for one in listdir(current_path):
        # print(one, isdir(one), isfile(one))
        if isdir(current_path + '/' + one):
            dirs.put((current_path, one))
        else:
            dir_tree.append(prefix + '/' + one)

    while not dirs.empty():
        base_path, one_dir = dirs.get()
        current_path = base_path + '/' + one_dir
        # print(listdir(current_path))
        for one in listdir(current_path):
            # print(current_path + '/' + one, isdir(current_path + '/' + one), isfile(current_path + '/' + one))
            if isdir(current_path + '/' + one):
                dirs.put((current_path, one))
            else:
                dir_tree.append(prefix + '/' + current_path.replace('./', '') + '/' + one)

    return dir_tree


if __name__ == '__main__':
    dir_tree = get_director_tree('哈哈://u.vip')
    print(dir_tree)