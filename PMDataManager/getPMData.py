from PMDataManager.SQL import MSSQL, PMDbSql
from datetime import datetime


def init_mssql(dict_db_info):
	db = dict_db_info['db']
	host = dict_db_info['host']
	user = dict_db_info['user']
	pwd = dict_db_info['pwd']

	mssql = MSSQL.MSSQL(host=host, user=user, pwd=pwd, db=db)
	func_sql_exec = mssql.ExecQuery
	return mssql, func_sql_exec


# 获取指定strategy_type     的strategy trader 的info和pnl
def strategy_type_get_data(dict_db_info, list_strategy_type, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	# 初始化mssql引擎
	mssql, func_sql_exec = init_mssql(dict_db_info)

	try:
		if len(list_strategy_type) == 0:
			return
	except:
		return

	# 通过strategy_type获取strategy_info strategy_id
	df_strategy_info = PMDbSql.strategy_type_get_strategy_info(list_strategy_type, func_sql_exec)
	if not(len(df_strategy_info) > 0):
		print('select strategy type-strategy Wrong')
		return
	list_strategy_id = df_strategy_info['Id'].tolist()

	# 通过strategy_id获取trader_info trader_id
	df_trader_info = PMDbSql.strategy_get_trader_info(list_strategy_id, func_sql_exec)
	if not(len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()

	# 通过trader_id获取trader_pnl
	print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
	df_trader_pnl = PMDbSql.trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not(len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return
	print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl


# 获取指定strategy_id       的strategy trader的 info和pnl
def strategy_id_get_data(dict_db_info, list_strategy_id, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	# 初始化mssql
	mssql, func_sql_exec = init_mssql(dict_db_info)

	try:
		if len(list_strategy_id) == 0:
			return
	except:
		return

	# 通过strategy_id获取strategy_info
	df_strategy_info = PMDbSql.strategy_id_get_strategy_info(list_strategy_id, func_sql_exec)
	if not (len(df_strategy_info) > 0):
		print('select strategy type-strategy Wrong')
		return

	# 通过strategy_info获取trader_info
	df_trader_info = PMDbSql.strategy_get_trader_info(list_strategy_id, func_sql_exec)
	if not (len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()

	# 通过trader_info获取trader_pnl
	print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
	df_trader_pnl = PMDbSql.trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not (len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return
	print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl


# 获取指定trader_id         的trader info和pnl
def trader_id_get_data(dict_db_info, list_strategy_id, list_trader_id, start_date=datetime(2015, 1, 1), end_date=datetime.today()):
	mssql, func_sql_exec = init_mssql(dict_db_info)
	try:
		if len(list_strategy_id) == 0 or len(list_trader_id) == 0:
			return
	except:
		return

	df_strategy_info = PMDbSql.strategy_id_get_strategy_info(list_strategy_id, func_sql_exec)
	# if not (len(df_strategy_info) > 0):
	# 	print('select strategy type-strategy Wrong')
	# 	return

	df_trader_info = PMDbSql.trader_get_trader_info(list_trader_id, func_sql_exec)
	if not (len(df_trader_info) > 0):
		print('select strategy-trader Wrong')
		return
	df_trader_pnl = PMDbSql.trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
	if not (len(df_trader_pnl) > 0):
		print('select trader-pnl Wrong')
		return

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl
