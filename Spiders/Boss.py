from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
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

f = open('../DataClean/Boss.csv', mode='a', encoding='UTF-8', newline='')
csv_writer = csv.DictWriter(f, fieldnames=[
    '标题',
    '城市',
    '薪资',
    '经验',
    '学历',
    '岗位标签',
    '公司名',
    '公司标签',
    '公司福利',
    '详情页',
])
# 写入表头
csv_writer.writeheader()

# selenium爬取速度相对较慢>>>模拟人的行为去操作浏览器
# 极大程度减少被反爬，requests虽快，但如果某网站有JS逆向加密，解密会花更多时间
driver = webdriver.Edge('D:\Codes\Python\Spider\Boss\msedgedriver.exe')  # 实例化浏览器对象
# driver.get('https://www.zhipin.com/c100010000/?query=' + key + '&page=' + str(page))

# # 设置隐式等待，如果元素加载出来就执行，没加载出来就等，10秒不出报异常
# driver.implicitly_wait(10)
# # 搜索指定关键字，通过xpath或css选择器
# driver.find_element_by_css_selector('.ipt-search').send_keys(key)
# # driver.find_element_by_css_selector('.btn.btn-search').click() #反爬，使用键盘操作
# driver.find_element_by_css_selector('.ipt-search').send_keys(Keys.ENTER)

# 循环搜索关键词
for key in keys:
    page = 1  # 首页

    # 循环访问page+1
    while True:
        driver.get('https://www.zhipin.com/c100010000/?query=' + key + '&page=' + str(page))

        # 获取岗位卡片
        driver.implicitly_wait(10)
        lis = driver.find_elements_by_css_selector('.job-list li')
        for li in lis:
            title = li.find_element_by_css_selector('.job-name a').text  # 标题
            city = li.find_element_by_css_selector('.job-area').text  # 城市
            salary = li.find_element_by_css_selector('.job-limit .red').text  # 薪资
            limit = str(li.find_element_by_css_selector('.job-limit p').get_attribute('innerHTML')) \
                .split('<em class="vline"></em>')  # 要求
            exp = limit[0]  # 经验
            edu = limit[1]  # 学历

            spans = li.find_elements_by_css_selector('.tag-item')  # 标签列表

            tags = []
            for span in spans:
                tags.append(span.text)
            tag = ','.join(tags)  # 岗位标签

            company_name = li.find_element_by_css_selector('.name a').text  # 公司名
            company_tag = li.find_element_by_css_selector('.false-link').text  # 公司标签
            desc = li.find_element_by_css_selector('.info-desc').text  # 公司福利
            href = li.find_element_by_css_selector('.job-name a').get_attribute('href')  # 详情页
            print(title, city, salary, exp, tag, company_name, company_tag, href)
            dit = {
                '标题': title,
                '城市': city,
                '薪资': salary,
                '经验': exp,
                '学历': edu,
                '岗位标签': tag,
                '公司名': company_name,
                '公司标签': company_tag,
                '公司福利': desc,
                '详情页': href,
            }
            csv_writer.writerow(dit)
        page += 1

        # 通过检测翻页按钮判断当前关键词是否查询完毕
        if driver.find_element_by_css_selector('.page a:last-child').get_attribute('class') == 'next disabled':
            break

driver.close()
