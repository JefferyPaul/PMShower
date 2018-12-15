from SQL.MSSQL import MSSQL
from bak.PMData_power import *
from datetime import datetime
import pandas as pd
from pyecharts import Line, Grid
import os


def select_strategy(list_type, func_sql_exec):
	if len(list_type) < 1:
		return ""
	sql = '''
		SELECT 
			[Id]
	      ,[OutSampleDate]
	      ,[Type]
	    FROM [Platinum.PM].[dbo].[StrategyDbo]
	    where type in ('%s')
    ''' % "','".join(list_type)
	re_sql = func_sql_exec(sql)
	df = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type'])
	return df


def draw_echarts(df, path):
	grid = Grid(
		width=1200,
		height=700
	)
	line = Line()
	dt = datetime.now().strftime("%H%M%S")
	if not(os.path.isdir(path)):
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


def filter():
	dict_filtered = {}
	list_pnl = []
	
	df_strategy_id = select_strategy(strategy_type, func_sql_exec)

	for strategy_id in df_strategy_id['Id'].tolist():
		print('Calculating:  %s   - - -   ' % strategy_id, end=""
		                                                       "")
		strategy = PMStrategy(Id=strategy_id, use_last_portfolio=True)
		if type(filter_condition['start_date']) == datetime:
			strategy.set_start_date(filter_condition['start_date'])
		
		# 策略数据

		strategy.get_data(func_sql_exec)
		std_pnl = strategy.std_pnl
		std_pnl = std_pnl.set_index('Date', drop=True)
		std_pnl.rename(columns={'Returns': strategy_id}, inplace=True)
		series_des_std_pnl = strategy.describe(cal_std=True)
		try:
			annual_return = float(series_des_std_pnl['annual_return'])
			sharpe = float(series_des_std_pnl['sharpe'])
			mdd = float(series_des_std_pnl['mdd'])
			count = int(series_des_std_pnl['count'])
		except:
			print('not good, Wrong')
			continue
		
		# 筛选
		if filter_condition['annul_R']:
			if annual_return < filter_condition['annul_R']:
				print('not Good, annul_R = %s' % annual_return)
				continue
		if filter_condition['sharpe']:
			if sharpe < filter_condition['sharpe']:
				print('not Good, sharpe = %s' % sharpe)
				continue
		if filter_condition['mdd']:
			if mdd > filter_condition['mdd']:
				print('not Good, mdd = %s' % mdd)
				continue
		if filter_condition['count']:
			if count < filter_condition['count']:
				print('not Good, count = %s' % count)
				continue
		
		# 符合要求
		dict_filtered[strategy_id] = series_des_std_pnl
		list_pnl.append(std_pnl)
		print('Satisfy, annual_R = %s ,  sharpe = %s , mdd = %s ' % (
			round(series_des_std_pnl['annual_return'], 3),
			round(series_des_std_pnl['sharpe'], 2),
			round(series_des_std_pnl['mdd'], 2)
		))

		if len(list_pnl) >= 10:
			df_pnl = pd.DataFrame(pd.concat(list_pnl, axis=1, sort=True))
			draw_echarts(df_pnl, out_put_path)
			# df_pnl.plot()
			list_pnl = []

	if len(list_pnl) > 0:
		df_pnl = pd.DataFrame(pd.concat(list_pnl, axis=1))
		draw_echarts(df_pnl, out_put_path)
		# df_pnl.plot()
		list_pnl = []
	df_describe_filtered = pd.DataFrame.from_dict(dict_filtered)
	df_describe_filtered.T.to_csv('%s/filtered.csv' % out_put_path, encoding='utf-8')


if __name__ == '__main__':
	program_start = datetime.now()

	# 设置条件
	filter_condition = {
		"start_date": datetime(2017, 9, 1),
		"end_date": "",
		"sharpe": 1,
		"annul_R": 0.1,
		"mdd": 0.07,
		"count": 200,

		"smaller_sharpe": False,
		"smaller_annul_R": False,
		"larger_mdd": False,
		"smaller_count": False,
	}

	# 基本信息
	# strategy_type = ['Cn.Com.60B.CPA', 'Cn.Com.60B.Pattern']
	strategy_type = ['Alpha-Future', 'Alpha-Index', 'Cn.All.60.PairX(CalArb)', 'Cn.All.60B.CPA(DArb)',
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
	path = r'F:/StrategyLogData/StrategyCheck-output'
	out_put_path = os.path.join(path, datetime.today().strftime('%Y%m%d_%H%M%S_PMStrategy_Filtered'))

	# db信息
	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"
	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	func_sql_exec = mssql.ExecQuery
	
	filter()
	mssql.close()
	
	program_end = datetime.now()
	print('Done!')
	print('Run time:  ', (program_end - program_start).seconds, ' s')