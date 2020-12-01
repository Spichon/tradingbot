class cotation_interface:
    def __init__(self, k):
        self.k = k

    def get_ohlc(self, asset, ticker) -> {}:
        """get ohlc for relative asset and ticker"""
        pass

    def get_trade_history(self, pair, since, file) -> {}:
        """get historical ohlc for relative asset and ticker"""
        pass

    def get_minimum_trade(self, pair) -> (int, int):
        """get minimum trade volume and value"""
        pass

    def get_available_assets(self) -> {} :
        """get all assets available for trading"""
        pass
