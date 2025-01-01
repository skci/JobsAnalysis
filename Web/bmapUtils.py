import grequests
from urllib.parse import quote
import requests


def getlocation(address):
    """
    获取地址的经纬度
    :param address: 地址
    :return: 地址经纬度列表
    """
    ak = '这里填写你的access key(前端)'
    url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(address) + '&output=json&ak=' + ak
    res = requests.get(url)
    data = res.json()
    print(data)
    if data['status'] == 0:
        lng = data['result']['location']['lng'] #获取经度
        lat = data['result']['location']['lat'] #获取纬度
        return [lng,lat]
    else:
        return data['status']


def getlocations(results):
    """
    重写后的grequests异步查询经纬度
    :param results: 地址及海拔元组
    :return: 地址经纬度及报错信息
    """
    urls = []
    task = []
    locations = []
    num = 0

    # admin
    ak1 = '这里填写你的access key1(服务器端)'
    ak2 = '这里填写你的access key2(服务器端)'
    ak3 = '这里填写你的access key3(服务器端)'
    ak4 = '这里填写你的access key4(服务器端)'
    ak5 = '这里填写你的access key5(服务器端)'

    for item in results:
        if num % 5 == 0:
            url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(item[0]) + '&output=json&ak=' + ak1
        elif num % 5 == 1:
            url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(item[0]) + '&output=json&ak=' + ak2
        elif num % 5 == 2:
            url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(item[0]) + '&output=json&ak=' + ak3
        elif num % 5 == 3:
            url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(item[0]) + '&output=json&ak=' + ak4
        else:
            url = 'http://api.map.baidu.com/geocoding/v3/?address=' + quote(item[0]) + '&output=json&ak=' + ak5

        urls.append(url)
        num += 1

    # 每次取第一个url，取完就删除，取光为止
    while urls:
        url = urls.pop(0)
        reqs = grequests.request("GET", url)
        task.append(reqs)

    # 此处map的requests参数是装有实例化请求对象的列表, 其返回值也是列表， size参数可以控制并发的数量
    responses = grequests.map(task)
    # [ < Response[200] >, < Response[200] >, < Response[200] ...

    for i in responses:
        temp = i.json()
        # {'status': 0, 'result': {'location': {'lng': 116.4133836971231

        if temp['status'] == 0:
            lng = temp['result']['location']['lng']  # 获取经度
            lat = temp['result']['location']['lat']  # 获取纬度
            locations.append([lng, lat])
        else:
            locations.append(temp['status'])

    return locations
