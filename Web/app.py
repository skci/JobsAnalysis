# 使用render_template返回渲染的模板时，需在项目主目录中加入一个templates目录
import time

from flask import Flask, render_template, request, redirect, url_for
from Web.bmapUtils import getlocations
from Web.getData import Spider, Clean
from Web.sqlUtils import search

# 创建web应用程序
app = Flask(__name__)


# 处理浏览器发送过来的请求
@app.route('/login')
def login():
    """
    登陆页
    :return: login.html 跳转到登录页
    """
    return render_template('login.html')


@app.route('/index')
# @app.route('/')  # 当访问到127.0.0.1：5000/
def index():
    """
    仪表板页（首页）
    1. 统计爬取岗位、城市、公司数量
    2. 获取岗位资历要求雷达图
    3. 获取全国岗位需求热力图
    :return: index.html 跳转到首页
    :return: job_num 岗位数量
    :return: city_num 城市数量
    :return: area_num 地区数量
    :return: company_num 公司数量
    :return: jobs 指定岗位列表
    :return: dit_edus 学历要求
    :return: dit_works 工作经验要求
    :return: edu_max 学历要求最大值
    :return: edu_max 工作要求最大值
    :return: data 热力图数据
    """

    '''
    2. 统计爬取岗位、城市、公司数量 >>> 显示爬取条目
    '''

    # 爬取岗位数量
    job_num = search(
        'SELECT COUNT(job) FROM liepin'
    )[0][0]

    # 爬取城市数量
    city_num = search(
        'SELECT COUNT(DISTINCT city) FROM liepin'
    )[0][0]

    # 爬取城市数量
    area_num = search(
        'SELECT COUNT(DISTINCT address) FROM liepin'
    )[0][0]

    # 爬取公司数量
    company_num = search(
        'SELECT COUNT(DISTINCT company) FROM liepin'
    )[0][0]

    '''
    3. 获取岗位资历要求 >>> 绘制雷达图
    '''

    # 岗位列表
    jobs = [
        'java开发',
        'python开发',
        '数据分析',
        '人工智能',
        '前端开发',
    ]

    work_max = 0
    edu_max = 0
    dit_works = []

    dit_edus = []

    # 通过岗位遍历要求
    for job in jobs:

        # 查询工作经历要求
        results = search(
            'SELECT `work`,COUNT(`work`) FROM liepin WHERE job LIKE \'%' + job + '%\' GROUP BY `work`'
        )
        # (('1-3年', '3098'), ('3-5年', '3098'), ('5-10年', ...

        count_work = [0, 0, 0, 0, 0]

        # 统计各要求数量
        for item in results:
            if item[0] == '经验不限':
                count_work[0] = item[1]
            elif item[0] == '1-3年':
                count_work[1] = item[1]
            elif item[0] == '3-5年':
                count_work[2] = item[1]
            elif item[0] == '5-10年':
                count_work[3] = item[1]
            elif item[0] == '10年以上':
                count_work[4] = item[1]
            else:
                return 0

        # 查询学历要求
        results = search(
            'SELECT edu,COUNT(edu) FROM liepin WHERE job LIKE \'%' + job + '%\' GROUP BY edu'
        )
        # (('本科', '3098'), ('硕士', '3098'), ('博士', ...

        count_edu = [0, 0, 0, 0, 0, 0]

        # 统计各要求数量
        for item in results:
            if item[0] == '学历不限':
                count_edu[0] = item[1]
            elif item[0] == '中专':
                count_edu[1] = item[1]
            elif item[0] == '大专':
                count_edu[2] = item[1]
            elif item[0] == '本科':
                count_edu[3] = item[1]
            elif item[0] == '硕士':
                count_edu[4] = item[1]
            elif item[0] == '博士':
                count_edu[5] = item[1]
            else:
                return 0

        # 取最大值，用于界限图表
        if max(count_work) > work_max:
            work_max = max(count_work)
        if max(count_edu) > edu_max:
            edu_max = max(count_edu)

        # 按echarts要求形式构建数据结构
        dit_work = {
            'value': count_work,
            'name': job,
        }
        dit_edu = {
            'value': count_edu,
            'name': job,
        }
        dit_works.append(dit_work)
        dit_edus.append(dit_edu)

    '''
    4. 获取全国岗位需求 >>> 绘制热力图
    '''

    data = []
    results = search(
        'SELECT address,COUNT(job) FROM liepin GROUP BY address'
    )
    # (('北京', '1286'), ('上海', '1112'), ('深圳'...

    locations = getlocations(results)
    # [[116.4133836971231, 39.910924547299565], [121.48053886017651, 31.235929042252014],
    # print(len(locations))

    # 存储为指定数据结构
    for item in results:
        location = locations.pop(0)
        if type(location) == list:
            dit = {
                "coord": location,
                "elevation": item[1],
            }
        else:
            continue

        data.append(dit)

    # '''
    # 4. 获取全国岗位需求 >>> 绘制热力图
    # '''
    #
    # data = []
    # results = search(
    #     'SELECT address,COUNT(job) FROM liepin GROUP BY address'
    # )
    # # (('北京', '1286'), ('上海', '1112'), ('深圳'...
    #
    #
    # # 存储为指定数据结构
    # for item in results:
    #     location = getlocation(item[0])
    #     # [116.4133836971231, 39.910924547299565]
    #
    #     if type(location) == list:
    #         dit = {
    #             "coord": location,
    #             "elevation": item[1],
    #         }
    #     else:
    #         continue
    #
    #     data.append(dit)

    return render_template('index.html', job_num=job_num, city_num=city_num, area_num=area_num, company_num=company_num,
                           data=data, jobs=jobs, dit_edus=dit_edus, dit_works=dit_works, edu_max=edu_max,
                           work_max=work_max)


@app.route('/table', methods=['GET', 'POST'])
def tables():
    """
    数据展示页
    :return: tables.html 跳转到数据展示页
    :return: dataSet 表格数据
    """
    dataSet = []
    sum = ''
    notice = '没有更多消息...'
    results = search(
        'SELECT job,tag,city,edu,`work`,company,company_tag,CONCAT(salary_low,\'-\',salary_high,\'K\'),url FROM liepin'
    )
    # (('python开发','后端开发','重庆','本科','1-3年','云图软件','行业Saas,A轮,1-49人','10-18K','https://w'), ('java开发'...

    # 存储为指定数据结构
    for item in results:
        item = list(item)
        item[0] = '<a href=' + item.pop(8) + ' target=\"_Blank\">' + item[0] + '</a>'
        dataSet.append(item)

    getData = request.args.to_dict()

    if getData:
        key = getData['key']
        time1 = time.time()
        data = Spider(key)
        time2 = time.time() - time1
        print('爬虫时间' + str(time2))
        Clean(data)
        sum = '1'
        notice = '【' + key + '】' + '爬虫任务已完成！'

    return render_template('tables.html', dataSet=dataSet, sum=sum, notice=notice)


@app.route('/citysalary/<job>')  # 动态路由
def get_citysalary(job):
    """
    获取岗位的城市平均薪资 Top10
    :param job: 指定岗位
    :return: citysalary.html 跳转到城市平均薪资图表页
    :return: city 城市
    :return: high 最高工资
    :return: low 最低工资
    :return: job 指定岗位
    """

    results = search(
        'SELECT city,FORMAT(AVG(salary_high),2),FORMAT(AVG(salary_low),2) FROM liepin '
        'WHERE job LIKE \'%' + job + '%\' GROUP BY city ORDER BY AVG( salary_high ) DESC LIMIT 10'
    )
    # (('北京', '30.98', '18.41'), ('深圳', '29.04', '17.56'), ('上海'...
    city = []
    high = []
    low = []

    for item in results:
        city.append(item[0])
        high.append(item[1])
        low.append(item[2])

    return render_template("citysalary.html", city=city, high=high, low=low, job=job)


@app.route('/expsalary/<job>')  # 动态路由
def get_expsalary(job):
    """
    获取指定岗位学历经验同薪资变化
    :param job: 指定岗位
    :return: 跳转到联动图表页
    :return: source 图表所需数据
    :return: job 指定岗位
    """

    # 学历列表
    edus = [
        '学历不限',
        '中专',
        '大专',
        '本科',
        '硕士',
        '博士',
    ]

    source = [['product', '经验不限', '1-3年', '3-5年', '5-10年', '10年以上']]

    for edu in edus:
        work_salary = [edu, 0, 0, 0, 0, 0]

        results = search(
            'SELECT `work`,FORMAT(AVG(salary_low),2) FROM liepin '
            'WHERE job LIKE \'%' + job + '%\' AND `edu` = \'' + edu + '\' GROUP BY `work`'
        )
        # (('1-3年', '30.98'), ('3-5年', '29.04'), ('5-10年'...

        # 统计各要求数量
        for item in results:
            if item[0] == '经验不限':
                work_salary[1] = item[1]
            elif item[0] == '1-3年':
                work_salary[2] = item[1]
            elif item[0] == '3-5年':
                work_salary[3] = item[1]
            elif item[0] == '5-10年':
                work_salary[4] = item[1]
            elif item[0] == '10年以上':
                work_salary[5] = item[1]
            else:
                return 0

        source.append(work_salary)

    return render_template("expsalary.html", source=source, job=job)


@app.route('/cityjob/<job>')  # 动态路由
def get_cityjobs(job):
    """
    获取城市岗位需求 Top20
    :param job: 指定岗位
    :return: cityjobs.html 跳转到城市岗位需求页面
    :return: job 指定岗位
    :return: data 图表所需数据
    """

    data = []
    results = search(
        'SELECT city,COUNT(job) FROM liepin WHERE job LIKE \'%' + job + '%\' GROUP BY city ORDER BY COUNT( job ) DESC'
    )
    # (('北京', '1286'), ('上海', '1112'), ('深圳'...

    # 存储为指定数据结构
    for item in results:
        dit = {
            'value': item[1],
            'name': item[0],
        }
        data.append(dit)

    return render_template("cityjob.html", job=job, data=data)


@app.route('/jobskill/<job>')  # 动态路由
def get_jobskill(job):
    """
    获取指定岗位的能力要求
    :param job: 指定岗位
    :return: html 跳转到岗位能力要求页面
    :return: job 指定岗位
    :return: data 图表所需数据类型
    """

    dit1 = {}
    dit2 = {}
    results = search(
        'SELECT COUNT(*),SUBSTRING_INDEX(SUBSTRING_INDEX(tag,\',\',help_topic_id+1),\',\',-1)AS a FROM liepin '
        'JOIN mysql.help_topic ON help_topic_id<(LENGTH(tag)-LENGTH(REPLACE(tag,\',\',\'\'))+1) '
        'WHERE job LIKE \'%' + job + '%\' GROUP BY(a) ORDER BY COUNT(*) DESC LIMIT 8'
    )
    # ((292, 'python'), (104, 'mysql'), (75, 'Django'), (64, 'linux'), (
    dit1_max = 0
    for item in results:
        dit1[item[1]] = item[0]
        if dit1_max < item[0]:
            dit1_max = item[0]

    results = search(
        'SELECT COUNT(*),SUBSTRING_INDEX(company_tag,\',\',1) AS a FROM liepin '
        'WHERE job LIKE \'%' + job + '%\' GROUP BY a ORDER BY COUNT(*) DESC LIMIT 8'
    )
    # ((292, '计算机软件'), (104, '互联网'), (75, '电商'), (64, 'IT服务'), (
    dit2_max = 0
    for item in results:
        dit2[item[1]] = item[0]
        if dit2_max < item[0]:
            dit2_max = item[0]

    return render_template("jobskill.html", job=job, dit1=dit1, dit2=dit2, dit1_max=dit1_max, dit2_max=dit2_max)


if __name__ == '__main__':
    app.run(debug=True, threaded=False)  # 启动应用程序>>>启动一个flask项目