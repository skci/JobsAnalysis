import pymysql


def getconnect():
    """
    连接数据库
    :return: con 数据连接对象
    """

    con = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='123456',
        db='jobsanalysis',
        charset='utf8'
    )

    return con


def search(sql_str):
    """
    查询多个结果，返回元组对象
    :param sql_str: sql语句
    :return: result 数据库查询结果
    """

    # 获取数据库连接对象
    con = getconnect()

    # 游标
    cur = con.cursor()
    cur.execute(sql_str)

    # 每执行一次取结果中的一行
    result = cur.fetchall()

    # 销毁
    cur.close()
    con.close()
    return result
