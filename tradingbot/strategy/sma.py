from tradingbot.strategy import strategy_interface
import pandas as pd
import numpy as np

class sma_strategy(strategy_interface):

    def __init__(self, name,  df, n1, n2):
        super().__init__(name, df)
        self.n1 = n1
        self.n2 = n2

    def populate(self):
        price = self.df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        sma = pd.Series(price.rolling(window=self.n2).mean(), name='SMA_{}'.format(self.n2))
        self.df = self.df.join(sma)

    def get_signals(self):
        self.populate()
        self.df['position'] = np.sign(self.df['close'] - self.df['SMA_{}'.format(self.n2)])
        self.df['position'] = self.df['position'].shift(1)
        return self.df['position']
