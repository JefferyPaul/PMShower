from SQL.MSSQL import MSSQL
from PMDataManager.PMData import *
from datetime import datetime
import pandas as pd


if __name__ == '__main__':
	# pd.set_option('display.height', 1000)
	# pd.set_option('display.max_rows', 500)
	# pd.set_option('display.max_columns', 500)
	pd.set_option('display.width', 1000)

	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"

	trader = PMTrader(Id='DLjm@192.168.1.16@29005')
	trader.set_start_date(datetime(2018, 10, 1))

	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	re_sql = mssql.ExecQuery(trader.get_pnl_sql())
	if type(re_sql) == dict or type(re_sql) == list:
		df = pd.DataFrame(re_sql)
		print(df.head())

	mssql.close()