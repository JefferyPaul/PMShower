import pandas as pd
import pymssql


class PMDatabaseSQL:
    def __init__(self):
        conn = pymssql.connect(host='192.168.1.101',
                               user='sa',
                               password='st@s2013',
                               database='SQLServer',
                               charset='utf8')
        cursor = conn.cursor()
        pass

    def db_select(self):
        pass
