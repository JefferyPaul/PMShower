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
		self.traders_id = []
		self.traders_weight = pd.DataFrame(columns=['Date', 'TraderId', 'Weight'])
		self.portfolio_user_id = portfolio_user_id

		self.traders = []
		self.pnl = 0

	def get_traders_sql(self):
		sql = '''
			SELECT Id
		      FROM [Platinum.PM].[dbo].[TraderDbo]
             where StrategyId = '%s'
        ''' % self.Id
		return sql

	def get_portfolio_sql(self):
		sql = '''
			SELECT [Date],[TraderId],[Weight]
			  FROM [Platinum.PM].[dbo].[PortfolioTraderWeightDbo]
			  where UserId = '%s' and TraderId in ('%s')
	    ''' % (self.portfolio_user_id, "','".join(self.traders_id))
		return sql

	def set_strategy_traders(self, l):
		self.traders_id = pd.DataFrame(l).loc[:, 0].tolist()

	def set_portfolio(self, l):
		if len(self.traders_id) > 0:
			df = pd.DataFrame(l, columns=['Date', 'TraderId', 'Weight'])
			self.traders_weight = df
		else:
			print('Wrong in PMStrategy.set_portfolio, no traders')

	def calculate_pnl(self):

		pass


class PMTrader(PMData):
	def __init__(self, Id):
		PMData.__init__(self, Id=Id, type='Trader')
		self.pnl = pd.DataFrame(columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital', 'Returns'])

	def get_pnl_sql(self):
		sql = '''
			SELECT [Date],[TraderId],[Pnl],[Commission],[Slippage],[Capital]
		    FROM [Platinum.PM].[dbo].[TraderLogDbo]
		    where TraderId = '%s' and  Date>'%s' and Date < '%s'
        ''' % (self.Id, self.start_date.strftime('%Y%m%d'), self.end_date.strftime('%Y%m%d'))
		return sql

	def set_pnl(self, df):
		if type(df) == pd.DataFrame:
			df = pd.DataFrame(df, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
			pass
		else:
			try:
				df = pd.DataFrame(df, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
			except:
				print('Wrong in PMTrader.set_pnl, because the input df type is wrong')

		df['Returns'] = df['Pnl'] / df['Commission']
		self.pnl = df
