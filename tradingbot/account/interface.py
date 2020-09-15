import krakenex


class account_interface:

    def add_order(self, pair, type, ordertype, volume):
        pass

    def cancel_order(self, txid):
        pass

    def get_query_orders(self):
        pass

    def get_balances(self):
        pass

    def get_open_orders(self):
        pass

    def get_closed_orders(self):
        pass

    def get_open_positions(self):
        pass

    def get_trade_balance(self, asset):
        pass

    def get_trade_volume(self):
        pass

    def get_query_trade(self, txids: []):
        pass

    def get_trades_history(self):
        pass
