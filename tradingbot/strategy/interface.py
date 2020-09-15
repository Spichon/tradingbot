import pandas
import numpy as np


class strategy_interface:
    def __init__(self, name, df):
        self.df = df
        self.name = name

    def populate(self):
        """Add indicator columns"""
        pass

    def get_signals(self):
        """Generate bullish or bearish signals"""
        pass

    def get_asset_return(self):
        self.df['asset_log_returns'] = np.log(self.df['close']).diff()
        self.df['strategy_asset_log_returns'] = self.df['position'] * self.df['asset_log_returns']
        self.df['cum_strategy_asset_log_returns'] = self.df['strategy_asset_log_returns'].cumsum()
        self.df['cum_strategy_asset_relative_returns'] = np.exp(self.df['cum_strategy_asset_log_returns']) - 1
        return self.df['cum_strategy_asset_relative_returns']

    def draw_indicators(self):
        pass


