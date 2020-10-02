from tradingbot.strategy import strategy_interface

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class sma_strategy(strategy_interface):
    def __init__(self, name: str, n1: int, n2: int):
        self.n1 = n1
        self.n2 = n2
        super().__init__(name)

    def populate(self, df: pd.DataFrame) -> pd.DataFrame:
        price = df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        sma1 = pd.Series(price.rolling(window=self.n1).mean(), name='{}_{}'.format(self.name, self.n1))
        sma2= pd.Series(price.rolling(window=self.n2).mean(), name='{}_{}'.format(self.name, self.n2))
        df = df.join(sma1)
        df = df.join(sma2)
        return df

    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['{}_position'.format(self.name)] = np.sign(df['close'] - df['{}_{}'.format(self.name, self.n2)])
        df['{}_position'.format(self.name)] = df['{}_position'.format(self.name)].shift(1)
        return df

    def get_signal(self, df: pd.DataFrame) -> int:
        return int(df['{}_position'.format(self.name)].tail(1).values[0])

    def draw_indicator(self, df: pd.DataFrame, ax: plt.subplot2grid):
        ax.plot(df['time'], df['{}_{}'.format(self.name, self.n1)], color='green',
                label='{}_{}'.format(self.name, self.n1))
        ax.plot(df['time'], df['{}_{}'.format(self.name, self.n2)], color='red',
                label='{}_{}'.format(self.name, self.n2))

