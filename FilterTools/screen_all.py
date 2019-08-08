from FilterTools import PMFilter
from FilterTools.draw_charts import *
from datetime import datetime
from PMDataManager import getPMData


'''
	db_info中的 start_date end_date,用于取trader_pnl时指定日期区间
	filter_condition中的 date 用于指定判断策略是否符合要求时所使用的数据的日期区间
'''
if __name__ == '__main__':
	dt_program_start = datetime.now()
	db_info = {
		"db": "Platinum.PM",
		"host": "192.168.1.101",
		"user": "sa",
		"pwd": "st@s2013"
	}

	# 设置条件
	list_filter_condition = [
		{
			"std_start_date": datetime(2017, 1, 1),
			"std_end_date": datetime.today(),
			"start_date": datetime(2017, 6, 1),
			"end_date": datetime.today(),
			"sharpe": 1,
			"annul_R": 0.1,
			"mdd": 0.1,
			"count": 350,
			"smaller_sharpe": False,
			"smaller_annul_R": False,
			"larger_mdd": False,
			"smaller_count": False,
		},
		{
			"std_start_date": datetime(2018, 1, 1),
			"std_end_date": datetime.today(),
			"start_date": datetime(2018, 6, 1),
			"end_date": datetime.today(),
			"sharpe": 0.8,
			"annul_R": 0.05,
			"mdd": 0.07,
			"count": 50,
			"smaller_sharpe": False,
			"smaller_annul_R": False,
			"larger_mdd": False,
			"smaller_count": False,
		}
	]

	# 对比项信息
	strategy_type_all = [
		'Alpha-Future', 'Alpha-Index', 'Cn.All.60.PairX(CalArb)', 'Cn.All.60B.CPA(DArb)',
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
		'Global.BN.60B.Pattern', 'Others', 'Stock'
	]
	# strategy_type_all = strategy_type_all[::2]

	output_path = r'../output/filter_%s' % datetime.now().strftime('%Y%m%d-%H%M%S')

	df_strategy_info, df_trader_info, df_trader_pnl = getPMData.strategy_type_get_data(
		dict_db_info=db_info,
		list_strategy_type=strategy_type_all,
		start_date=datetime(2017, 1, 1)
	)

	dict_satisfy_strategy = PMFilter.strategy_filter(
		df_strategy_info,
		df_trader_info,
		df_trader_pnl,
		list_filter_condition
	)
	if not os.path.isdir(output_path):
		os.mkdir(output_path)
	draw_pm_item_returns(dict_satisfy_strategy, output_path)

	print(dict_satisfy_strategy.keys())

	# Finish
	dt_program_end = datetime.now()
	print('All is Finished:    ', end='')
	print('Start at : %s' % dt_program_start.strftime('%H:%M:%S'))
	print('Finish at: %s' % dt_program_end.strftime('%H:%M:%S'))
