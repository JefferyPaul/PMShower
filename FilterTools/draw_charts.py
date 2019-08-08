from pyecharts import Line, Grid
import os
from datetime import datetime
import pandas as pd
import random


def draw_cumsum(df, path_output):
	grid = Grid(
		width=1200,
		height=700
	)
	line = Line()

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


def draw_pm_item_returns(dict_item, path):
	l_returns = []

	for i in dict_item.keys():
		item_i = dict_item[i]
		item_id = item_i.Id
		std_pnl = item_i.cal_std_returns()
		std_pnl = std_pnl[['Returns']]
		std_pnl.rename(columns={'Returns': item_id}, inplace=True)

		l_returns.append(std_pnl)

		if len(l_returns) >= 10:
			df_pnl = pd.DataFrame(pd.concat(l_returns, axis=1, sort=True))
			dt = datetime.now().strftime("%H%M%S")
			path_render = os.path.join(
				path,
				"Pnl-%s-%s.html" % (dt, str(random.randint(1,10000.)))
			)
			draw_cumsum(df_pnl, path_render)
			l_returns = []

	if len(l_returns) > 0:
		df_pnl = pd.DataFrame(pd.concat(l_returns, axis=1, sort=True))
		dt = datetime.now().strftime("%H%M%S")
		path_render = os.path.join(
			path,
			"Pnl-%s-%s.html" % (dt, str(random.randint(1, 10000.)))
		)
		draw_cumsum(df_pnl, path_render)
		l_returns = []
	print('Draw All strategy pnl, Finished')


def draw_same_ticker_trader_returns(dict_trader, path):
	# 1 查找相同 trader_short_name 的trader，
	# dict_trader_in_short_name = { trader_short_name1:[ trader1, trader2], trader_short_name2:[], }
	list_trader_id = list(dict_trader.keys())
	dict_trader_in_short_name = {}
	for i_trader_id in list_trader_id:
		i_trader_short_name = i_trader_id.split('@')[0]
		if i_trader_short_name not in list(dict_trader_in_short_name.keys()):
			dict_trader_in_short_name[i_trader_short_name] = []
			dict_trader_in_short_name[i_trader_short_name].append(dict_trader[i_trader_id])
		else:
			dict_trader_in_short_name[i_trader_short_name].append(dict_trader[i_trader_id])
	
	# 遍历每个 trader_short_name
	# 将同一 trader_short_name的trader 的std_pnl组合成一个df
	# draw(df) 画图
	for i_trader_short_name in list(dict_trader_in_short_name.keys()):
		list_trader_same_short_name = dict_trader_in_short_name[i_trader_short_name]
	
		if not(len(list_trader_same_short_name) > 0):
			continue
		else:
			l_returns = []
			for i_trader in list_trader_same_short_name:
				trader_id = i_trader.Id
				trader_belong_strategy_id = i_trader.belong_strategy_id

				df_std_pnl = i_trader.cal_std_returns()
				df_std_pnl = df_std_pnl[['Returns']]
				df_std_pnl.rename(columns={'Returns': '%s-%s' % (trader_belong_strategy_id, trader_id)}, inplace=True)
				l_returns.append(df_std_pnl)
			if len(l_returns) > 0:
				df_pnl = pd.DataFrame(pd.concat(l_returns, axis=1, sort=True))
				if not(os.path.isdir(path)):
					os.mkdir(path)
				path_render = os.path.join(path, '%s-%s.html' % (i_trader_short_name, str(int(len(l_returns)))))
				draw_cumsum(df_pnl, path_render)
				l_returns = []
	print('Draw All trader pnl, Finished')

