from SQL.MSSQL import MSSQL
from SQL.PM_db_sql import *
from PMDataManager.PMData import *
from datetime import datetime
import pandas as pd

'''
	按使用上的理解，我认为
	strategy 应该按portfolio_user 分为benchmark 和 portfolio_user_id，
	这里的portfolio应该是strategy的属性 trader_weight应该是strategy的信息。

	但是目前的PMdb - StrategyDbo 中并没有赋予strategy以portfolio属性，
	而是将portfolio_user_id trader_weight放在PortfolioTraderWeightDbo，没有加入strategy作为key，作为trader的属性，
	这就使得portfolio变成strategy 与 trader之间的一个类别，而不是strategy的一个属性。

	导致，正常的strategy - trader - pnl的链条中，并没有portfolio，
	如果要展示portfolio则需要 strategy - trader - trader_portfolio_weight - pnl -  strategy 的链条，复杂且不连贯，
	后者是 特定地为strategy输入portfolio的信息，而没办法从db中顺畅地获取。

	所以暂且不考虑portfolio的strategy 展示。
	而PMStrategy的设计仍然将portfolio作为strategy的属性。
'''


def is_satisfy(pm_item, filter_condition):
	filter_start_date = filter_condition['start_date']
	filter_end_date = filter_condition['end_date']

	std_start_date = filter_condition.get('std_start_date', filter_start_date)
	std_end_date = filter_condition.get('std_end_date', filter_end_date)
	filter_sharpe = filter_condition['sharpe']
	filter_R = filter_condition['annul_R']
	filter_mdd = filter_condition['mdd']
	filter_count = filter_condition['count']
	filter_s_sharpe = filter_condition['smaller_sharpe']
	filter_s_R = filter_condition['smaller_annul_R']
	filter_l_mdd = filter_condition['larger_mdd']
	filter_s_count = filter_condition['smaller_count']

	des = pm_item.describe(use_std=True, start_date=filter_start_date, end_date=filter_end_date,
	                        std_start_date=std_start_date, std_end_date=std_end_date)
	count = int(des['count'])
	sharpe = float(des['sharpe'])
	mdd = float(des['mdd'])
	annu_R = float(des['annual_return'])

	if str(filter_sharpe).isdigit():
		if not filter_s_sharpe:
			if sharpe < filter_sharpe:
				return False
		else:
			if sharpe > filter_sharpe:
				return False

	if str(filter_R).isdigit():
		if not filter_s_R:
			if annu_R < filter_R:
				return False
		else:
			if annu_R > filter_R:
				return False

	if str(filter_count).isdigit():
		if not filter_s_count:
			if count < filter_count:
				return False
		else:
			if count > filter_count:
				return False

	if str(filter_mdd).isdigit():
		if not filter_l_mdd:
			if mdd > filter_mdd:
				return False
		else:
			if mdd < filter_mdd:
				return False
	return True


def strategy_filter(df_strategy_info, df_trader_info, df_trader_pnl, list_filter_condition):
	print('set strategy: ', datetime.strftime(datetime.now(), '%H:%M:%S'))
	df_strategy_info = pd.DataFrame(df_strategy_info, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
	df_trader_info = pd.DataFrame(df_trader_info, columns=['TraderId', 'StrategyId'])
	df_trader_pnl = pd.DataFrame(df_trader_pnl,
	                             columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	dict_strategy = {}
	for i in df_strategy_info.index:
		strategy_info = df_strategy_info.loc[i, :]
		strategy_id = strategy_info['Id']
		print('%s: ' % strategy_id, datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		list_traders_id = df_trader_info.loc[df_trader_info['StrategyId'] == strategy_id, 'TraderId'].tolist()
		obj_strategy = PMStrategy(Id=strategy_id, list_traders_id=list_traders_id)
		obj_strategy.set_strategy(df_trader_pnl)

		is_satisfy_i = 1
		for filter_condition_i in list_filter_condition:
			if not is_satisfy(obj_strategy, filter_condition_i):
				print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Not Satisfy')
				is_satisfy_i = 0
				break
		if is_satisfy_i != 1:
			continue
		dict_strategy[strategy_id] = obj_strategy
		print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Satisfy')
	print('All Done:    ', datetime.strftime(datetime.now(), '%H:%M:%S'))
	return dict_strategy


def trader_filter(df_trader_info, df_trader_pnl, list_filter_condition):
	print('set trader: ', datetime.strftime(datetime.now(), '%H:%M:%S'))
	df_trader_pnl = pd.DataFrame(
		df_trader_pnl,
		columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns']
	)

	dict_trader = {}
	list_trader_id = df_trader_info['TraderId'].tolist()
	for i_trader_id in list_trader_id:
		print('%s: ' % i_trader_id, datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		i_trader_belong_strategy_id = df_trader_info.loc[df_trader_info['TraderId']==i_trader_id, 'StrategyId'].tolist()[0]
		obj_trader = PMTrader(i_trader_id, belong_strategy_id=i_trader_belong_strategy_id)
		obj_trader.set_trader_pnl(df_trader_pnl.loc[df_trader_pnl['TraderId'] == i_trader_id])

		is_satisfy_i = 1
		for filter_condition_i in list_filter_condition:
			if not is_satisfy(obj_trader, filter_condition_i):
				print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Not Satisfy')
				is_satisfy_i = 0
				break
		if is_satisfy_i == 0:
			continue
		dict_trader[i_trader_id] = obj_trader
		print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Satisfy')
	print('Satisfy Check Done:    ', datetime.strftime(datetime.now(), '%H:%M:%S'))
	return dict_trader
