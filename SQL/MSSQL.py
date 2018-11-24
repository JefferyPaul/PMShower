import pymssql


class MSSQL:
    def __init__(self, host, user, pwd, db):  # 类的构造函数，初始化数据库连接ip或者域名，以及用户名，密码，要连接的数据库名称
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = pymssql.connect(host=self.host,
                                    user=self.user,
                                    password=self.pwd,
                                    database=self.db,
                                    charset='utf8')

    def close(self):
        self.conn.close()

    # 执行查询语句,返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
    def ExecQuery(self, sql):
        cur = self.conn.cursor()
        if not cur:
            raise(NameError, "连接数据库失败")
        else:
            pass
        cur.execute(sql)
        resList = cur.fetchall()
        return resList

    def ExecNonQuery(self, sql):
        cur = self.conn.cursor()
        if not cur:
            raise(NameError, "连接数据库失败")
        else:
            pass
        cur.execute(sql)
        self.conn.commit()

    # def __GetConnect(self):  # 得到数据库连接信息函数， 返回: conn.cursor()
    #     self.conn = pymssql.connect(host=self.host,
    #                                 user=self.user,
    #                                 password=self.pwd,
    #                                 database=self.db,
    #                                 charset='utf8')
    #     cur = self.conn.cursor()  # 将数据库连接信息，赋值给cur。
    #     if not cur:
    #         raise(NameError, "连接数据库失败")
    #     else:
    #         return cur
