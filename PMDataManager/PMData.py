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

	def cal_describe(self, df=None, start_date=None, end_date=None, item='All'):
		def cal_stat(df):
			df = pd.DataFrame(df)
			r_describe = df['Returns'].describe()

			annualized_std = r_describe['std'] * np.sqrt(250)
			daily_return = r_describe['mean']
			annualized_return = r_describe['mean'] / r_describe['count'] * 250
			sharp = annualized_return / annualized_std

			dict_stat = {"annualized_std": annualized_std,
			             "daily_return": daily_return,
			             "annualized_return": annualized_return,
			             "sharp": sharp}
			return dict_stat

		def cal_mdd(df):
			df = pd.DataFrame(df)
			df['Returns_cumsum'] = df['Returns'].cumsum()
			df_cum = df[['Date','Returns_cumsum']]

			df_cum['max_here'] = df_cum['Returns_cumsum'].expanding().max()
			df_cum['dd_here'] = df_cum['max_here'] - df_cum['Returns_cumsum']
			df_cum.loc[df_cum['dd_here'] == 0, 'max_here_index'] = df_cum.loc[df_cum['dd_here'] == 0, :].index
			df_cum['max_here_index'] = df_cum['max_here_index'].fillna(method='ffill')
			df_cum['dd_period'] =  df_cum.index - df_cum['max_here_index']

			series_mdd = df_cum.loc[df_cum['dd_here']==df_cum['dd_here'].max(), :]
			mdd = float(series_mdd['dd_here'])
			mdd_date = int(series_mdd['Date']).__str__()
			mdd_start_date = int(
				df_cum.loc[series_mdd['max_here_index'], 'Date']).__str__()

			series_lddp = df_cum.loc[df_cum['dd_period']==df_cum['dd_period'].max(), :]
			lddp = int(series_lddp['dd_period']).__str__()
			lddp_end_date = int(series_lddp['Date']).__str__()
			lddp_start_date = int(
				df_cum.loc[series_lddp.index - series_lddp['dd_period'], 'Date']).__str__()

			dict_mdd = {"mdd":mdd,
			            "mdd_date":mdd_date,
			            "mdd_start_date":mdd_start_date,
			            "lddp":lddp,
			            "lddp_end_date":lddp_end_date,
			            "lddp_start_date":lddp_start_date}
			return dict_mdd

		if df is None:
			if not (type(self.pnl) == pd.DataFrame):
				return pd.Series()
			else:
				df = pd.DataFrame(self.pnl)
		else:
			df = pd.DataFrame(df)

		if start_date is None:
			start_date = self.start_date.strftime('%Y%m%d')
		if end_date is None:
			end_date = self.end_date.strftime('%Y%m%d')

		df = df.loc[df['Date'] <= end_date, :]
		df = df.loc[df['Date'] >= start_date, :]
		df = df.reset_index(drop=True)

		dict_stat = {}
		dict_mdd = {}
		if item == 'All' or item == 'stat':
			dict_stat = cal_stat(df)
		if item == 'All' or item == 'mdd':
			dict_mdd = cal_mdd(df)

		series_des = pd.Series(dict(dict_stat, **dict_mdd))
		return series_des

	def pnl_standardize(self):
		if not(type(self.pnl) == pd.DataFrame):
			pass
		else:
			series_des = self.cal_describe(item='stat')
			init_annualized_std = float(series_des.annualized_std)
			mul = 0.12 / init_annualized_std
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

	def get_product_inf(self, sql_exec):
		sql = '''
			SELECT [Date],[StrategyId],[PortfolioUserId],[Weight]
			  FROM [Platinum.PM].[dbo].[ProductPortfolioWeightDbo]
			  where ProductId = '%s' and PortfolioUserId = '%s'
        ''' % (self.Id, self.portfolio_user_id)
		re_sql = sql_exec(sql)
		df = pd.DataFrame(re_sql, columns=['Date', 'StrategyId', 'PortfolioUserId', 'Weight'])
		self.strategies_weight = df
		self.list_strategies_id = df['StrategyId'].tolist()

		if self.product_start_at_create:
			create_date = min(df['Date'].tolist())
			self.start_date = datetime.strptime(create_date, '%Y%m%d')

	def get_product_strategies(self, sql_exec):
		if len(self.list_strategies_id) < 1:
			pass
		else:
			for strategy_id in self.list_strategies_id:
				strategy_portfolio_user_id = self.strategies_weight.loc[self.strategies_weight['StrategyId'] == strategy_id,
				                                                        'PortfolioUserId'].tolist()[0]
				strategy = PMStrategy(Id=strategy_id, portfolio_user_id=strategy_portfolio_user_id,
				                      use_last_portfolio=self.strategy_use_last_portfolio)
				strategy.set_start_date(self.start_date)
				strategy.set_end_date(self.end_date)

				strategy.get_traders_id(sql_exec)
				strategy.get_portfolio(sql_exec)
				strategy.get_strategy_traders(sql_exec)
				strategy.calculate_pnl()
				self.list_strategies.append(strategy)

	def calculate_pnl(self):
		if len(self.list_strategies) < 1:
			pass
		else:
			l_df = []
			for strategy in self.list_strategies:
				df_pnl = strategy.pnl
				df_weight = self.strategies_weight.loc[self.strategies_weight['StrategyId'] == strategy.Id, :]

				df_merge = pd.merge(left=df_pnl, right=df_weight, on='Date', how='left')
				df_merge = df_merge.sort_values(by='Date')
				df_merge = df_merge.fillna(method='ffill')
				if self.product_start_at_create:
					df_merge = df_merge.fillna(0)
				else:
					df_merge = df_merge.fillna(method='bfill')
				df_merge['portfolio_returns'] = df_merge['Returns'] * df_merge['Weight']
				l_df.append(df_merge)
			df = pd.DataFrame(pd.concat(l_df))
			df_r = pd.DataFrame(df.groupby(by='Date')['portfolio_returns'].sum())
			df_r.rename(columns={'portfolio_returns': 'Returns'}, inplace=True)
			df_r['Date'] = df_r.index
			df_r = df_r.reset_index(drop=True)
			self.pnl = df_r


class PMStrategy(PMData):
	def __init__(self, Id, portfolio_user_id='Benchmark', use_last_portfolio=False):
		PMData.__init__(self, Id=Id, type='Strategy')
		self.list_traders_id = []
		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])
		self.portfolio_user_id = portfolio_user_id
		
		self.use_last_portfolio = use_last_portfolio
		self.list_traders = []

	def get_traders_id(self, sql_exec):
		sql = '''
			SELECT Id
		      FROM [Platinum.PM].[dbo].[TraderDbo]
             where StrategyId = '%s'
        ''' % self.Id
		re_sql = sql_exec(sql)
		self.list_traders_id = pd.DataFrame(re_sql).loc[:, 0].tolist()

	def get_portfolio(self, sql_exec):
		if len(self.list_traders_id) < 1:
			pass
		else:
			sql = '''
				SELECT [Date],[TraderId],[Weight]
				  FROM [Platinum.PM].[dbo].[PortfolioTraderWeightDbo]
				  where UserId = '%s' and TraderId in ('%s')
		    ''' % (self.portfolio_user_id, "','".join(self.list_traders_id))
			re_sql = sql_exec(sql)
			df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Weight'])
			
			if not self.use_last_portfolio:
				self.traders_weight = df
			else:
				last_date = max(set(df['Date'].tolist()))
				df = df.loc[df['Date'] == last_date, :]
				self.traders_weight = df

	def get_strategy_traders(self, sql_exec):
		if len(self.list_traders_id) < 1:
			pass
		else:
			for trader_id in self.list_traders_id:
				trader = PMTrader(Id=trader_id)
				trader.set_start_date(self.start_date)
				trader.set_end_date(self.end_date)
				trader.get_pnl(sql_exec)
				self.list_traders.append(trader)
			print('%s - Get Strategy Traders - Done' % self.Id)

	def calculate_pnl(self):
		if len(self.list_traders) < 1:
			pass
		else:
			l_df = []
			for trader in self.list_traders:
				df_pnl = trader.pnl
				df_weight = self.traders_weight

				df_merge = pd.merge(left=df_pnl, right=df_weight, on=['TraderId', 'Date'], how='left')
				df_merge = df_merge.sort_values(by=['TraderId', 'Date'])
				df_merge = df_merge.fillna(method='ffill')
				df_merge = df_merge.fillna(method='bfill')
				df_merge['portfolio_returns'] = df_merge['Returns'] * df_merge['Weight']
				l_df.append(df_merge)
			df = pd.DataFrame(pd.concat(l_df))
			df_r = pd.DataFrame(df.groupby(by='Date')['portfolio_returns'].sum())
			df_r.rename(columns = {'portfolio_returns': 'Returns'}, inplace=True)
			df_r['Date'] = df_r.index
			df_r = df_r.reset_index(drop=True)
			self.pnl = df_r


class PMTrader(PMData):
	def __init__(self, Id):
		PMData.__init__(self, Id=Id, type='Trader')
		self.pnl = pd.DataFrame(columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	def get_pnl(self, sql_exec):
		sql = '''
			SELECT [Date],[TraderId],[Pnl],[Commission],[Slippage],[Capital]
		    FROM [Platinum.PM].[dbo].[TraderLogDbo]
		    where TraderId = '%s' and  Date>='%s' and Date<='%s'
        ''' % (self.Id, self.start_date.strftime('%Y%m%d'), self.end_date.strftime('%Y%m%d'))
		re_sql = sql_exec(sql)
		df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
		df['Returns'] = df['Pnl'] / df['Capital']
		self.pnl = df
