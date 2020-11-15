from tradingbot.strategy import strategy_interface

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class ema_strategy(strategy_interface):
    def __init__(self, name: str, n1: int, n2: int):
        self.n1 = n1
        self.n2 = n2
        super().__init__(name)

    def get_positions(self, df: pd.DataFrame) -> pd.DataFrame:
        price = df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        ema = pd.Series(price.ewm(span=self.n1, min_periods=self.n1).mean(), name='{}_{}'.format(self.name, self.n1))
        ema2 = pd.Series(price.ewm(span=self.n2, min_periods=self.n2).mean(), name='{}_{}'.format(self.name, self.n2))
        df['{}_position'.format(self.name)] = np.sign(ema - ema2)
        df['{}_position'.format(self.name)] = df['{}_position'.format(self.name)].shift(1)
        return df