
class PMItem:
    def __init__(self,
                 trader_id=None,
                 strategy_id=None,
                 strategy_portfolio_user_id=None,
                 product_id=None,
                 product_user_id=None
                 ):
        if trader_id is None:
            trader_id = []
        if strategy_id is None:
            strategy_id = []
        if strategy_portfolio_user_id is None:
            strategy_portfolio_user_id = ["Benchmark"]
        if product_id is None:
            product_id = []
        if product_user_id is None:
            product_user_id = []

        self.item = {
            "product_id": product_id,
            "product_user_id": product_user_id,
            "strategy_id": strategy_id,
            "strategy_portfolio_user_id": strategy_portfolio_user_id,
            "trader_id": trader_id
        }
