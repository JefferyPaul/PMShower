from SQL.MSSQL import MSSQL
from PMDataManager.PM_Data import *
from PMDataManager.PM_Class import *
from datetime import datetime
import pandas as pd
from pyecharts import Line, Grid
import os


def get_db_data(db_info, filter_item, start_date, end_date):
	db = db_info['db']
	host = db_info['host']
	user = db_info['user']
	pwd = db_info['pwd']
	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	func_sql_exec = mssql.ExecQuery

	filter_type = filter_item['type']
	list_filter_item = filter_item['item']

	if filter_type == '1':
		list_strategy_type = list_filter_item

		print('strategy_type_get_strategies : ', datetime.strftime(datetime.now(),'%H:%M:%S'), end='')
		df_strategy_info = strategy_type_get_strategies(list_strategy_type, func_sql_exec)
		if not(len(df_strategy_info) > 0):
			print('select strategy type-strategy Wrong')
			return
		list_strategy_id = df_strategy_info['Id'].tolist()
		print('    ', datetime.strftime(datetime.now(),'%H:%M:%S'))

		print('strategy_get_trader : ', datetime.strftime(datetime.now(),'%H:%M:%S'), end='')
		df_trader_info = strategy_get_trader(list_strategy_id, func_sql_exec)
		if not(len(df_trader_info) > 0):
			print('select strategy-trader Wrong')
			return
		list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()
		print('    ', datetime.strftime(datetime.now(),'%H:%M:%S'))

		# df_trader_weight = trader_get_weight(list_trader_id, func_sql_exec)
		# if not(len(df_trader_weight) > 0):
		# 	print('select trader-weight Wrong')
		# 	return
		# df_trader_weight = pd.DataFrame(df_trader_weight, columns=['Date', 'TraderId', 'Weight'])
		print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(),'%H:%M:%S'), end='')
		df_trader_pnl = trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
		if not(len(df_trader_pnl) > 0):
			print('select trader-pnl Wrong')
			return
		print('    ', datetime.strftime(datetime.now(),'%H:%M:%S'))

		mssql.close()
		return df_strategy_info, df_trader_info, df_trader_pnl
	elif filter_type == '2':
		list_strategy_id = list_filter_item

		print('strategy_type_get_strategies : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		df_strategy_info = strategy_get_strategy_info(list_strategy_id, func_sql_exec)
		if not (len(df_strategy_info) > 0):
			print('select strategy type-strategy Wrong')
			return
		print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

		print('strategy_get_trader : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		df_trader_info = strategy_get_trader(list_strategy_id, func_sql_exec)
		if not (len(df_trader_info) > 0):
			print('select strategy-trader Wrong')
			return
		list_trader_id = df_trader_info.loc[:, 'TraderId'].tolist()
		print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

		print('trader_get_trader_pnl : ', datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		df_trader_pnl = trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date)
		if not (len(df_trader_pnl) > 0):
			print('select trader-pnl Wrong')
			return
		print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'))

		mssql.close()
		return df_strategy_info, df_trader_info, df_trader_pnl
	else:
		print('filter type input Wrong')
		return


def strategy_filter(filter_condition, df_strategy_info, df_trader_info, df_trader_pnl):
	def is_satisfy(strategy):
		des = strategy.describe(cal_std=True)
		count = int(des['count'])
		sharpe = float(des['sharpe'])
		mdd = float(des['mdd'])
		annu_R = float(des['annual_return'])

		filter_sharpe = filter_condition['sharpe']
		filter_R = filter_condition['annul_R']
		filter_mdd = filter_condition['mdd']
		filter_count = filter_condition['count']
		filter_s_sharpe = filter_condition['smaller_sharpe']
		filter_s_R = filter_condition['smaller_annul_R']
		filter_l_mdd = filter_condition['larger_mdd']
		filter_s_count = filter_condition['smaller_count']

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

	df_strategy_info = pd.DataFrame(df_strategy_info, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
	df_trader_info = pd.DataFrame(df_trader_info, columns=['TraderId', 'StrategyId'])
	df_trader_pnl = pd.DataFrame(df_trader_pnl, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	print('set strategy: ', datetime.strftime(datetime.now(), '%H:%M:%S'))
	dict_strategy = {}
	for i in df_strategy_info.index:
		strategy_info = df_strategy_info.loc[i, :]
		strategy_id = strategy_info['Id']
		print('%s: ' % strategy_id, datetime.strftime(datetime.now(), '%H:%M:%S'), end='')
		obj_strategy = PMStrategy(strategy_id)
		obj_strategy.list_traders_id = df_trader_info.loc[df_trader_info['StrategyId']==strategy_id, 'TraderId'].tolist()
		for trader_id in obj_strategy.list_traders_id:
			obj_trader = PMTrader(trader_id)
			obj_trader.pnl = df_trader_pnl[df_trader_pnl['TraderId'] == trader_id]
			obj_strategy.list_traders.append(obj_trader)

		obj_strategy.calculate_pnl()
		if is_satisfy(obj_strategy):
			dict_strategy[strategy_id] = obj_strategy
			print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Satisfy')
		else:
			print('    ', datetime.strftime(datetime.now(), '%H:%M:%S'), '   Not Satisfy')
	print('All Done:    ', datetime.strftime(datetime.now(),'%H:%M:%S'))
	return dict_strategy


def draw_charts(dict_strategy, path):
	def draw(df):
		grid = Grid(
			width=1200,
			height=700
		)
		line = Line()
		dt = datetime.now().strftime("%H%M%S")
		if not (os.path.isdir(path)):
			os.mkdir(path)
		path_output = os.path.join(path, "Pnl-%s.html" % dt)

		df_sum = pd.DataFrame(df.cumsum())
		for i in df_sum.columns.tolist():
			s = df_sum[i]
			line.add(
				i,
				x_axis=s.index.tolist(),
				y_axis=s.values.tolist(),
				is_datazoom_show=True,
				legend_pos="5%",
				legend_top='5%'
			)

		grid.add(line, grid_top='20%')
		grid.render("%s" % path_output)
		print("--- Render %s ---" % path_output)

	l_strategy_pnl = []
	for i in dict_strategy.keys():
		strategy_i = dict_strategy[i]
		strategy_i.cal_std_pnl()
		strategy_id = strategy_i.Id
		std_pnl = strategy_i.std_pnl
		std_pnl = std_pnl.set_index('Date', drop=True)
		std_pnl.rename(columns={'Returns': strategy_id}, inplace=True)
		l_strategy_pnl.append(std_pnl)

		if len(l_strategy_pnl) >= 10:
			df_pnl = pd.DataFrame(pd.concat(l_strategy_pnl, axis=1, sort=True))
			draw(df_pnl)
			l_strategy_pnl = []

	if len(l_strategy_pnl) > 0:
		df_pnl = pd.DataFrame(pd.concat(l_strategy_pnl, axis=1, sort=True))
		draw(df_pnl)
		l_strategy_pnl = []

	print('Draw All strategy pnl, Finished')

if __name__ == '__main__':
	program_start = datetime.now()

	# 设置数据库信息
	db_info = {
		"db": "Platinum.PM",
		"host": "192.168.1.101",
		"user": "sa",
		"pwd": "st@s2013"
	}

	# 设置条件
	filter_condition = {
		"start_date": datetime(2017, 6, 1),
		"end_date": "",

		"sharpe": 1,
		"annul_R": 0.1,
		"mdd": 0.07,
		"count": 200,

		"smaller_sharpe": False,
		"smaller_annul_R": False,
		"larger_mdd": False,
		"smaller_count" :False,
	}

	# 对比项信息
	'''
		type:
			"1": strategy_type,
			"2": strategy_id
	'''
	strategy_type_all = ['Alpha-Future', 'Alpha-Index', 'Cn.All.60.PairX(CalArb)', 'Cn.All.60B.CPA(DArb)',
	                 'Cn.All.60B.CPA(PDArb)', 'Cn.All.60B.PairEx(MFA)', 'Cn.All.60B.PairX(MFA)',
	                 'Cn.Bonds.60B.PairX(MFA)', 'Cn.Bonds.60B.Pattern', 'Cn.Bonds.U16.CPA', 'Cn.Com.60B.CPA',
	                 'Cn.Com.60B.Pattern', 'Cn.Com.Tick.Pattern', 'Cn.Com.U16.CPA', 'Cn.Com.U16.Pattern',
	                 'Cn.Com.U17.CPA', 'Cn.Com.U18.CPA', 'Cn.Com.U18.Pattern', 'Cn.Com.U19.CPA',
	                 'Cn.Com.U20.CPA', 'Cn.Com.U21.CPA', 'Cn.Com.U22.CPA', 'Cn.Com.U22.Pattern',
	                 'Cn.Com.U24.CPA', 'Cn.Com.U25.CPA', 'Cn.Csi.60B.PairX(MFA)', 'Cn.Csi.60B.Pattern',
	                 'Cn.Csi.Tick.Pattern', 'Cn.Csi.U16.CPA', 'Cn.Options.60.PairEx(CalArb)',
	                 'Cn.Options.60A.PairEx(VerArb)', 'Cn.Physical.60B.PairEx', 'Cn.Stocks.D.Alpha(NoHedging)',
	                 'Cn.Stocks.D.Alpha(VsFutures)', 'Cn.Stocks.D.Alpha(VsIndex)', 'Global.All.60B.Pattern',
	                 'Global.BMX.60B.PairX(MFA)', 'Global.BMX.60B.Pattern', 'Global.BN.60B.PairX(MFA)',
	                 'Global.BN.60B.Pattern', 'Others', 'Stock']
	filter_item = {
		"type": "1",
		"item": strategy_type_all
	}

	start_date = filter_condition['start_date']
	if filter_condition['end_date'] == "":
		end_date = datetime.today()
	else:
		end_date = filter_condition['end_date']

	df_strategy_info, df_trader_info, df_trader_pnl = get_db_data(db_info, filter_item, start_date, end_date)

	dict_satisfy_strategy = strategy_filter(filter_condition, df_strategy_info, df_trader_info, df_trader_pnl)

	# df_strategy_info = pd.DataFrame(df_strategy_info, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
	# df_trader_info = pd.DataFrame(df_trader_info, columns=['TraderId', 'StrategyId'])
	# df_trader_pnl = pd.DataFrame(df_trader_pnl, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])




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