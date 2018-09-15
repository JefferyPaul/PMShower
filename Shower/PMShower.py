from Shower.PMItem import PMItem
from datetime import *
from PMDataManager.data_collector import *
from PMDataManager import db_checker


class PMShower:
	def __init__(self, start_date=None, end_date=None):
		def set_date(ser_type):
			if ser_type == 'start':
				return datetime(year=2015, month=1, day=1)
			else:
				return datetime.today()

		self.items = []
		if start_date is None:
			self.start_date = set_date("start")
		else:
			self.start_date = start_date
		if end_date is None:
			self.end_date = set_date("end")
		else:
			self.end_date = end_date

	def select_item(self):
		item = db_checker
		self.add_item(item)
		pass

	def add_item(self):
		item = PMItem(
			Trader_Short_Id=None
		)
		self.items.append(item)

	def collect_data(self):
		pass

	def show(self, set_mdd=None, set_volatility=None):
		data = data_collector(self.items)
		pass
