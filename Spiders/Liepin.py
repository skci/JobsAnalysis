import requests
import parsel
import csv

keys = [
    'Python开发',
    'Java开发',
    '前端开发',
    'PHP开发',
    'C++开发',
    'Android开发',
    '数据库开发',
    'IT产品经理',
    'IT项目经理',
    '软件测试',
    '数据分析',
    'UI设计',
    '互联网营销',
    '算法工程师',
    'IT运维',
    '计算机视觉',
    '人工智能',
    '区块链',
]

# mode = 'w' 覆盖写入; mode = 'a' 追加写入
f = open('../DataClean/Liepin.csv', mode='a', encoding='UTF-8', newline='')
csv_writer = csv.DictWriter(f, fieldnames=[
    '标题',
    '城市',
    '薪资',
    '经验',
    '学历',
    '岗位标签',
    '公司名',
    '公司标签',
    '详情页',
])

# 写入表头
# csv_writer.writeheader()

for key in keys:
    # 1.发送请求
    # 请求URL
    url = 'https://www.liepin.com/zhaopin/'
    # 查询字符串参数
    data = {
        'headId': 'e2abb7875370e0f78ae009333ed5fb5b',
        'ckId': 'wtaxoj1cgwa0dubu3w8t0qrvji77pc09',
        'oldCkId': 'e2abb7875370e0f78ae009333ed5fb5b',
        'fkId': '7b1k9b3dmlgtcilifmz31rxh3kwtzf1b',
        'skId': '7b1k9b3dmlgtcilifmz31rxh3kwtzf1b',
        'sfrom': 'search_job_pc',
        'key': key,
        'currentPage': 0,
        'scene': 'page',
    }
    # 请求标头,伪装模拟
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'
    }

    while True:
        # 请求方法GET
        response = requests.get(url=url, params=data, headers=headers)

        # 2.获取数据
        '''<Response [200]> response响应对象
        200：请求成功 500：服务器问题 404：网址问题
        403：没有访问权限 300：重定向跳转 903：开发人员返回特定状态码
        '''
        # print(response.text)

        # 3.解析数据 css √  xpath ×  re ×
        selector = parsel.Selector(response.text)  # 将response.text数据转换成selector对象
        lis = selector.css('.job-list-item')  # 列表

        for li in lis:
            '''
            attr()属性选择器获取标签内属性 ： attribute
            get()获取第一个标签数据，返回字符串数据类型
            getall()获取多个标签数据，返回列表数据类型
            '''
            # 获取标题
            title = li.css('.job-title-box div:nth-child(1)::attr(title)').get()
            # 获取城市
            city = li.css('.job-dq-box .ellipsis-1::text').get()
            # 获取薪资
            salary = li.css('.job-salary::text').get()
            # 获取标签
            tag_list = li.css('.labels-tag::text').getall()
            # 获取经验要求
            exp = tag_list[0]
            # 获取学历要求
            edu = tag_list[1]
            # 获取其他标签    ','.join(): 把列表里的元素用“,”连接合并成一个字符串数据
            tag = ','.join(tag_list[2:])
            # 获取公司名字
            company_name = li.css('.company-name::text').get()
            # 获取公司标签
            company_tag_list = li.css('.company-tags-box span::text').getall()
            company_tag = ','.join(company_tag_list)
            # 获取详情页
            href = li.css('.job-detail-box a:nth-child(1)::attr(href)').get()

            print(title, city, salary, exp, edu, tag, company_name, company_tag, href)

            # 4.保存数据
            dit = {
                '标题': title,
                '城市': city,
                '薪资': salary,
                '经验': exp,
                '学历': edu,
                '岗位标签': tag,
                '公司名': company_name,
                '公司标签': company_tag,
                '详情页': href,
            }
            csv_writer.writerow(dit)

        # 爬取全部页面
        if not bool(lis):
            break
        else:
            data['currentPage'] += 1
            continue
