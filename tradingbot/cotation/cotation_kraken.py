from tradingbot.cotation import cotation_interface

import os
import krakenex
import pandas as pd
import csv
import time
import datetime


class cotation_kraken(cotation_interface):
    def __init__(self):
        key = os.getenv('key')
        secret = os.getenv('secret')
        super().__init__(krakenex.API(key=key, secret=secret))

    def get_ohlc(self, asset, ticker) -> {}:
        """get ohlc for relative asset and ticker"""
        return self.k.query_public('OHLC', {'pair': asset, 'interval': ticker})['result']

    def get_asset_info(self, asset):
        """get minimum trade volume and value"""
        assets = self.k.query_public('Assets', {'asset': asset})
        assets = assets['result']
        return assets

    def get_available_assets(self) -> {}:
        """get minimum trade volume and value"""
        assets = self.k.query_public('AssetPairs')
        assets = assets['result']
        return assets

    def get_trade_history(self, pair, since, path: '' = None):
        api_end = "9999999999"
        if path is None:
            path = 'backtesting/{}.csv'.format(pair)
        with open(path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["time", "price", "volume"])
            while True:
                api_data = self.k.query_public('Trades', {'pair': pair, 'since': since})
                if len(api_data["error"]) != 0:
                    time.sleep(3)
                    break
                for trade in api_data["result"][pair]:
                    if int(trade[2]) < int(api_end):
                        writer.writerow([datetime.datetime.fromtimestamp(int(trade[2])), trade[0], trade[1]])
                    else:
                        break
                since = api_data["result"]["last"]
