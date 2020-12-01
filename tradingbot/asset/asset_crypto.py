from tradingbot.cotation import cotation_interface
from tradingbot.asset import asset_interface
from tradingbot.optimizer import optimizer_interface
from tradingbot.strategy import strategy_interface


class asset_crypto(asset_interface):
    def __init__(self, altname: str, base: str, quote: str, ordermin: float, lot_decimals: int,
                 cotation_place: cotation_interface, optimizer: optimizer_interface,
                 strategies: [strategy_interface] = None):
        super().__init__(altname=altname,
                         base=base,
                         quote=quote,
                         ordermin=ordermin,
                         lot_decimals=lot_decimals,
                         cotation_place=cotation_place,
                         optimizer=optimizer,
                         strategies=strategies
                         )
