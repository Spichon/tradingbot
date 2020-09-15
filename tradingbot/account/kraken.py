import krakenex
from tradingbot.account import account_interface
import os

class kraken_account_wrapper(account_interface):
    def __init__(self):
        key = os.getenv('key')
        secret = os.getenv('secret')
        self.k = krakenex.API(key=key, secret=secret)

    def get_api(self):
        return self.k

    def add_order(self, pair, type, ordertype, volume):
        return self.k.query_private('AddOrder', {'pair': pair,
                                                 'type': type,
                                                 'ordertype': ordertype,
                                                 'volume': volume})

    def get_minimum_trade(self, pair):
        assets = self.k.query_public('AssetPairs')
        assets = assets['result']
        relevant_pair = assets[pair]
        return int(relevant_pair['ordermin']), int(relevant_pair['lot_decimals'])

    def cancel_order(self, txid):
        self.k.query_private('CancelOrder', {'txid': txid})

    def get_query_orders(self):
        self.k.query_private('QueryOrders')

    def get_balances(self):
        return self.k.query_private('Balance')['result']

    def get_open_orders(self):
        return self.k.query_private('OpenOrders')['result']['open']

    def get_closed_orders(self):
        return self.k.query_private('ClosedOrders')['result']

    def get_open_positions(self):
        return self.k.query_private('OpenPositions')

    def get_trade_balance(self, asset):
        return self.k.query_private('TradeBalance', {'asset': asset})

    def get_trade_volume(self):
        return self.k.query_private('TradeVolume')

    def get_query_trade(self, txids: []):
        return self.k.query_private('QueryTrades', {'txids': txids})

    def get_trades_history(self):
        return self.k.query_private('TradesHistory')
