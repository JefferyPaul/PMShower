from datetime import datetime
import pandas as pd
import numpy as np


class PMData:
	def __init__(self, Id, type, start_date=datetime(year=2017, month=7, day=1), end_date=datetime.today()):
		self.Id = Id
		self.type = type

		self.start_date = start_date
		self.end_date = end_date

		self.pnl = pd.DataFrame(columns=['Date', 'Returns'])
		self.std_pnl = pd.DataFrame(columns=['Date', 'Returns'])

	def set_start_date(self, dt):
		if type(dt) == datetime:
			self.start_date = dt
		else:
			pass

	def set_end_date(self, dt):
		if type(dt) == datetime:
			self.end_date = dt
		else:
			pass

	def describe(self, start_date=None, end_date=None, cal_std=None):
		def cal_stat():
			if len(df) < 1:
				return
			r_describe = df['Returns'].describe()

			count = int(r_describe['count'])
			first_date = min(df['Date'].tolist())
			last_date = max(df['Date'].tolist())
			annual_std = float(r_describe['std']) * np.sqrt(250)
			daily_return = float(r_describe['mean'])
			try:
				annual_return = daily_return * 250
			except:
				annual_return = np.nan
			if annual_std == 0:
				sharpe = np.nan
			else:
				try:
					sharpe = annual_return / annual_std
				except:
					sharpe = np.nan

			dict_describe['count'] = count
			dict_describe['first_date'] = first_date
			dict_describe['last_date'] = last_date
			dict_describe['daily_return'] = daily_return
			dict_describe['annual_return'] = annual_return
			dict_describe['annual_std'] = annual_std
			dict_describe['sharpe'] = sharpe

		def cal_mdd():
			if len(df) < 1:
				return
			df['Returns_cumsum'] = df['Returns'].cumsum()
			df_cum = df[['Date', 'Returns_cumsum']]

			df_cum.loc[:, 'max_here'] = df_cum.loc[:, 'Returns_cumsum'].expanding().max()
			df_cum.loc[:, 'dd_here'] = df_cum.loc[:, 'max_here'] - df_cum.loc[:, 'Returns_cumsum']
			df_cum.loc[df_cum.loc[:, 'dd_here'] == 0, 'max_here_index'] = df_cum.loc[df_cum.loc[:, 'dd_here'] == 0,
			                                                              :].index
			df_cum.loc[:, 'max_here_index'] = df_cum.loc[:, 'max_here_index'].fillna(method='ffill')
			df_cum.loc[:, 'dd_period'] = df_cum.index - df_cum.loc[:, 'max_here_index']
			df_cum.loc[:, 'index'] = df_cum.index.tolist()

			# cal_mdd
			series_mdd = df_cum.loc[df_cum['dd_here'] == df_cum['dd_here'].max(), :]
			if len(series_mdd) >= 1:
				series_mdd = series_mdd.iloc[-1]
				mdd = float(series_mdd['dd_here'])
				mdd_date = series_mdd['Date']
				mdd_start_date = df_cum.loc[series_mdd['max_here_index'], 'Date']
			else:
				mdd = np.nan
				mdd_date = ""
				mdd_start_date = ""

			series_ldd = df_cum.loc[df_cum['dd_period'] == df_cum['dd_period'].max(), :]
			if len(series_ldd) >= 1:
				series_ldd = series_ldd.iloc[-1]
				ldd = int(series_ldd['dd_period'])
				ldd_end_date = series_ldd['Date']
				ldd_start_date = df_cum.loc[int(series_ldd['index']) - int(series_ldd['dd_period']), 'Date']
			else:
				ldd = np.nan
				ldd_end_date = ""
				ldd_start_date = ""

			dict_describe['mdd'] = mdd
			dict_describe['mdd_date'] = mdd_date
			dict_describe['mdd_start_date'] = mdd_start_date
			dict_describe['ldd'] = ldd
			dict_describe['ldd_end_date'] = ldd_end_date
			dict_describe['ldd_start_date'] = ldd_start_date

		dict_describe = {
			'count': 0,
			'first_date': "",
			'last_date': "",
			'daily_return': np.nan,
			'annual_return': np.nan,
			'annual_std': np.nan,
			'sharpe': np.nan,
			'mdd': np.nan,
			'mdd_start_date': "",
			'mdd_date': "",
			'ldd': np.nan,
			'ldd_start_date': "",
			'ldd_end_date': ""
		}

		df = pd.DataFrame(self.pnl)
		if start_date is None:
			start_date = self.start_date.strftime('%Y%m%d')
		if type(start_date) == datetime:
			start_date = start_date.strftime('%Y%m%d')
		if end_date is None:
			end_date = self.end_date.strftime('%Y%m%d')
		if type(end_date) == datetime:
			end_date = end_date.strftime('%Y%m%d')

		df = df.loc[df['Date'] <= end_date, :]
		df = df.loc[df['Date'] >= start_date, :]
		df = df.reset_index(drop=True)

		cal_stat()
		cal_mdd()

		if cal_std:
			describe_annual_std = dict_describe['annual_std']
			if describe_annual_std == 0:
				mul = 0
			else:
				mul = 0.12 / describe_annual_std
			dict_describe['daily_return'] = dict_describe['daily_return'] * mul
			dict_describe['annual_return'] = dict_describe['annual_return'] * mul
			dict_describe['annual_std'] = 0.12
			dict_describe['mdd'] = dict_describe['mdd'] * mul
		return dict_describe

	def cal_std_pnl(self):
		if not (type(self.pnl) == pd.DataFrame):
			pass
		else:
			dict_describe = self.describe()
			init_annual_std = float(dict_describe['annual_std'])
			if init_annual_std != 0:
				mul = 0.12 / init_annual_std
			else:
				mul = 0
			self.std_pnl = pd.DataFrame(self.pnl).copy()
			self.std_pnl['Returns'] = self.std_pnl['Returns'] * mul


class PMProduct(PMData):
	def __init__(self, Id, user, product_start_at_create=True, strategy_use_last_portfolio=True):
		PMData.__init__(self, Id=Id, type='Product')
		self.portfolio_user_id = user
		self.list_strategies_id = []
		self.strategies_weight = pd.DataFrame(columns=['Date', 'StrategyId', 'PortfolioUserId', 'Weight'])

		self.product_start_at_create = product_start_at_create
		self.strategy_use_last_portfolio = strategy_use_last_portfolio
		self.list_strategies = []


class PMStrategy(PMData):
	def __init__(self, Id, portfolio_user_id='Benchmark', use_last_portfolio=False):
		PMData.__init__(self, Id=Id, type='Strategy')
		self.strategy_info = []
		self.list_traders_id = []

		self.portfolio_user_id = portfolio_user_id
		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])
		self.use_last_portfolio = use_last_portfolio

		self.list_traders = []
		self.strategy_type = ""
		self.out_sample_date = ""
		self.online_date = ""

	# def get_data(self, sql_exec):
	# 	self.get_traders_id(sql_exec)
	# 	self.get_portfolio(sql_exec)
	# 	self.get_strategy_traders(sql_exec)
	# 	self.calculate_pnl()
	# 	self.cal_std_pnl()
	#
	# def get_strategy_inf(self, sql_exec):
	# 	sql = '''
	# 			SELECT *
	# 		      FROM [Platinum.PM].[dbo].[StrategyDbo]
	#              where Id = '%s'
	#         ''' % self.Id
	# 	re_sql = sql_exec(sql)
	# 	series_info = pd.Series(re_sql)
	# 	if len(re_sql) > 0:
	# 		series_info = pd.Series(re_sql)
	# 		self.out_sample_date = datetime.strptime(series_info['OutSampleDate'], format='%Y-%m-%d')
	# 		self.online_date = datetime.strptime(series_info['OnlineDate'], format='%Y-%m-%d')
	# 		self.strategy_type = series_info['Type']
	# 	else:
	# 		pass
	#
	# def get_traders_id(self, sql_exec):
	# 	sql = '''
	# 		SELECT Id
	# 	      FROM [Platinum.PM].[dbo].[TraderDbo]
    #          where StrategyId = '%s'
    #     ''' % self.Id
	# 	re_sql = sql_exec(sql)
	# 	if len(re_sql) > 0:
	# 		self.list_traders_id = pd.DataFrame(re_sql).loc[:, 0].tolist()
	# 	else:
	# 		pass
	#
	# def get_portfolio(self, sql_exec):
	# 	if len(self.list_traders_id) < 1:
	# 		pass
	# 	else:
	# 		sql = '''
	# 			SELECT [Date],[TraderId],[Weight]
	# 			  FROM [Platinum.PM].[dbo].[PortfolioTraderWeightDbo]
	# 			  where UserId = '%s' and TraderId in ('%s')
	# 	    ''' % (self.portfolio_user_id, "','".join(self.list_traders_id))
	# 		re_sql = sql_exec(sql)
	# 		if len(re_sql) > 0:
	# 			df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Weight'])
	#
	# 			if not self.use_last_portfolio:
	# 				self.traders_weight = df
	# 			else:
	# 				last_date = max(set(df['Date'].tolist()))
	# 				df = df.loc[df['Date'] == last_date, :]
	# 				self.traders_weight = df
	#
	# def get_strategy_traders(self, sql_exec):
	# 	if len(self.list_traders_id) < 1:
	# 		pass
	# 	else:
	# 		for trader_id in self.list_traders_id:
	# 			trader = PMTrader(Id=trader_id)
	# 			trader.set_start_date(self.start_date)
	# 			trader.set_end_date(self.end_date)
	# 			trader.get_data(sql_exec)
	# 			trader.set_out_sample_date(out_sample_date=self.out_sample_date, online_date=self.online_date)
	# 			self.list_traders.append(trader)

	# print('%s - Get Strategy Traders - Done' % self.Id)

	def calculate_pnl(self):
		if len(self.list_traders) < 1:
			return

		if self.portfolio_user_id=='Benchmark':
			l_df = [i.pnl for i in self.list_traders]
		else:
			l_df = []
			for trader in self.list_traders:
				df_pnl = trader.pnl

				df_weight = self.traders_weight
				if len(df_pnl) < 1 or len(df_weight) < 1:
					continue
				try:
					# weight日期在pnl范围内，直接用merge
					# weight在pnl日期范围外，使用最后一次weight
					if True in [d in df_pnl['Date'].unique().tolist() for d in df_weight['Date'].unique().tolist()]:
						df_merge = pd.merge(left=df_pnl, right=df_weight, on=['TraderId', 'Date'], how='left')
						df_merge = df_merge.sort_values(by=['TraderId', 'Date'])
						df_merge = df_merge.fillna(method='ffill')
						df_merge = df_merge.fillna(method='bfill')
					else:
						df_weight = df_weight.loc[df_weight['Date'] == max(df_weight['Date'].unique()), :]
						df_weight = df_weight[['TraderId', 'Weight']]
						df_merge = pd.merge(left=df_pnl, right=df_weight, on=['TraderId'], how='left')
						df_merge = df_merge.sort_values(by=['TraderId', 'Date'])
						df_merge = df_merge.fillna(method='ffill')
						df_merge = df_merge.fillna(method='bfill')
					df_merge['Returns'] = df_merge['Returns'] * df_merge['Weight']
					l_df.append(df_merge)
				except:
					continue
		if len(l_df) > 0:
			df = pd.DataFrame(pd.concat(l_df))
			df_r = pd.DataFrame(df.groupby(by='Date')['Returns'].sum())
			# df_r = pd.DataFrame(df.groupby(by='Date')['portfolio_returns'].sum())
			# df_r.rename(columns={'portfolio_returns':'Returns'}, inplace=True)
			df_r['Date'] = df_r.index
			df_r = df_r.reset_index(drop=True)
			self.pnl = df_r

			self.cal_std_pnl()
		else:
			pass


class PMTrader(PMData):
	def __init__(self, Id):
		PMData.__init__(self, Id=Id, type='Trader')
		self.pnl = pd.DataFrame(
			columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])
		self.out_sample_date = ""
		self.online_date = ""

	# def get_data(self, sql_exec):
	# 	self.get_pnl(sql_exec)
	# 	self.cal_std_pnl()
	#
	# def get_pnl(self, sql_exec):
	# 	sql = '''
	# 		SELECT [Date],[TraderId],[Pnl],[Commission],[Slippage],[Capital]
	# 	    FROM [Platinum.PM].[dbo].[TraderLogDbo]
	# 	    where TraderId = '%s' and  Date>='%s' and Date<='%s'
    #     ''' % (self.Id, self.start_date.strftime('%Y%m%d'), self.end_date.strftime('%Y%m%d'))
	# 	re_sql = sql_exec(sql)
	#
	# 	if len(re_sql) > 0:
	# 		df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
	# 		df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
	# 		df['Returns'] = df['Pnl'] / df['Capital']
	# 		self.pnl = df
	# 	else:
	# 		pass

	def set_out_sample_date(self, out_sample_date, online_date):
		self.out_sample_date = out_sample_date
		self.online_date = online_date
