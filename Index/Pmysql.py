# coding-utf8
import pymysql
from apiTest.settings import DATABASES
host = DATABASES['default']['HOST']
user = DATABASES['default']['USER']
password = DATABASES['default']['PASSWORD']
port = int(DATABASES['default']['PORT'])
database = DATABASES['default']['NAME']
charset = "utf8"


class Pmysql():
    """python操作mysql的增删改查的封装"""

    def __init__(self):
        """
        初始化参数
        :param host: 主机
        :param user: 用户名
        :param password: 密码
        :param database: 数据库
        :param port: 端口号，默认是3306
        :param charset: 编码，默认是utf8
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self.conn = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database,
                                    port=self.port,
                                    charset=self.charset)

        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def fetchone(self, sql, params=None):
        """
        根据sql和参数获取一行数据
        :param sql: sql语句
        :param params: sql语句对象的参数元组，默认值为None
        :return: 查询的一行数据
        """
        dataOne = None
        try:
            count = self.cur.execute(sql, params)
            if count != 0:
                dataOne = self.cur.fetchone()
        except Exception as ex:
            print(ex)
        finally:
            self.close()
        return dataOne

    def fetchall(self, sql, params=None):

        """
        根据sql和参数获取一行数据
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 查询的一行数据
        """
        dataall = None
        try:
            count = self.cur.execute(sql, params)
            if count != 0:
                dataall = self.cur.fetchall()
        except Exception as ex:
            print(ex)
        finally:
            self.close()
        return dataall

    def __item(self, sql, params=None):

        """
        执行增删改
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        count = 0
        try:
            count = self.cur.execute(sql, params)
            self.conn.commit()
        except Exception as ex:
            print(ex)
        finally:
            self.close()
        return count

    def update(self, sql, params=None):

        """
        执行修改
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        return self.__item(sql, params)

    def insert(self, sql, params=None):

        """
        执行新增
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        return self.__item(sql, params)

    def delete(self, sql, params=None):

        """
        执行删除
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        return self.__item(sql, params)

    def close(self):
        """
        关闭执行工具和连接对象
        """
        if self.cur is not None:
            self.cur.close()
