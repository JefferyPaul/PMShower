from FilterTools import PMFilter
from FilterTools.draw_charts import *
from PMDataManager import getPMData


if __name__ == '__main__':
	program_start = datetime.now()
	db_info = {
		"db": "Platinum.PM",
		"host": "192.168.1.101",
		"user": "sa",
		"pwd": "st@s2013",
		"start_date": datetime(2015, 1, 1),
		"end_date": datetime.today(),
	}

	# 对比项信息
	path_selected_strategies = r'./satisfy_strategy.csv'
	df_strategy_file = pd.read_csv(path_selected_strategies)
	list_select_strategy = df_strategy_file.loc[df_strategy_file['satisfy'] == 1, 'strategy'].tolist()

	output_path = r'../output/filter_%s' % datetime.now().strftime('%Y%m%d-%H%M%S')
	if not os.path.isdir(output_path):
		os.mkdir(output_path)

	list_filter_condition = [
		{
			"start_date": datetime(2018, 6, 1),
			"end_date": datetime.today(),
			"std_start_date":datetime(2018, 1, 1),
			"std_end_date":datetime.today(),
			"sharpe": 1.5,
			"annul_R": 0.1,
			"mdd": 0.07,
			"count": 20,
			"smaller_sharpe": False,
			"smaller_annul_R": False,
			"larger_mdd": False,
			"smaller_count": False,
		},
		{
			"start_date": datetime(2018, 9, 1),
			"end_date": datetime.today(),
			"std_start_date": datetime(2018, 1, 1),
			"std_end_date": datetime.today(),
			"sharpe": 2,
			"annul_R": 0.1,
			"mdd": 0.07,
			"count": 10,
			"smaller_sharpe": False,
			"smaller_annul_R": False,
			"larger_mdd": False,
			"smaller_count": False,
		}
	]

	df_strategy_info, df_trader_info, df_trader_pnl = getPMData.strategy_id_get_data(
		db_info, list_select_strategy, start_date=datetime(2017, 1, 1))
	dict_satisfy_strategy = PMFilter.strategy_filter(df_strategy_info, df_trader_info, df_trader_pnl, list_filter_condition)
	draw_pm_item_returns(dict_satisfy_strategy, output_path)

	for i in df_strategy_file.index:
		s = df_strategy_file.loc[i, 'strategy']
		if s not in dict_satisfy_strategy.keys():
			df_strategy_file.loc[i, 'satisfy'] = 0
	df_strategy_file[['strategy', 'satisfy']].to_csv(path_selected_strategies, index=False)

	print(dict_satisfy_strategy.keys())
