import pandas as pd


def strategy_type_get_strategies(list_type, func_sql_exec):
	list_re = []
	split_list = lambda l, x:[l[i:i + x] for i in range(0, len(l), x)]
	for list_type_split in split_list(list_type, 900):
		sql = '''
					SELECT 
						[Id]
				      ,[OutSampleDate]
				      ,[Type]
				      ,[OnlineDate]
				    FROM [Platinum.PM].[dbo].[StrategyDbo]
				    where Type in ('%s')
				''' % "','".join(list_type_split)
		re_sql = func_sql_exec(sql)
		if len(re_sql) > 0:
			df = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
			list_re.append(df)

	if len(list_re) > 0:
		df_strategy_info = pd.concat(list_re)
		return df_strategy_info
	else:
		return


def strategy_get_strategy_info(list_strategy_id, func_sql_exec):
	list_re = []
	split_list = lambda l, x:[l[i:i + x] for i in range(0, len(l), x)]
	for list_strategy_id_split in split_list(list_strategy_id, 900):
		sql = '''
				SELECT 
					[Id]
			      ,[OutSampleDate]
			      ,[Type]
			      ,[OnlineDate]
			    FROM [Platinum.PM].[dbo].[StrategyDbo]
			    where Id in ('%s')
			''' % "','".join(list_strategy_id_split)
		re_sql = func_sql_exec(sql)
		if len(re_sql) > 0:
			df = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
			list_re.append(df)

	if len(list_re) > 0:
		df_strategy_info = pd.concat(list_re)
		return df_strategy_info
	else:
		return


def strategy_get_trader_info(list_strategy_id, func_sql_exec):
	list_re = []
	split_list = lambda l, x:[l[i:i + x] for i in range(0, len(l), x)]
	for list_strategy_id_split in split_list(list_strategy_id, 900):
		sql = '''
					SELECT 
						[Id]
						,[StrategyId]
				    FROM [Platinum.PM].[dbo].[TraderDbo]
				    where StrategyId in ('%s')
			''' % "','".join(list_strategy_id_split)
		re_sql = func_sql_exec(sql)
		if len(re_sql) > 0:
			df = pd.DataFrame(re_sql, columns=['TraderId', 'StrategyId'])
			list_re.append(df)

	if len(list_re) > 0:
		df_trader_info = pd.concat(list_re)
		return df_trader_info
	else:
		return


def trader_get_trader_info(list_trader_id, func_sql_exec):
	list_re = []
	split_list = lambda l, x:[l[i:i + x] for i in range(0, len(l), x)]
	for list_trader_id_split in split_list(list_trader_id, 900):
		sql = '''
			SELECT 
			[Id]
			,[StrategyId]
			FROM [Platinum.PM].[dbo].[TraderDbo]
			where Id in ('%s')
		''' % "','".join(list_trader_id_split)
		re_sql = func_sql_exec(sql)
		if len(re_sql) > 0:
			df = pd.DataFrame(re_sql, columns=['TraderId', 'StrategyId'])
			list_re.append(df)

	if len(list_re) > 0:
		df_trader_info = pd.concat(list_re)
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


def strategy_name_get_strategy_info(list_strategy_name, func_sql_exec):
	if len(list_strategy_name) < 1:
		return
	else:
		list_re = []
		split_list = lambda l,x: [l[i:i+x] for i in range(0,len(l),x)]
		for list_strategy_name_split in split_list(list_strategy_name, 900):
			sql = '''
					SELECT 
						[Id]
				      ,[OutSampleDate]
				      ,[Type]
				      ,[OnlineDate]
				    FROM [Platinum.PM].[dbo].[StrategyDbo]
				    where Name in ('%s')
				''' % "','".join(list_strategy_name_split)
			re_sql = func_sql_exec(sql)
			if len(re_sql) > 0:
				df = pd.DataFrame(re_sql, columns=['Id', 'OutSampleDate', 'Type', 'OnlineDate'])
				list_re.append(df)

		if len(list_re) > 0:
			df_strategy_info = pd.concat(list_re)
			return df_strategy_info
		else:
			return
