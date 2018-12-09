from datetime import datetime
import pandas as pd
import numpy as np


# [ {product, user}, {product, user}, {}, ] 需要 product_name 和 user
# def product_get_strategy(list_product_user, sql_exec):
# 	df = pd.DataFrame(list_product_user)
# 	# if df['user'] = nan:
#
# 	sql = '''
# 				SELECT [Date],[StrategyId],[PortfolioUserId],[Weight]
# 				  FROM [Platinum.PM].[dbo].[ProductPortfolioWeightDbo]
# 				  where ProductId = '%s' and PortfolioUserId = '%s'
# 	        ''' % (Id, portfolio_user_id)
# 	re_sql = sql_exec(sql)
# 	if len(re_sql) <= 0:
# 		return
# 	df = pd.DataFrame(re_sql, columns=['Date', 'StrategyId', 'PortfolioUserId', 'Weight'])
# 	strategies_weight = df
# 	list_strategies_id = df['StrategyId'].tolist()
#
# 	if product_start_at_create:
# 		create_date = min(df['Date'].tolist())
# 		start_date = datetime.strptime(create_date, '%Y%m%d')
#
# 	if len(list_strategies_id) < 1:
# 		pass
# 	else:
# 		for strategy_id in list_strategies_id:
# 			strategy_portfolio_user_id = strategies_weight.loc[
# 				strategies_weight['StrategyId'] == strategy_id, 'PortfolioUserId'
# 			].tolist()[0]
# 			strategy = PMStrategy(Id=strategy_id, portfolio_user_id=strategy_portfolio_user_id,
# 			                      use_last_portfolio=strategy_use_last_portfolio)
# 			strategy.set_start_date(start_date)
# 			strategy.set_end_date(end_date)
# 			strategy.get_data(sql_exec)
# 			list_strategies.append(strategy)

def strategy_type_get_strategies(list_type, func_sql_exec):
	if len(list_type) < 1:
		return ""
	sql = '''
			SELECT 
				[Id]
		      ,[OutSampleDate]
		      ,[Type]
		      ,[OnlineDate]
		    FROM [Platinum.PM].[dbo].[StrategyDbo]
		    where type in ('%s')
	    ''' % "','".join(list_type)
	re_sql = func_sql_exec(sql)
	if len(re_sql) > 0:
		df_strategy_info = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
		return df_strategy_info
	else:
		return 


def strategy_get_strategy_info(list_strategy, func_sql_exec):
	if len(list_strategy) < 1:
		return ""
	sql = '''
			SELECT 
				[Id]
		      ,[OutSampleDate]
		      ,[Type]
		      ,[OnlineDate]
		    FROM [Platinum.PM].[dbo].[StrategyDbo]
		    where Id in ('%s')
	    ''' % "','".join(list_strategy)
	re_sql = func_sql_exec(sql)
	if len(re_sql) > 0:
		df_strategy_info = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
		return df_strategy_info
	else:
		return


def strategy_get_trader(list_strategy, func_sql_exec):
	sql = '''
				SELECT 
					[Id]
					,[StrategyId]
			    FROM [Platinum.PM].[dbo].[TraderDbo]
			    where StrategyId in ('%s')
		''' % "','".join(list_strategy)
	re_sql = func_sql_exec(sql)
	if len(re_sql) > 0:
		df_trader_info = pd.DataFrame(re_sql, columns=['TraderId', 'StrategyId'])
		return df_trader_info
	else:
		return 


def trader_get_weight(list_trader_id, func_sql_exec, user_id='Benchmark', use_last_portfolio=True):
	if len(list_trader_id) < 1:
		return
	else:
		list_re = []
		split_list = lambda l,x: [l[i:i+x] for i in range(0,len(l),x)]
		for list_trader_id_split in split_list(list_trader_id, 900):
			sql = '''
				SELECT 
					[Date]
					,[TraderId]
					,[Weight]
				FROM [Platinum.PM].[dbo].[PortfolioTraderWeightDbo]
				where UserId = '%s' and TraderId in ('%s')
		    ''' % (user_id, "','".join(list_trader_id_split))
			re_sql = func_sql_exec(sql)
			if len(re_sql) > 0:
				df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Weight'])
				list_re.append(df)

		if len(list_re) > 0:
			df_trader_weight = pd.concat(list_re)
			# 使用最新的portfolio
			# if use_last_portfolio:
			# 	last_date = max(set(trader_weight['Date'].tolist()))
			# 	trader_weight = trader_weight.loc[trader_weight['Date'] == last_date, :]
			return df_trader_weight
		else:
			return


def trader_get_trader_pnl(list_trader_id, func_sql_exec, start_date, end_date):
	if len(list_trader_id) < 1:
		return
	else:
		list_re = []
		split_list = lambda l,x: [l[i:i+x] for i in range(0,len(l),x)]
		for list_trader_id_split in split_list(list_trader_id, 900):
			sql = '''
						SELECT 
							[Date]
							,[TraderId]
							,[Pnl]
							,[Commission]
							,[Slippage]
							,[Capital]
					    FROM [Platinum.PM].[dbo].[TraderLogDbo]
					    where Date>='%s' and Date<='%s' and TraderId in ('%s')
			        ''' % (start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'),  "','".join(list_trader_id_split))
			re_sql = func_sql_exec(sql)
			if len(re_sql) > 0:
				df = pd.DataFrame(re_sql, columns=['Date', 'TraderId', 'Pnl', 'Commission', 'Slippage', 'Capital'])
				df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
				df = df[df['Capital'] > 0]
				df['Returns'] = df['Pnl'] / df['Capital']
				list_re.append(df)

		if len(list_re) > 0:
			df_trader_pnl = pd.concat(list_re)
			return df_trader_pnl
		else:
			return
