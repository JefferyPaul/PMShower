from PMDataManager.PMItem import PMItem
from PMDataManager.data_collector import *


class PMShower:
	def __init__(self, start_date=None, end_date=None):
		self.list_items = []
		if start_date is None:
			self.start_date = self.set_date("start")
		else:
			self.start_date = start_date
		if end_date is None:
			self.end_date = self.set_date("end")
		else:
			self.end_date = end_date

	def set_date(self, ser_type):
		if ser_type == 'start':
			return datetime(year=2015, month=1, day=1)
		else:
			return datetime.today()

	def add_item(self):
		item = PMItem(
			trader_id=None
		)
		self.list_items.append(item)

	def show(self):
		data = data_collector(self.list_items)
		pass
