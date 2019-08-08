import pandas as pd
import numpy as np
from PMDataManager.SQL.MSSQL import MSSQL


def get_db_data():
	mssql = MSSQL(host='192.168.1.101', user='sa', pwd='st@s2013', db='Platinum.PM')
	func_sql_exec = mssql.ExecQuery
	# 1
	sql = '''
			SELECT[Id],[Type],[Name]
		    FROM [Platinum.PM].[dbo].[StrategyDbo]
		'''
	re_sql = func_sql_exec(sql)
	if len(re_sql) < 0:
		print('no strategy info')
	df_strategy_info = pd.DataFrame(re_sql, columns=['Id', 'Type', 'Name'])

	# 2
	sql = '''
			SELECT[Id],[StrategyId]
		    FROM [Platinum.PM].[dbo].[TraderDbo]
		'''
	re_sql = func_sql_exec(sql)
	if len(re_sql) < 0:
		print('no trader info')
	df_trader_info = pd.DataFrame(re_sql, columns=['Id', 'StrategyId'])

	# 3
	sql = '''
			SELECT[Date],[TraderId],[Pnl],[Commission]
			  FROM [Platinum.PM].[dbo].[TraderLogDbo]
			  WHERE date>'20180101'
		'''
	re_sql = func_sql_exec(sql)
	if len(re_sql) < 0:
		print('no trader pnl')
	df_trader_pnl = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission'])

	mssql.close()
	return df_strategy_info, df_trader_info, df_trader_pnl


def identify():
	# 1,strategy info identify
	def set_strategy_data_type(i):
		if len(i.split('.')) >= 3:
			return i.split('.')[2]
		else:
			return ''
	df_strategy_info['DataType'] = df_strategy_info['Type'].apply(set_strategy_data_type)

	def set_strategy_trading_type(i):
		if len(i.split('.')) >= 4:
			return i.split('.')[3]
		else:
			return ''
	df_strategy_info['TradingType'] = df_strategy_info['Type'].apply(set_strategy_trading_type)

	def set_strategy_model_id(i):
		if len(i.split('.')) >= 2:
			if i.split('.')[1] != 'X':
				return i.split('.')[1]
			else:
				if len(i.split('.')) >= 3:
					return 'X.' + i.split('.')[2]
				else:
					return ''
	df_strategy_info['ModelId'] = df_strategy_info['Name'].apply(set_strategy_model_id)

	def set_strategy_trading_range(i):
		if len(i.split('.')) >= 2:
			return '.'.join([i.split('.')[0], i.split('.')[1]])
		else:
			return ''
	df_strategy_info['TradingRange'] = df_strategy_info['Type'].apply(set_strategy_trading_range)

	# 2,trader info identify
	def set_trader_trading_object(i):
		if i.find("@") <= -1:
			return ''
		else:
			tobj = i.split("@")[0]
			l_tobj = []
			l_tobj.append(tobj)
			if tobj.find("_") > -1:
				l_tobj += tobj.split("_")
			return ','.join(l_tobj)
	df_trader_info['TradingObject'] = df_trader_info['Id'].apply(set_trader_trading_object)

	# 3,trader pnl info
	l_comm_ratio = []
	df_trader_pnl['absPnl'] = df_trader_pnl['Pnl'].apply(np.abs)
	for i_trader_id in df_trader_info['Id'].tolist():
		df_pnl_i = df_trader_pnl[df_trader_pnl['TraderId'] == i_trader_id]
		sum_pnl = sum(df_pnl_i['absPnl'].tolist())
		sum_comm = sum(df_pnl_i['Commission'].tolist())
		if sum_pnl > 0:
			comm_ratio = round(sum_comm / sum_pnl, 3)
			l_comm_ratio.append(comm_ratio)
		else:
			l_comm_ratio.append('')
	df_trader_info['Freq'] = l_comm_ratio


def update_db():
	pass


def output_csv():
	df_strategy_info.to_csv('./strategyInfo.csv')
	df_trader_info.to_csv('./traderInfo.csv')


if __name__ == '__main__':
	df_strategy_info, df_trader_info, df_trader_pnl = get_db_data()
	identify()
	output_csv()
