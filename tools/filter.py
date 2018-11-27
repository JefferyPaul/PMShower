from SQL.MSSQL import MSSQL
from PMDataManager.PMData import *
from datetime import datetime
import pandas as pd
from pyecharts import Line,Grid
import os


type = '''
	Alpha-Future,Alpha-Index,Cn.All.60.PairX(CalArb),Cn.All.60B.CPA(DArb)
	Cn.All.60B.CPA(PDArb)
	Cn.All.60B.PairEx(MFA)
	Cn.All.60B.PairX(MFA)
	Cn.Bonds.60B.PairX(MFA)
	Cn.Bonds.60B.Pattern
	Cn.Bonds.U16.CPA
	Cn.Com.60B.CPA
	Cn.Com.60B.Pattern
	Cn.Com.Tick.Pattern
	Cn.Com.U16.CPA
	Cn.Com.U16.Pattern
	Cn.Com.U17.CPA
	Cn.Com.U18.CPA
	Cn.Com.U18.Pattern
	Cn.Com.U19.CPA
	Cn.Com.U20.CPA
	Cn.Com.U21.CPA
	Cn.Com.U22.CPA
	Cn.Com.U22.Pattern
	Cn.Com.U24.CPA
	Cn.Com.U25.CPA
	Cn.Csi.60B.PairX(MFA)
	Cn.Csi.60B.Pattern
	Cn.Csi.Tick.Pattern
	Cn.Csi.U16.CPA
	Cn.Options.60.PairEx(CalArb)
	Cn.Options.60A.PairEx(VerArb)
	Cn.Physical.60B.PairEx
	Cn.Stocks.D.Alpha(NoHedging)
	Cn.Stocks.D.Alpha(VsFutures)
	Cn.Stocks.D.Alpha(VsIndex)
	Global.All.60B.Pattern
	Global.BMX.60B.PairX(MFA)
	Global.BMX.60B.Pattern
	Global.BN.60B.PairX(MFA)
	Global.BN.60B.Pattern
	Others
	Stock
'''


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
			legend_pos="10%",
			legend_top='30%'
		)

	line.render("%s" % path_output)
	print("--- Render %s ---" % path_output)


if __name__ == '__main__':
	list_type = [ 'Cn.Com.U16.Pattern']
	path = r'F:/StrategyLogData/StrategyCheck-output'
	s_dt = datetime.today().strftime('%Y%m%d_%H%M%S')
	out_put_path = os.path.join(path, s_dt)

	# list_type = ['Cn.Com.U16.CPA', 'Cn.Com.U16.Pattern']
	start_date = datetime(2018,1,1)

	db = "Platinum.PM"
	host = "192.168.1.101"
	user = "sa"
	pwd = "st@s2013"
	mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
	func_sql_exec = mssql.ExecQuery

	dict_filtered = {}
	list_pnl = []
	df_strategy_id = select_strategy(list_type, func_sql_exec)

	for strategy_id in df_strategy_id['Id'].tolist():
	# for strategy_id in ['Cn.Com.U16.Pattern@CnCom.Id007104.C_A']:
		print('Calculating:  %s' % strategy_id)
		strategy = PMStrategy(Id=strategy_id, use_last_portfolio=True)
		if start_date:
			strategy.set_start_date(start_date)

		strategy.get_traders_id(func_sql_exec)
		strategy.get_portfolio(func_sql_exec)
		strategy.get_strategy_traders(func_sql_exec)
		strategy.calculate_pnl()

		series_des_pnl = strategy.cal_describe(item='stat')
		# print(series_des_pnl)
		try:
			annualized_return = float(series_des_pnl.annualized_return)
			sharp = float(series_des_pnl.sharp)
		except:
			print('not good')
			continue
		if annualized_return < 0.01 or sharp < 0.1:
			print('not good')
		else:
			strategy.pnl_standardize()
			std_pnl = strategy.std_pnl
			std_pnl = std_pnl.set_index('Date', drop=True)
			std_pnl.rename(columns={'Returns': strategy_id}, inplace=True)
			series_des_std_pnl = strategy.cal_describe(df=strategy.std_pnl)
			dict_filtered[strategy_id] = series_des_pnl
			list_pnl.append(std_pnl)
			print('satisfy:')
			print('%s   : r:%s ,  s:%s' %(strategy_id, series_des_std_pnl.annualized_return, series_des_std_pnl.shape))

		if len(list_pnl) >= 10:
			df_pnl = pd.DataFrame(pd.concat(list_pnl, axis=1))
			draw_echarts(df_pnl, out_put_path)
			# df_pnl.plot()
			list_pnl = []
	print('Done!')

	mssql.close()
