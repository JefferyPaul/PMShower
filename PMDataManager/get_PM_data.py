from SQL.MSSQL import MSSQL
from SQL.PM_db_sql import *
from datetime import datetime
import pandas as pd


def init_mssql(dict_db_info):
	db = dict_db_info['db']
	host = dict_db_info['host']
	user = dict_db_info['user']
	pwd = dict_db_info['pwd']

	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	func_sql_exec = mssql.ExecQuery
	return mssql, func_sql_exec


def strategy_type_get_data(dict_db_info, list_strategy_type, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	mssql, func_sql_exec = init_mssql(dict_db_info)

	try:
		if len(list_strategy_type) == 0:
			return
	except:
		return

	df_strategy_info = strategy_type_get_strategies(list_strategy_type, func_sql_exec)
	if not(len(df_strategy_info) > 0):
		print('select strategy type-strategy Wrong')
		return
	list_strategy_id = df_strategy_info['Id'].tolist()

	df_trader_info = strategy_get_trader_info(list_strategy_id, func_sql_exec)
	if not(len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()

	# df_trader_weight = trader_get_weight(list_trader_id, func_sql_exec)
	# if not(len(df_trader_weight) > 0):
	# 	print('select trader-weight Wrong')
	# 	return
	# df_trader_weight = pd.DataFrame(df_trader_weight, columns=['Date', 'TraderId', 'Weight'])

	print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
	df_trader_pnl = trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not(len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return
	print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl


def strategy_id_get_data(dict_db_info, list_strategy_id, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	mssql, func_sql_exec = init_mssql(dict_db_info)

	try:
		if len(list_strategy_id) == 0:
			return
	except:
		return

	df_strategy_info = strategy_get_strategy_info(list_strategy_id, func_sql_exec)
	if not (len(df_strategy_info) > 0):
		print('select strategy type-strategy Wrong')
		return

	df_trader_info = strategy_get_trader_info(list_strategy_id, func_sql_exec)
	if not (len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()

	print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
	df_trader_pnl = trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not (len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return
	print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl


def trader_id_get_data(dict_db_info, list_strategy_id, list_trader_id, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	mssql, func_sql_exec = init_mssql(dict_db_info)
	try:
		if len(list_strategy_id) == 0 or len(list_trader_id) == 0:
			return
	except:
		return

	df_strategy_info = strategy_get_strategy_info(list_strategy_id, func_sql_exec)
	# if not (len(df_strategy_info) > 0):
	# 	print('select strategy type-strategy Wrong')
	# 	return

	df_trader_info = trader_get_trader_info(list_trader_id, func_sql_exec)
	if not (len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	df_trader_pnl = trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not (len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl

