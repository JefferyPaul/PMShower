import pandas as pd


class PMData:
    def __init__(self, id):
        self.id = id
        self.pnl = 0

    def describe(self, start_date=0, end_date=0):
        pass

    def set_start_date(self):
        pass

    def set_end_date(self):
        pass


class Product(PMData):
    def __init__(self, id):
        PMData.__init__(self, id)
        self.portfolio_user_id = ""
        self.strategies = []
        self.strategies_weight = []

    def calculate_pnl(self):
        pass

    def get_strategies(self):
        pass


class Strategy(PMData):
    def __init__(self):
        PMData.__init__(self)
        self.traders = []

    def calculate_pnl(self):
        pass

    def get_traders(self):
        pass


class Trader(PMData):
    def __init__(self):
        PMData.__init__(self)

    def get_pnl(self):
        pass
