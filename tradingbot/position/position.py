import numpy as np


class position:
    def __init__(self, asset, df, signals, percent):
        self.asset = asset
        self.df = df
        self.percent = percent
        self.signals = signals

    def buy_position(self):
        pass

    def backtest(self):
        pass

    def get_asset_return(self):
        self.df['asset_log_returns'] = np.log(self.df['close']).diff()
        self.df['strategy_asset_log_returns'] = self.signals * self.df['asset_log_returns'] * self.percent
        self.df['cum_strategy_asset_log_returns'] = self.df['strategy_asset_log_returns'].cumsum()
        self.df['cum_strategy_asset_relative_returns'] = np.exp(self.df['cum_strategy_asset_log_returns']) - 1
        return self.df['cum_strategy_asset_relative_returns']
