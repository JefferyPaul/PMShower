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
		# self.std_pnl = pd.DataFrame(columns=['Date', 'Returns'])

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

	def describe(self, start_date=None, end_date=None, use_std=None, std_start_date=None, std_end_date=None):
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

		if start_date is None:
			start_date = self.start_date.strftime('%Y%m%d')
		if type(start_date) == datetime:
			start_date = start_date.strftime('%Y%m%d')
		if end_date is None:
			end_date = self.end_date.strftime('%Y%m%d')
		if type(end_date) == datetime:
			end_date = end_date.strftime('%Y%m%d')

		if use_std:
			if std_start_date is None:
				std_start_date = start_date
			if std_end_date is None:
				std_end_date = end_date
			df = pd.DataFrame(self.cal_std_pnl(start_date=std_start_date, end_date=std_end_date))
		else:
			df = pd.DataFrame(self.pnl)

		df = df.loc[df['Date'] <= end_date, :]
		df = df.loc[df['Date'] >= start_date, :]
		df = df.reset_index(drop=True)

		cal_stat()
		cal_mdd()
		return dict_describe

	def cal_std_pnl(self, start_date=None, end_date=None):
		if not (type(self.pnl) == pd.DataFrame):
			return
		else:
			if start_date is None or start_date == "":
				start_date = self.start_date.strftime('%Y%m%d')
			if end_date is None or end_date == '':
				end_date = self.end_date.strftime('%Y%m%d')
			dict_describe = self.describe(start_date=start_date, end_date=end_date)
			init_annual_std = float(dict_describe['annual_std'])
			if init_annual_std != 0:
				mul = 0.12 / init_annual_std
			else:
				mul = 0
			std_pnl = pd.DataFrame(self.pnl).copy()
			# std_pnl = std_pnl[std_pnl['Date'] > start_date]
			# std_pnl = std_pnl[std_pnl['Date'] < end_date]
			std_pnl['Returns'] = std_pnl['Returns'] * mul
		return std_pnl


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
	def __init__(self, Id, portfolio_user_id='Benchmark',
	             use_last_portfolio=False, list_traders_id=None, list_traders=None,
	             strategy_type=None, out_sample_date=None, online_date=None):
		PMData.__init__(self, Id=Id, type='Strategy')

		self.list_traders_id = list_traders_id
		self.portfolio_user_id = portfolio_user_id
		self.use_last_portfolio = use_last_portfolio
		self.list_traders = list_traders
		self.strategy_type = strategy_type
		self.out_sample_date = out_sample_date
		self.online_date = online_date

		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])

	def set_strategy(self, df_trader_pnl):
		for i_trader_id in self.list_traders_id:
			obj_trader = PMTrader(i_trader_id, out_sample_date=self.out_sample_date, online_date=self.online_date)
			obj_trader.pnl = df_trader_pnl[df_trader_pnl['TraderId'] == i_trader_id]
			self.list_traders.append(obj_trader)
		self.calculate_pnl()

	def calculate_pnl(self):
		if len(self.list_traders) < 1:
			return

		if self.portfolio_user_id == 'Benchmark':
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
	def __init__(self, Id, belong_strategy_id=None, out_sample_date=None, online_date=None):
		PMData.__init__(self, Id=Id, type='Trader')
		self.out_sample_date = out_sample_date
		self.online_date = online_date
		self.belong_strategy_id = belong_strategy_id

	def set_trader_pnl(self, df):
		df = df[['Date','Returns']]
		# df.set_index('Date', drop=True)
		self.pnl = df
