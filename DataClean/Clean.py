import pandas as pd
from sqlalchemy import create_engine

# 读取数据文件，转成DataFrame对象
fileNameStr = 'Liepin.csv'
# dtype = str,最好读取的时候都以字符串的形式读入，不然可能会使数据失真
# 比如一个0010008的编号可能会读取成10008
data = pd.read_csv(fileNameStr, encoding='utf-8', dtype=str)

# 没必要，因为读取csv后就是DataFrame类型
df = pd.DataFrame(data)
# DataDF.info()

# 输出全部行，不省略
pd.set_option('display.max_rows', None)

# df.drop(['详情页'], axis=1, inplace=False)

# # 查看重复行
# duplicate_bool = DataDF.duplicated(keep='first')
# repeat = DataDF.loc[duplicate_bool == True]
# print(repeat)

# 对重复行进行清洗。
df.drop_duplicates(subset=['标题','城市','薪资','学历','经验','岗位标签','公司名','公司标签'],inplace=True)

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


clean_df.info()

# 将数据保存到 MySQL 数据库
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/jobsanalysis?charset=utf8')
con = engine.connect()
clean_df.to_sql(name='liepin', con=con, if_exists='replace')  # 'fail'不存储，'replace'替换，'append'追加
con.close()