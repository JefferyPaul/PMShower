from datetime import datetime
import pandas as pd


class PMData:
	def __init__(self, Id, type, start_date=datetime(year=2017, month=7, day=1), end_date=datetime.today()):
		self.Id = Id
		self.type = type
		self.pnl = 0
		self.start_date = start_date
		self.end_date = end_date

	def describe(self, start_date=0, end_date=0):
		pass

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


class PMProduct(PMData):
	def __init__(self, Id, user):
		PMData.__init__(self, Id=Id, type='Product')
		self.portfolio_user_id = user
		self.strategies = []
		self.strategies_weight = []

	def calculate_pnl(self):
		pass

	def get_strategies_sql(self):
		sql = '''
			SELECT *
			  FROM [Platinum.PM].[dbo].[ProductPortfolioWeightDbo]
			  where ProductId = '%s' and PortfolioUserId = '%s'
        ''' % (self.Id, self.portfolio_user_id)
		return sql


class PMStrategy(PMData):
	def __init__(self, Id, portfolio_user_id='Benchmark'):
		PMData.__init__(self, Id=Id, type='Strategy')
		self.list_traders_id = []
		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])
		self.portfolio_user_id = portfolio_user_id

		self.list_traders = []
		self.pnl = pd.DataFrame(columns=['Returns'])

	def get_traders_id(self, sql_exec):
		sql = '''
			SELECT Id
		      FROM [Platinum.PM].[dbo].[TraderDbo]
             where StrategyId = '%s'
        ''' % self.Id
		re_sql = sql_exec(sql)
		self.list_traders_id = pd.DataFrame(re_sql).loc[:, 0].tolist()

	def get_portfolio_sql(self, sql_exec):
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
				df_merge = df_merge.fillna(1)
				df_merge['portfolio_returns'] = df_merge['Returns'] * df_merge['Weight']
				l_df.append(df_merge)
			df = pd.DataFrame(pd.concat(l_df))
			df_r = pd.DataFrame(df.groupby(by='Date')['Returns'].sum())
			self.pnl = df_r


class PMTrader(PMData):
	def __init__(self, Id):
		PMData.__init__(self, Id=Id, type='Trader')
		self.pnl = pd.DataFrame(columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	def get_pnl(self, sql_exec):
		sql = '''
			SELECT [Date],[TraderId],[Pnl],[Commission],[Slippage],[Capital]
		    FROM [Platinum.PM].[dbo].[TraderLogDbo]
		    where TraderId = '%s' and  Date>'%s' and Date < '%s'
        ''' % (self.Id, self.start_date.strftime('%Y%m%d'), self.end_date.strftime('%Y%m%d'))
		re_sql = sql_exec(sql)
		df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
		df['Returns'] = df['Pnl'] / df['Capital']
		self.pnl = df
