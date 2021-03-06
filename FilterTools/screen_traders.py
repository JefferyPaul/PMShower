from FilterTools import PMFilter
from FilterTools.draw_charts import *
from PMDataManager import getPMData


def check_strategy_trader_id():
	global df_selected_traders
	df = df_selected_traders.copy()
	for i_index in df.index:
		i_trader = df.loc[i_index, 'trader']
		i_strategy = df.loc[i_index, 'strategy']
		if i_strategy != df_trader_info.loc[df_trader_info['TraderId']==i_trader, 'StrategyId']:
			df.drop(i_index, axis=0, inplace=True)
			print('Wrong input,this trader-strategy is not math: %s - %s' % (i_trader, i_strategy))
	df_selected_traders = df


if __name__ == '__main__':
	dt_program_start = datetime.now()
	db_info = {
		"db": "Platinum.PM",
		"host": "192.168.1.101",
		"user": "sa",
		"pwd": "st@s2013"
	}

	# 对比项信息
	path_selected_strategy = r'../compare_traders_AIO_PMId.csv'
	df_input = pd.read_csv(path_selected_strategy)
	list_selected_trader_id = list(set(df_input['traderId'].dropna()))
	list_selected_strategy_id = list(set(df_input['strategyId'].dropna()))

	output_path = r'../output/filter_AIO_traders_%s' % datetime.now().strftime('%Y%m%d-%H%M%S')

	# 设置条件
	list_filter_condition = [
		{
			"std_start_date":datetime(2017, 6, 6),
			"std_end_date":datetime(2018, 6, 1),
			"start_date": datetime(2017, 6, 6),
			"end_date": datetime.today(),
			"sharpe": 0.5,
			"annul_R": 0.05,
			"mdd": 0.3,
			"count": 350,
			"smaller_sharpe": False,
			"smaller_annul_R": False,
			"larger_mdd": False,
			"smaller_count": False,
		}
		# ,{
		# 	"std_start_date":datetime(2018, 1, 1),
		# 	"std_end_date":datetime(2018, 6, 1),
		# 	"start_date": datetime(2018, 1, 1),
		# 	"end_date": datetime.today(),
		# 	"sharpe": 0.8,
		# 	"annul_R": 0.05,
		# 	"mdd": 0.3,
		# 	"count": 50,
		# 	"smaller_sharpe": False,
		# 	"smaller_annul_R": False,
		# 	"larger_mdd": False,
		# 	"smaller_count": False,
		# }
	]

	# 从db 获取所需数据
	df_strategy_info, df_trader_info, df_trader_pnl = getPMData.trader_id_get_data(
		dict_db_info=db_info,
		list_strategy_id=list_selected_strategy_id,
		list_trader_id=list_selected_trader_id,
		start_date=datetime(2017, 1, 1)
	)
	df_strategy_info = pd.DataFrame(df_strategy_info, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
	df_trader_info = pd.DataFrame(df_trader_info, columns=['TraderId', 'StrategyId'])
	df_trader_pnl = pd.DataFrame(df_trader_pnl, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	# 筛选
	dict_satisfy_trader = PMFilter.trader_filter(
		df_trader_info=df_trader_info,
		df_trader_pnl=df_trader_pnl,
		list_filter_condition=list_filter_condition
	)

	# 输出信息
	if not(os.path.isdir(output_path)):
		os.mkdir(output_path)
	list_satisfy_info = []
	df_input['isSatisfy'] = 0
	df_input['mdd'] = ""
	df_input['sharpe'] = ""
	df_input['annual_return'] = ""
	df_input['annual_std'] = ""
	for i_satisfy_trader_id in dict_satisfy_trader.keys():
		i_satisfy_trader = dict_satisfy_trader[i_satisfy_trader_id]
		i_trader_id = i_satisfy_trader.Id
		i_trader_belong_strategy_id = i_satisfy_trader.belong_strategy_id
		list_satisfy_info.append([i_trader_belong_strategy_id, i_trader_id])

		des = i_satisfy_trader.describe(
			is_use_std=True,
			std_start_date=datetime(2017,6,6),
			std_end_date=datetime(2018,6,1),
			start_date=datetime(2017,6,6),
			end_date=datetime.today()
		)
		mdd = des['mdd']
		sharpe = des['sharpe']
		annual_return = des['annual_return']
		annual_std = des['annual_std']
		df_input.loc[df_input['traderId']==i_trader_id, 'isSatisfy'] = 1
		df_input.loc[df_input['traderId']==i_trader_id, 'mdd'] = mdd
		df_input.loc[df_input['traderId']==i_trader_id, 'sharpe'] = sharpe
		df_input.loc[df_input['traderId']==i_trader_id, 'annual_return'] = annual_return
		df_input.loc[df_input['traderId']==i_trader_id, 'annual_std'] = annual_std

	df_satisfy_info = pd.DataFrame(list_satisfy_info, columns=['strategyId', 'traderId'])
	path_info = os.path.join(output_path, '_trader_info.csv')
	df_satisfy_info.to_csv(path_info, index=False)
	path_info = os.path.join(output_path, '_trader_info_2.csv')
	df_input.to_csv(path_info, index=False)
	print('output info finished : %s' % datetime.now().strftime('%H:%M:%S'))

	# 输出 对比图
	draw_same_ticker_trader_returns(dict_satisfy_trader, output_path)

	# Finish
	dt_program_end = datetime.now()
	print('All is Finished:    ', end='')
	print('Start at : %s' % dt_program_start.strftime('%H:%M:%S'))
	print('Finish at: %s' % dt_program_end.strftime('%H:%M:%S'))
