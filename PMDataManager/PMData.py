from datetime import datetime
import pandas as pd
import numpy as np


'''
	PMData
		:pnl
			pd.DataFrame(columns=['Pnl', 'Commission', 'Slippage', 'Capital', 'Returns']), index=[datetime()]
			包含 多个序列信息
		:returns
			pd.DataFrame(columns=['Returns']), index=[datetime()]
			
		cal_std()
			对returns进行标准化 （vol=12%）,
			需要指定用于计算vol的时间区间，然后对全时间区间进行std,
			并返回全时间区间的std_returns
		describe()
			需要输入两个时间区间，第一个时间区间用于标准化计算和转换（若不做标准化则不需要），第二个时间区间用于 计算统计值。 
			例如对 2017/1/1 - 2017/12/31数据进行标准化，再计算 2017/6/1 - 2017/12/31的统计值。
				方法中需要用到range(1,n)记录和计算序列序号，所以需要进行reset_index
		
'''


class PMData:
	def __init__(self, Id, type, dt_start_date=datetime(year=2017, month=7, day=1), dt_end_date=datetime.today()):
		self.Id = Id
		self.type = type
		self.dt_start_date = dt_start_date
		self.dt_end_date = dt_end_date
		self.pnl = pd.DataFrame(columns=['Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])
		self.returns = pd.DataFrame(columns=['Returns'])

	# 计算 return std sharpe mdd等
	# self.describe( is_use_std=True )时需要用到self.cal_std_returns
	def describe(self, start_date=None, end_date=None, is_use_std=True, std_start_date=None, std_end_date=None):
		'''
		:param start_date:      计算describe数据的起始日期
		:param end_date:        计算describe数据的结束日期
		:param is_use_std:      是否需要 标准化数据（使std=12%）
		:param std_start_date:  用于标准化数据的起始日期
		:param std_end_date:    用于标准化数据（的结束日期
		:return:

		两组date的用处，如： 2017/1/1 - 2017/12/31数据进行标准化，再计算 2017/6/1 - 2017/12/31的统计值。
		df_returns: 用于计算describe的df，
			若不需要标准版df_returns=self.returns，
			若需要标准化df_returns=pd.DataFrame(self.cal_std_returns(start_date=std_start_date, end_date=std_end_date))
		'''

		def cal_stat():
			if len(df_returns) < 1:
				return
			first_date = min(df_returns['Date'].tolist())
			last_date = max(df_returns['Date'].tolist())

			r_describe = df_returns['Returns'].describe()
			count = int(r_describe['count'])
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
			if len(df_returns) < 1:
				return
			df_returns['Returns_cumsum'] = df_returns['Returns'].cumsum()
			df_cum = df_returns[['Date', 'Returns_cumsum']]

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

		# 初始化describe数值
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
			start_date = self.dt_start_date
		if end_date is None:
			end_date = self.dt_end_date

		if is_use_std:
			# 若需要标准化数据，但未传入 std_start_date或std_end_date，便用start_date end_date替代
			if std_start_date is None:
				std_start_date = start_date
			if std_end_date is None:
				std_end_date = end_date
			df_returns = pd.DataFrame(self.cal_std_returns(start_date=std_start_date, end_date=std_end_date))
		else:
			df_returns = pd.DataFrame(self.returns)

		# 数据处理
		if len(df_returns) == 0:
			return None
		df_returns = df_returns.reset_index()
		df_returns = df_returns.loc[df_returns['Date'] <= end_date, :]
		df_returns = df_returns.loc[df_returns['Date'] >= start_date, :]
		df_returns = df_returns.reset_index(drop=True)

		# 计算
		cal_stat()
		cal_mdd()
		return dict_describe

	# 给定日期，进行标准化
	# 需要用到 self.describe( is_use_std=False )
	def cal_std_returns(self, start_date=None, end_date=None):
		if not (type(self.returns) == pd.DataFrame):
			return None
		elif len(self.returns) == 0:
			return None
		else:
			if start_date is None or start_date == "":
				start_date = self.dt_start_date
			if end_date is None or end_date == '':
				end_date = self.dt_end_date
			dict_describe = self.describe(start_date=start_date, end_date=end_date, is_use_std=False)

			if dict_describe is None:
				return None
			init_annual_std = float(dict_describe['annual_std'])
			if init_annual_std != 0:
				mul = 0.12 / init_annual_std
			else:
				mul = 0
			df_std_returns = pd.DataFrame(self.returns).copy()
			df_std_returns['Returns'] = df_std_returns['Returns'] * mul
		return df_std_returns


class PMProduct(PMData):
	def __init__(self, Id, user, product_start_at_create=True, strategy_use_last_portfolio=True):
		'''
		:param Id:
		:param user:
		:param product_start_at_create:
		:param strategy_use_last_portfolio: 若使用portfolio的strategy，则存在用哪一个portfolio的问题，
			若为True则用最后一个，若为False则将各段portfolio连接合并。
		'''
		PMData.__init__(self, Id=Id, type='Product')
		self.portfolio_user_id = user
		self.list_strategies_id = []
		self.strategies_weight = pd.DataFrame(columns=['Date', 'StrategyId', 'PortfolioUserId', 'Weight'])

		self.product_start_at_create = product_start_at_create
		self.strategy_use_last_portfolio = strategy_use_last_portfolio
		self.list_strategies = []


class PMStrategy(PMData):
	def __init__(self, Id, portfolio_user_id='Benchmark',
	             use_last_portfolio=False, list_trader_id=None, list_traders=None,
	             strategy_type=None, out_sample_date=None, online_date=None):
		'''
		:param Id:
		:param portfolio_user_id:
		:param use_last_portfolio:
		:param list_trader_id: trader的id
		:param list_traders:用于绑定存放trader实例
		:param strategy_type:
		:param out_sample_date:
		:param online_date:
		'''
		PMData.__init__(self, Id=Id, type='Strategy')

		self.list_trader_id = list_trader_id
		if not list_traders:
			self.list_traders = []
		else:
			self.list_traders = list_traders

		self.strategy_type = strategy_type
		self.out_sample_date = out_sample_date
		self.online_date = online_date

		self.portfolio_user_id = portfolio_user_id
		self.use_last_portfolio = use_last_portfolio
		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])

	def set_strategy(self, df_trader_pnl):
		if len(self.list_trader_id) == 0:
			return
		# 创建trader实例，绑定在 self.list_trader
		for i_trader_id in self.list_trader_id:
			obj_trader = PMTrader(
				i_trader_id,
				out_sample_date=self.out_sample_date,
				online_date=self.online_date,
				belong_strategy_id=self.Id
			)
			obj_trader.set_trader_pnl(df_trader_pnl=df_trader_pnl)
			self.list_traders.append(obj_trader)

		self.calculate_returns()

	def calculate_returns(self):
		if len(self.list_traders) < 1:
			return

		if self.portfolio_user_id == 'Benchmark':
			list_trader_returns = [i.returns for i in self.list_traders]
		else:
			list_trader_returns = []
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
					list_trader_returns.append(df_merge)
				except:
					continue

		if len(list_trader_returns) > 0:
			df_all_returns = pd.DataFrame(pd.concat(list_trader_returns))
			df_strategy_returns = pd.DataFrame(df_all_returns.groupby(by=df_all_returns.index)['Returns'].sum())
			self.returns = df_strategy_returns
		else:
			pass


class PMTrader(PMData):
	def __init__(self, Id, belong_strategy_id=None, out_sample_date=None, online_date=None):
		PMData.__init__(self, Id=Id, type='Trader')
		self.out_sample_date = out_sample_date
		self.online_date = online_date
		self.belong_strategy_id = belong_strategy_id

	def set_trader_pnl(self, df_trader_pnl):
		df = df_trader_pnl.loc[
			df_trader_pnl['TraderId'] == self.Id,
			['Date', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns']
		]
		df = df.set_index('Date', drop=True)
		self.pnl = df
		self.returns = df[['Returns']]
