from SQL.MSSQL import MSSQL
from PMDataManager.PMData import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"
	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)

	trader = PMTrader(Id='DLjm@192.168.1.16@29005')
	trader.set_start_date(datetime(2018, 10, 1))

	strategy = PMStrategy(Id='China.Commodities.Id002022E', portfolio_user_id='Jeffery')
	strategy.set_start_date(datetime(2018, 10, 1))
