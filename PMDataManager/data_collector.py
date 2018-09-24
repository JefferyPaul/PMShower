import pandas as pd
from datetime import *
import pymssql
from SQL.MSSQL import MSSQL
from PMDataManager.PMData import *


def get_sql_config():
	return []


def data_collector(list_items):
	def get_trader_log(list_trader_id):
		list_returns = []
		for trader_id in list_trader_id:
			sql = "select * from TraderLogDbo " \
				  "where TraderId = '%s' " % (trader_id)
			list_returns += mssql.ExecQuery(sql=sql)
		df_returns = pd.DataFrame(
			list_returns,
			columns=[]
		)
		return df_returns

	def get_strategy_traders(list_strategy_id):
		list_returns = []
		for strategy_id in list_strategy_id:
			sql = "select * from TraderDbo " \
				  "where StrategyId = '%s' " % (strategy_id)
			list_returns += mssql.ExecQuery(sql=sql)
		df_returns = pd.DataFrame(
			list_returns,
			columns=['TraderId, StrategyId']
		)
		return df_returns

	def get_product_strategies(list_product_id):
		list_returns = []
		for product_id in list_product_id:
			sql = "select * from ProductPortfolioWeightDbo " \
				  "where ProductId = '%s'" % (product_id)
			list_returns += mssql.ExecQuery(sql=sql)
		df_returns = pd.DataFrame(
			list_returns,
			columns=['Date', 'ProductId', 'StrategyId', 'PortfolioUserId', 'Weight']
		)
		return df_returns

	def get_portfolio(list_portfolio_id):
		list_returns = []
		for i_StrategyId, i_UserId in list_portfolio_id:
			sql = "SELECT l.Date, l.UserId, l.TraderId, l.Weight, r.StrategyId" \
				  "FROM PortfolioTraderWeightDbo l left join PortfolioDbo r" \
				  "on l.UserId = r.UserId" \
				  "WHERE r.UserId = '%s' and StrategyId like '%s'" \
				  "order by Date" % (i_StrategyId, i_UserId)
			list_returns += mssql.ExecQuery(sql=sql)
		df_returns = pd.DataFrame(
			list_returns,
			columns=[]
		)
		return df_returns


	host, user, password, database = get_sql_config()
	mssql = MSSQL(host, user, password, database)

	for item in list_items:
		if item.ProductId:
			for product_id in item.ProductId:
				product = Product(id=product_id)

				df_product_strategies = pd.DataFrame(get_product_strategies(item.ProductId))
				# return - df.columns = [ Date, ProductId, StrategyId, PortfolioUserId, Weight ]
				list_strategy = df_product_strategies['StrategyId'].tolist()
				df_product_strategies["Weight_Percent"] = df_product_strategies["Weight"] / [
					df_product_strategies.groupby("ProductId")["Weight"].sum().to_dict()[i]
					for i in df_product_strategies["ProductId"].tolist()
				]
				df_strategy_weight = df_product_strategies[["StrategyId", "Weight_Percent"]]

				product.strategies = list_strategy
				product.strategies_weight = df_strategy_weight
				product.portfolio_user_id = df_product_strategies["PortfolioUserId"].unique().tolist()[0]

		if item.StrategyId:
			df_strategy_traders = pd.DataFrame(get_strategy_traders(item.StrategyId))
			# return - df.columns = ['TraderId, StrategyId']

		if item.Strategy_Portfolio_UserId:		# both Benchmark and userId need to do get_portfolio
			portfolio_returns = get_portfolio(item.Strategy_Portfolio_UserId)
			df_portfolio_returns = pd.DataFrame(portfolio_returns)
			# { strategy_name : [ trader_name: weight, trader_name: weight, }, }
			list_trader = df_portfolio_returns["TraderId"]

		if item.Trader_Id:
			trader_returns = get_trader_log(item.Trader_Id)
			pass

	mssql.close()
	# 如果正常运行，会在此断开conn；但若运行途中出现问题，conn会如何？
