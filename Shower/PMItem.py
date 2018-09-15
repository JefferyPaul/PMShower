
class PMItem:
    def __init__(self,
                 Trader_Short_Id = None,
                 StrategyId = None,
                 Strategy_Portfolio_UserId = None,
                 ProductId = None,
                 Product_UserId = None
                 ):
        if Trader_Short_Id is None:
            Trader_Short_Id = []
        if StrategyId is None:
            StrategyId = []
        if Strategy_Portfolio_UserId is None:
            Strategy_Portfolio_UserId = []
        if ProductId is None:
            ProductId = []
        if Product_UserId is None:
            Product_UserId = []

        self.item = {
            "Trader_Short_Id": Trader_Short_Id,
            "StrategyId": StrategyId,
            "Strategy_Portfolio_UserId": Strategy_Portfolio_UserId,
            "ProductId": ProductId,
            "Product_UserId": Product_UserId
        }
