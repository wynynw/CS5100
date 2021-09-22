# coding:utf-8
import random
import datetime
import matplotlib.pyplot as plt
import math


file = open("49_cities.txt", "r")
#file = open("cities_full.txt", "r")
data = file.readlines()
city_list=[]
for i in range(1,len(data)):
    data[i] = data[i].strip('\n')
    name = data[i].split(",")[0]
    value = [float(data[i].split(",")[1]),float(data[i].split(",")[1])]
    city_list.append([name,value])


def calcDist(x,y):
    '''
    :param x: the longitude and latitude of a city
    :param y: the longitude and latitude of another city
    :return: the distance between the two cities
    '''
    dist = math.sqrt((y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2)
    return dist

def path_len(city):
    '''
    :param city: a path order of cities
    :return: the total distance
    '''
    path_dis = 0
    for i in range(len(city)):
        two_dis = calcDist(city[i][1],city[i-1][1])  # 两点距离
        path_dis += two_dis
    return path_dis

def desent(city):
    '''
    :param city: an array of cities
    :return: cities as the steepest ascent order
    '''
    flag = 0
    j=0
    path_dis = float("inf")
    while j<len(city):
        for i in range(len(city)):
            two_dis = calcDist(city[j][1],city[i-1][1])  # 两点距离
            if path_dis < two_dis:
                path_dis = two_dis
                flag = i
        a = city[j]
        city[j] = city[flag]
        city[flag] = a
        j+=1
    return city

def change_path(city, i):
    '''
    :param city: an array of cities
    :param i: random value
    :return: changed array of cities
    '''
    path_new=[]
    for c in city:
        path_new.append(c)
    temp = path_new[0]
    path_new[0] = path_new[i]
    path_new[i] = temp
    return path_new


def hillClimbing(city):
    '''
    :param city: an array of cities
    :return: the path of hill climbing algorithms
    '''
    n = len(city)
    get_new_path = city
    old_len = path_len(city)
    count = 0
    while count < n*n:
        i = random.randint(0, n - 1)
        path_new = change_path(city, i)
        path_desent = desent(path_new)
        count += 1
        if path_len(path_desent) < old_len:
            old_len=path_len(path_desent)
            get_new_path=path_desent
    if get_new_path == city:
        return city
    else:
        return get_new_path

def best_path(path):
    '''
    :param path: an array of cities
    :return: the set of all the optimal distances
    '''
    path0=path
    nums=0
    flag = 0
    pathBetter=[]
    dis_list= []
    dis_better = float('inf')
    start = datetime.datetime.now()
    time = datetime.datetime.now()
    while nums<100:
        if flag == 0:
            start = datetime.datetime.now()
            flag=1
        path_better=hillClimbing(path)
        nums+=1
        print("iterations:"+str(nums))
        if path_better == path:
            dis=path_len(path_better)
            dis_list.append([nums,dis])
            end = datetime.datetime.now()
            if dis < dis_better:
                dis_better = dis
                pathBetter = path_better
                time = end - start
            path=path0
            a = path.index(path_better[len(path_better)-1])
            b = path[a]
            path[a]=path[0]
            path[0]=b
            flag = 0
        else:
            path=path_better
        if (nums)%2000 == 0:
            path = path0
            a = path.index(path_better[len(path_better) - 1])
            b = path[a]
            path[a] = path[0]
            path[0] = b
            for i in range(len(pathBetter)):
                if len(pathBetter[i]) ==2:
                    pathBetter[i] = pathBetter[i][0]
            with open("output.txt", "a") as f:
                output = str(path_len(path_better)) + "," + "-".join(pathBetter) + "," + str(dis_better) + "," + str(time) + "\n"
                f.write(output)
    return dis_list

if __name__ == '__main__':
    dis_list=best_path(city_list)
    plt.figure()
    x=[]
    y=[]
    for i in range(len(dis_list)):
        x.append(dis_list[i][0])
        y.append(dis_list[i][1])
    plt.plot(x,y)
    plt.title('Best solutions of 49_cities with steepest ascent HC')
    plt.show()


