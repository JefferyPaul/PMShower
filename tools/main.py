from SQL.MSSQL import MSSQL
from PMDataManager.PMData import *
from datetime import datetime
import pandas as pd


def test_trader():
	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"

	trader = PMTrader(Id='DLjm@192.168.1.16@29005')
	trader.set_start_date(datetime(2018, 10, 1))

	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	re_sql = mssql.ExecQuery(trader.get_pnl_sql())
	if type(re_sql) == dict or type(re_sql) == list:
		df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
		print(df.head())

	mssql.close()


def test_strategy():
	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"

	strategy = PMStrategy(Id='China.Commodities.Pattern.T2N')
	strategy.set_start_date(datetime(2018, 10, 1))

	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	sql = strategy.get_traders_sql()
	re_sql = mssql.ExecQuery(sql=sql)
	strategy.set_strategy_traders(re_sql)
	sql = strategy.get_portfolio_sql()
	re_sql = mssql.ExecQuery(sql=sql)
	print(re_sql)

	mssql.close()


if __name__ == '__main__':
	test_strategy()
