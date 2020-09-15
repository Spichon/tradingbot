from tradingbot.strategy import strategy_interface
import pandas
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib import style

class ema_strategy(strategy_interface):

    def __init__(self, name, df, n1, n2):
        super().__init__(name, df)
        self.n1 = n1
        self.n2 = n2

    def populate(self):
        price = self.df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        ema = pd.Series(price.ewm(span=self.n1, min_periods=self.n1).mean(), name='EMA_{}'.format(self.n1))
        self.df = self.df.join(ema)
        ema2 = pd.Series(price.ewm(span=self.n2, min_periods=self.n2).mean(), name='EMA_{}'.format(self.n2))
        self.df = self.df.join(ema2)

    def get_signals(self):
        self.df['position'] = np.sign(self.df['EMA_{}'.format(self.n1)] - self.df['EMA_{}'.format(self.n2)])
        self.df['position'] = self.df['position'].shift(1)

    def get_signal(self):
        self.df['position'] = np.sign(self.df['close'] - self.df['EMA_{}'.format(self.n2)])
        return int(self.df['position'].shift(1).tail(1))

    def draw_OHLC_with_indicator(self):
        style.use('ggplot')
        df = self.df
        df['time'] = df['time'].map(mdates.date2num)
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        candlestick_ohlc(ax1, df.values, width=0.01, colorup='green',
                         colordown='red')
        ax2.bar(df['time'], df['volume'], 0.015, color='k')
        ax1.plot(df['time'], df['EMA_{}'.format(self.n1)], color='green', label='EMA_{}'.format(self.n1))
        ax1.plot(df['time'], df['EMA_{}'.format(self.n2)], color='blue', label='EMA_{}'.format(self.n2))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
        plt.show()
