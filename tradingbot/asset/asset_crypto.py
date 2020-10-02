from tradingbot.cotation import cotation_interface
from tradingbot.asset import asset_interface
from tradingbot.strategy import strategy_interface


class asset_crypto(asset_interface):
    def __init__(self, asset: str, cotation_place: cotation_interface, strategies: [strategy_interface] = None):
        super().__init__(asset, cotation_place, strategies)
