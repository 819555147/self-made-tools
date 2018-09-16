# -* encode UTF-8
import numpy as np
from numpy import dtype
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import codecs
import csv
from collections import defaultdict
import json

# 自定义numpy数据类型
movie = dtype([('movieid', int), ('title', str, 70)])
rate = dtype([('movieid', int), ('rating', float)])
film_rating = dtype([('title', str, 70), ('rating', float)])
film_genres = dtype([('title', str, 70), ('genres', str, 70)])
film_genres_rating = dtype([('title', str, 70), ('genres', str, 70), ('rating', float)])
user_rating = dtype([('userid', int), ('rating', float)])


def countGenres(genres_nd):
    '''
    :param genres_nd:
    :return:
    统计得到字典： {genres:出现次数}
    以及列表：包含出现的所有标签
    '''
    dictionary = defaultdict(int)
    lst = []
    for _ in genres_nd:
        for __ in _['genres'].split("|"):
            dictionary[__] += 1
            lst.append(__)

    # print(dictionary)
    return dictionary, lst


def merge(nd1: 'ndarray include id and title', nd2: 'ndarray include id and rating') -> 'ndarray with id and average rating':
    '''
    :param nd1: id and title
    :param nd2: id and rating
    :return: ndarray id and rating
    '''
    res = np.array([], dtype=rate)
    for _ in nd1:
        # 筛选条件：movieid相等
        condition = nd2['movieid'] == _["movieid"]
        if np.all(condition == False) == True:
            continue
        # 筛选出id相等的movie的所有评分
        total_rating = np.compress(condition, nd2)["rating"]
        # 计算均值
        mean_rating = np.mean(total_rating)
        # 生成 rate对象
        temp = np.array([(_['movieid'], mean_rating)], dtype=rate)
        # 组合
        res = np.concatenate((res, temp), 0)
    return res


def extract(nd1: 'ndarray with id and rating', nd2: 'ndarray with id and title')-> 'ndarray with title and rating':
    '''
    :param nd1: id and rating
    :param nd2: id and title
    :return: ndarray with title and rating
    '''
    result = np.array([], dtype=film_rating)
    # print(nd2)

    for _ in nd1:
        condition = nd2['movieid'] == _['movieid']
        # print(condition)
        if np.all(condition == False) == True:
            continue
        # 通过id筛选得到title，这里肯定唯一
        tt = np.compress(condition, nd2)['title'][0]
        # 生成film对象
        temp = np.array([(tt, _['rating'])], dtype=film_rating)
        # 组合
        result = np.concatenate((result, temp), 0)
    return result


def union(nd1: 'ndarray with title and rating', nd2: 'ndarray with title and genres')-> 'ndarray with title and genres':
    '''
    :param nd1: title and rating
    :param nd2: title and genres
    :return: ndarray title and genres
    '''
    result = np.array([], dtype=film_genres)

    for _ in nd1:
        condition = nd2['title'] == _['title']
        # print(condition)
        if np.all(condition == False) == True:
            continue
        # 通过title筛选得到genres，这里肯定唯一
        gen = np.compress(condition, nd2)['genres'][0]
        # 生成film对象
        temp = np.array([(_['title'], gen)], dtype=film_genres)
        # 组合
        result = np.concatenate((result, temp), 0)
    return result


def union2(nd1: 'ndarray with title and rating', nd2: 'ndarray with title and genres')-> 'ndarray with title and genres and rating':
    '''
        :param nd1: title and rating(average)
        :param nd2: title and genres
        :return: ndarray title and genres and rating
        '''
    result = np.array([], dtype=film_genres_rating)

    for _ in nd1:
        condition = nd2['title'] == _['title']
        # print(condition)
        if np.all(condition == False) == True:
            continue
        # 通过title筛选得到genres，这里肯定唯一
        gen = np.compress(condition, nd2)['genres'][0]
        # 生成film对象
        temp = np.array([(_['title'], gen, _['rating'])], dtype=film_genres_rating)
        # 组合
        result = np.concatenate((result, temp), 0)
    return result


# 读取电影id和名字，使用numpy.loadtxt有些行会读错！不知为何
# movieid, title = np.loadtxt('movies.csv', dtype=str, delimiter=',', skiprows=1, usecols=(0, 1),
#                             unpack=True, encoding='cp936')
# 不知为何读不出来
# movieid, title, genres = np.genfromtxt(file, dtype=str, delimiter=',', skip_header=1, usecols=(0, 1, 3),
#                                        unpack=True)
# movieid2, rating = np.loadtxt('ratings.csv', dtype=float, delimiter=',', skiprows=1, usecols=(1, 2), unpack=True,
#                               converters={1: lambda x: int(x), 2: lambda x: float(x)}, encoding='cp936')

# 使用csv读取正确无误
# 读取电影id和title以及genres
with codecs.open('movies.csv', 'r', encoding='cp936') as f:
    reader = csv.reader(f)
    movies = np.array(list(reader))
    movieid = movies[1:, 0]
    title = movies[1:, 1]
    genres = movies[1:, 2]

# 读取电影id和rating
with codecs.open('ratings.csv', 'r', encoding='cp936') as f:
    reader = csv.reader(f)
    movies = np.array(list(reader))
    userid = movies[1:, 0]
    movieid2 = movies[1:, 1]
    rating = movies[1:, 2]


# i: id-title
# ii: id-rating
# iii: title-genres
# iiii: userid-rating
i = np.array(list(zip(map(int, movieid), title)), dtype=movie)
ii = np.array(list(zip(map(int, movieid2), rating)), dtype=rate)
iii = np.array(list(zip(title, genres)), dtype=film_genres)
iiii = np.array(list(zip(map(int, userid), rating)), dtype=user_rating)
# print(i)
# print(ii)
# print(iii)


# 获取所有电影id以及其平均评分的数组
res = merge(i, ii)

# 计算所有电影的平均分
mean_rating = np.mean(res['rating'])


def figure1():
    # 图1
    fig = plt.figure(1)
    # 绘制散点图，显示离散数据点
    plt.subplot(121)
    plt.scatter(res['movieid'][:], res['rating'][:], c=res['rating'][:]*100, s=res['rating'][:]*0.1)

    # 百分位数
    p25 = np.percentile(res['rating'], 25)
    p50 = np.percentile(res['rating'], 50)
    p75 = np.percentile(res['rating'], 75)

    plt.axhline(p25, label='25% line', c='r')
    plt.axhline(p50, label='50% line', c='g')
    plt.axhline(p75, label='75% line', c='b')

    plt.xlabel('movie id')
    plt.ylabel('rating')

    plt.title('movie rating')

    # 箱线图
    plt.subplot(122)
    plt.boxplot(res['rating'], 0, 'gx', vert=False)

    plt.legend(['Q5', 'Q4', '', 'Q2',
                'Q1', 'median value', 'x stand for outlier'], loc='best')
    plt.title('show outlier')


def figure2():
    # 直方图，显示rating分布
    fig = plt.figure(2)
    plt.autoscale()

    # 调整字体
    matplotlib.rcParams.update({'font.size': 7})

    plt.subplot(211)
    # 柱数目，0.1分一个桶，从0-5分共有51个桶
    buckets = [x/10+0.05 for x in range(0, 51)];buckets[0] -= 0.05;buckets[-1] -= 0.05
    # buckets = [x/10 for x in range(0, 51)]
    # print(buckets)
    plt.hist(res['rating'], buckets, facecolor='orange', edgecolor='black')

    # 高于平均分的和低于平均分的以不同颜色区分，有错误
    x = np.array([x/10 for x in range(0, 51)])
    # plt.fill_betweenx(x, x > mean_rating, res['rating'], facecolor="green", alpha=0.4)
    # plt.fill_betweenx(x, x <= mean_rating, res['rating'], facecolor="red", alpha=0.4)

    # 平均评分线
    plt.axvline(mean_rating, label='mean rating', c='r')

    plt.xlabel('rating')
    plt.ylabel('amount')
    # x轴
    plt.xticks(x)
    plt.legend(loc='best')
    plt.title('rating amount')

    plt.subplot(212)
    sns.set_style('darkgrid')
    sns.distplot(res['rating'], kde=True, hist_kws=None, kde_kws=None)
    # fit参数可以指定概率分布
    # sns.distplot(d, fit=stats.laplace, kde=False)

    plt.xlabel('rating')
    plt.ylabel('amount')
    # x轴
    plt.xticks(x)


def figure3_4_5():
    # 计算各个分段得的数组
    res09 = np.compress(res['rating'] <= 0.9, res)
    res19 = np.compress(1.0 <= res['rating'], res)
    res19 = np.compress(1.9 >= res19['rating'], res19)
    res29 = np.compress(2.0 <= res['rating'], res)
    res29 = np.compress(2.9 >= res29['rating'], res29)
    res39 = np.compress(3.0 <= res['rating'], res)
    res39 = np.compress(3.9 >= res39['rating'], res39)
    res50 = np.compress(4.0 <= res['rating'], res)
    res50 = np.compress(5.0 >= res50['rating'], res50)

    resgm = np.compress(res['rating'] >= mean_rating, res)
    reslm = np.compress(res['rating'] < mean_rating, res)

    # 图3，各个分段的饼图
    fig = plt.figure(3)

    plt.subplot(121)
    # 饼图标签
    labels = '0-0.9', '1.0-1.9', '2.0-2.9', '3.0-3.9', '4.0-5.0'

    # 各部分占比
    size1 = res09.size
    size2 = res19.size
    size3 = res29.size
    size4 = res39.size
    size5 = res50.size

    sizes = [size1, size2, size3, size4, size5]

    # 0.1表示将Hogs那一块凸显出来
    explode = (0.1, 0.1, 0.1, 0, 0.1)

    # startangle表示饼图的起始角度
    plt.pie(sizes, explode=explode, labels=labels, autopct='%2.2f%%', labeldistance=0.8, shadow=True, startangle=90)
    # 饼图等宽
    plt.axis('equal')
    plt.title('Proportion of each part: 0-0.9, 1.0-1.9, 2.0-2.9, 3.0-3.9, 4.0-5.0')

    plt.subplot(122)
    labels = '>= mean rating', '< mean rating'
    size1 = resgm.size
    size2 = reslm.size
    sizes = [size1, size2]

    plt.pie(sizes, labels=labels, autopct='%2.2f%%', labeldistance=0.8, shadow=True, startangle=80)
    # 饼图等宽
    plt.axis('equal')
    plt.title('Proportion of two part: >= mean rating, < mean rating')

    # 图4，展示各个评分段的散点图
    fig = plt.figure(4)

    plt.subplot(231)
    plt.scatter(res09["movieid"], res09["rating"], c=res09["rating"] * 100, s=res09['rating'][:] * 0.3)
    plt.title('0-0.9')

    plt.subplot(232)
    plt.scatter(res19["movieid"], res19["rating"], c=res19["rating"] * 100, s=res19['rating'][:] * 0.1)
    plt.title('1.0-1.9')

    plt.subplot(233)
    plt.scatter(res29["movieid"], res29["rating"], c=res29["rating"] * 100, s=res29['rating'][:] * 0.1)
    plt.title('2.0-2.9')

    plt.subplot(234)
    plt.scatter(res39["movieid"], res39["rating"], c=res39["rating"] * 100, s=res39['rating'][:] * 0.1)
    plt.title('3.0-3.9')

    plt.subplot(235)
    plt.scatter(res50["movieid"], res50["rating"], c=res50["rating"] * 100, s=res50['rating'][:] * 0.1)
    plt.title('4.0-5.0')

    # 图五，低于平均和高于平均的散点图
    fig = plt.figure(5)

    plt.subplot(121)
    plt.scatter(resgm["movieid"], resgm["rating"], c=resgm["rating"] * 100, s=res['rating'][:] * 0.1)
    plt.title('greater than mean rating')

    plt.subplot(122)
    plt.scatter(reslm["movieid"], reslm["rating"], c=reslm["rating"] * 100, s=res['rating'][:] * 0.1)
    plt.title('less than mean rating')


def figure6():
    # 图6，五个分段的直方图
    fig = plt.figure(6)

    # sns.distplot(res['rating'], bins=5, kde=True)
    plt.hist(res['rating'], bins=[0, 1, 2, 3, 4, 5], edgecolor='white')


def figure7():
    # 分析一下5分的电影的分类
    # 5.0分电影，id-rating
    rating5_0 = np.compress(res['rating'] == 5.0, res)

    # 5.0分电影，title-rating
    film5_0 = extract(rating5_0, i)

    # 5.0分电影，title-genres
    genres5_0 = union(film5_0, iii)
    # 存文件
    # with open('genres5_0.csv', 'w', encoding='cp936', newline='') as f:
    #     writer = csv.writer(f)
    #     for _ in genres5_0:
    #         # print(list(_))
    #         writer.writerow(list(_))

    # 统计5.0分电影的标签以及出现次数，保存到json文件
    # genres5_0count 字典, genres5_0_total列表
    genres5_0count, genres5_0total = countGenres(genres5_0)
    # 保存到文件，已存，将注释
    # with open('genres5_0count.json', 'w', encoding='utf-8') as f:
    #     print(json.dump(genres5_0count, f))

    # 图7，显示5.0电影标签的直方图
    fig = plt.figure(7)

    # 直方图，显示各个标签出现的次数
    plt.subplot(211)

    plt.hist(genres5_0total, bins=len(genres5_0count.keys()), edgecolor='black', facecolor='pink')

    plt.xlabel("movie genres")
    plt.ylabel("count")

    # 饼图，同上显示比例
    plt.subplot(212)

    plt.pie(genres5_0count.values(), explode=None, labels=None, autopct='%2.2f%%', startangle=90,
            labeldistance=1.1)

    plt.legend(genres5_0count.keys(), loc='best')


def figure8():
    # <=1.2超级烂片
    res1_2 = np.compress(res['rating'] <= 1.2, res)
    # 生成词云，依据tag
    # 。。。暂不会

    # <=1.2分电影, title and rating
    film1_2 = extract(res1_2, i)

    # <=1.2分电影，title-genres-rating
    genres1_2 = union2(film1_2, iii)

    # 存文件，使用numpy.savetxt会串行！不知为何
    # with open('genres1_2.csv', 'w', encoding='cp936', newline='') as f:
    #     writer = csv.writer(f)
    #     for _ in genres1_2:
    #         writer.writerow(list(_))


def figure9_10_11():
    '''
    分析，随机抽12个用户，给出这些用户的所有评分
    '''
    # 样本用户
    # userid_sample = np.random.randint(low=int(np.min(userid)), high=int(np.max(userid)), size=4)
    userid_sample = np.random.randint(low=1, high=671, size=12)
    users = []

    for _ in userid_sample:
        condition = iiii['userid'] == _
        # 筛选不到元素
        if np.all(condition == False) == True:
            continue
        users.append(np.compress(condition, iiii))

    # 图9
    plt.figure(9)
    plt.title('user sample')

    plt.subplot(221)
    plt.scatter(np.arange(len(users[0])), users[0]['rating'], s=users[0]['rating']*1)
    plt.title('user ' + str(users[0]['userid'][0]))

    plt.subplot(222)
    plt.scatter(np.arange(len(users[1])), users[1]['rating'], s=users[1]['rating']*1)
    plt.title('user ' + str(users[1]['userid'][1]))

    plt.subplot(223)
    plt.scatter(np.arange(len(users[2])), users[2]['rating'], s=users[2]['rating']*1)
    plt.title('user ' + str(users[2]['userid'][2]))

    plt.subplot(224)
    plt.scatter(np.arange(len(users[3])), users[3]['rating'], s=users[3]['rating']*1)
    plt.title('user ' + str(users[3]['userid'][3]))

    # 图10
    plt.figure(10)
    plt.title('user sample')

    plt.subplot(221)
    plt.scatter(np.arange(len(users[4])), users[4]['rating'], s=users[4]['rating'] * 1)
    plt.title('user ' + str(users[4]['userid'][4]))

    plt.subplot(222)
    plt.scatter(np.arange(len(users[5])), users[5]['rating'], s=users[5]['rating'] * 1)
    plt.title('user ' + str(users[5]['userid'][5]))

    plt.subplot(223)
    plt.scatter(np.arange(len(users[6])), users[6]['rating'], s=users[6]['rating'] * 1)
    plt.title('user ' + str(users[6]['userid'][6]))

    plt.subplot(224)
    plt.scatter(np.arange(len(users[7])), users[7]['rating'], s=users[7]['rating'] * 1)
    plt.title('user ' + str(users[7]['userid'][7]))

    # 图11
    plt.figure(11)
    plt.title('user sample')

    plt.subplot(221)
    plt.scatter(np.arange(len(users[8])), users[8]['rating'], s=users[8]['rating'] * 1)
    plt.title('user ' + str(users[8]['userid'][8]))

    plt.subplot(222)
    plt.scatter(np.arange(len(users[9])), users[9]['rating'], s=users[9]['rating'] * 1)
    plt.title('user ' + str(users[9]['userid'][9]))

    plt.subplot(223)
    plt.scatter(np.arange(len(users[10])), users[10]['rating'], s=users[10]['rating'] * 1)
    plt.title('user ' + str(users[10]['userid'][10]))

    plt.subplot(224)
    plt.scatter(np.arange(len(users[11])), users[11]['rating'], s=users[11]['rating'] * 1)
    plt.title('user ' + str(users[11]['userid'][11]))


# 总体概况
figure1()
figure2()

# 各个分段详情
figure3_4_5()
figure6()

# 5.0分电影
figure7()

# <=1.2 超级烂片，注释掉，暂无图像
# figure8()

# 分析用户及其评分
figure9_10_11()


# 自动调整坐标轴大小
plt.autoscale()

plt.show()