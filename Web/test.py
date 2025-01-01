import grequests
import requests
import parsel
import pandas as pd
from sqlalchemy import create_engine


def Spider(key):
    """
    爬虫模块
    :param key: 爬取关键字
    :return: df: 爬取数据（DataFrame）
    """
    # 创建Pandas DataFrame表头
    df = pd.DataFrame(
        columns=[
            '标题',
            '城市',
            '薪资',
            '经验',
            '学历',
            '岗位标签',
            '公司名',
            '公司标签',
            '详情页'
        ]
    )

    task = []   # 异步任务
    lis = []    #职位卡片列表

    # 1.发送请求
    # 请求URL
    url = 'https://www.liepin.com/zhaopin/'
    # 请求标头,伪装模拟
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'
    }

    # 每页分配一个爬虫任务
    for i in range(10):
        # 查询字符串参数
        data = {'key': key, 'currentPage': i}
        reqs = grequests.request("GET", url=url, params=data, headers=headers)
        task.append(reqs)


    # 此处imap的requests参数是装有实例化请求对象的列表, 其返回值也是列表， size参数可以控制并发的数量
    responses = grequests.imap(task, size=10)
    # [ < Response[200] >, < Response[200] >, < Response[200] ...


    for response in responses:

        # 2.获取数据
        '''<Response [200]> response响应对象
        200：请求成功 500：服务器问题 404：网址问题
        403：没有访问权限 300：重定向跳转 903：开发人员返回特定状态码
        '''
        # print(response.text)

        # 3.解析数据 css √  xpath ×  re ×
        selector = parsel.Selector(response.text)   # 将response.text数据转换成selector对象
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

            print(title
                  #, city, salary, exp, edu, tag, company_name, company_tag, href
                  )

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

            # 将此行数据添加到Pandas DataFrame
            df = df.append(dit, ignore_index=True)

    return df


def Clean(df):
    """
    数据清洗模块
    :param df: 需要清洗的数据
    :return: 将数据存储到数据库中
    """
    # 输出全部行，不省略
    pd.set_option('display.max_rows', None)

    # 对重复行进行清洗。
    df.drop_duplicates(subset=['标题', '城市', '薪资', '学历', '经验', '岗位标签', '公司名', '公司标签'], inplace=True)

    # `城市`预处理。北京-朝阳区 >>> 北京，朝阳区。分成2个字段   <Renew> 要求：北京-朝阳区 >>> 北京。分隔出城市
    # area_df = df['城市'].str.split('-', expand=True)
    # area_df = area_df.rename(columns={0: 'city', 1: 'district'})
    df['address'] = df['城市']
    df['city'] = df['城市'].str.split('-', expand=True)[0]

    # `薪资`预处理。10-20K·15薪 >>> salary_low：10，salary_high：20
    salary_df = df['薪资'].str.split('k', expand=True)[0].str.split('-', expand=True)
    salary_df = salary_df.rename(columns={0: 'salary_low', 1: 'salary_high'})

    # `经验`预处理。经验不限 ：0，1-3年：1，3-5年：2，5-10年：3，10年以上:4
    def Work(year):
        if year in '1-3年':
            return '1-3年'
        elif year in '3-5年':
            return '3-5年'
        elif year in '5-10年':
            return '5-10年'
        elif year in '10年以上':
            return '10年以上'
        else:
            return '经验不限'

    df['work'] = df['经验'].apply(lambda year: Work(year))

    # `学历`预处理。学历不限 ：0，中专/中技及以上 ：1，大专及以上 ：2，本科及以上：3，硕士及以上：4，博士：5
    def Edu(edu):
        technical = ['中专/中技', '中专/中技及以上']
        junior = ['大专', '大专及以上']
        undergraduate = ['统招本科', '本科', '本科及以上']
        master = ['硕士', '硕士及以上']
        doctor = ['博士']

        if edu in technical:
            return '中专'
        elif edu in junior:
            return '大专'
        elif edu in undergraduate:
            return '本科'
        elif edu in master:
            return '硕士'
        elif edu in doctor:
            return '博士'
        else:
            return '学历不限'

    df['edu'] = df['学历'].apply(lambda edu: Edu(edu))

    # 重命名表头
    df.rename(columns={'标题': 'job', '岗位标签': 'tag', '公司名': 'company', '公司标签': 'company_tag', '详情页': 'url'},
              inplace=True)

    # 合并数据集
    clean_df = pd.concat([df, salary_df], axis=1)

    # 删除冗余列
    clean_df.drop(['学历', '经验', '薪资', '城市'], axis=1, inplace=True)  # 删除原区域
    # # 删除无关列
    # clean_df.drop(['公司标签'], axis=1, inplace=True)

    # 按行（axis=0）清洗缺省数据，“any”表示只要带了缺省值就删除所在的行/列，“all”表示全部缺省才删除
    clean_df.dropna(axis=0, how='any', inplace=True)

    # 将数据保存到 MySQL 数据库
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/jobsanalysis?charset=utf8')
    con = engine.connect()

    # 读取数据库信息
    sql_df = pd.read_sql(
        'SELECT job,tag,company,company_tag,url,address,city,work,edu,salary_low,salary_high FROM liepin', con=con)

    # 合并数据集
    clean_df = pd.concat([clean_df, sql_df], axis=0)

    # 删除重复数据
    clean_df.drop_duplicates(
        subset=['job', 'tag', 'company', 'company_tag', 'address', 'city', 'work', 'edu', 'salary_low', 'salary_high'],
        inplace=True)

    # 查看df信息
    # clean_df.info()

    # 存入数据库
    clean_df.to_sql(name='data1', con=con, if_exists='replace')  # 'fail'不存储，'replace'替换，'append'追加
    con.close()
