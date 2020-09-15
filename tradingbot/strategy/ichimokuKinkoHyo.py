from tradingbot.strategy import strategy_interface
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib import style


class ichimoku_kinko_hyo_strategy(strategy_interface):

    def __init__(self, name, df):
        super().__init__(name, df)

    def populate(self):
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        nine_period_high = self.df['high'].rolling(window= 9).max()
        nine_period_low = self.df['low'].rolling(window= 9).min()
        self.df['tenkan_sen'] = (nine_period_high + nine_period_low) /2
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = self.df['high'].rolling(window=26).max()
        period26_low = self.df['low'].rolling(window=26).min()
        self.df['kijun_sen'] = (period26_high + period26_low) / 2
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        self.df['senkou_span_a'] = ((self.df['tenkan_sen'] + self.df['kijun_sen']) / 2).shift(26)
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = self.df['high'].rolling(window=52).max()
        period52_low = self.df['low'].rolling(window=52).min()
        self.df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(52)
        # The most current closing price plotted 26 time periods behind (optional)
        self.df['chikou_span'] = self.df['close'].shift(-26)
        self.df.dropna(inplace=True)

    def get_signals(self):
        self.populate()
        self.df['above_cloud'] = 0
        self.df['above_cloud'] = np.where((self.df['low'] > self.df['senkou_span_a'])  & (self.df['low'] > self.df['senkou_span_b'] ), 1, self.df['above_cloud'])
        self.df['above_cloud'] = np.where((self.df['high'] < self.df['senkou_span_a']) & (self.df['high'] < self.df['senkou_span_b']), -1, self.df['above_cloud'])
        self.df['A_above_B'] = np.where((self.df['senkou_span_a'] > self.df['senkou_span_b']), 1, -1)
        self.df['tenkan_kiju_cross'] = np.NaN
        self.df['tenkan_kiju_cross'] = np.where((self.df['tenkan_sen'].shift(1) <= self.df['kijun_sen'].shift(1)) & (self.df['tenkan_sen'] > self.df['kijun_sen']), 1, self.df['tenkan_kiju_cross'])
        self.df['tenkan_kiju_cross'] = np.where((self.df['tenkan_sen'].shift(1) >= self.df['kijun_sen'].shift(1)) & (self.df['tenkan_sen'] < self.df['kijun_sen']), -1, self.df['tenkan_kiju_cross'])
        self.df['price_tenkan_cross'] = np.NaN
        self.df['price_tenkan_cross'] = np.where((self.df['open'].shift(1) <= self.df['tenkan_sen'].shift(1)) & (self.df['open'] > self.df['tenkan_sen']), 1, self.df['price_tenkan_cross'])
        self.df['price_tenkan_cross'] = np.where((self.df['open'].shift(1) >= self.df['tenkan_sen'].shift(1)) & (self.df['open'] < self.df['tenkan_sen']), -1, self.df['price_tenkan_cross'])
        self.df['buy'] = np.NaN
        self.df['buy'] = np.where((self.df['above_cloud'].shift(1) == 1) & (self.df['A_above_B'].shift(1) == 1) & ((self.df['tenkan_kiju_cross'].shift(1) == 1) | (self.df['price_tenkan_cross'].shift(1) == 1)), 1, self.df['buy'])
        self.df['buy'] = np.where(self.df['tenkan_kiju_cross'].shift(1) == -1, 0, self.df['buy'])
        self.df['buy'].ffill(inplace=True)
        self.df['sell'] = np.NaN
        self.df['sell'] = np.where((self.df['above_cloud'].shift(1) == -1) & (self.df['A_above_B'].shift(1) == -1) & ((self.df['tenkan_kiju_cross'].shift(1) == -1) | (self.df['price_tenkan_cross'].shift(1) == -1)), -1, self.df['sell'])
        self.df['sell'] = np.where(self.df['tenkan_kiju_cross'].shift(1) == 1, 0, self.df['sell'])
        self.df['sell'].ffill(inplace=True)
        self.df['position'] = self.df['buy'] + self.df['sell']

    def draw_OHLC(self):
        style.use('ggplot')
        df = self.df
        df['time'] = df['time'].map(mdates.date2num)
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        candlestick_ohlc(ax1, df.values, width=0.01, colorup='green',
                         colordown='red')  # modifier le width selon l’intervalle
        ax2.bar(df['time'], df['volume'], 0.015, color='k')  # idem
        # ax1.plot(df['time'], df['EMA_5'], color='blue', label='EMA_5')
        # ax1.plot(df['time'], df['EMA_10'], color='red', label='EMA_10')
        # ax1.plot(df['time'], df['senkou_span_a'], color='blue', label='senkou_span_a')
        # ax1.plot(df['time'], df['senkou_span_b'], color='red', label='senkou_span_b')
        # ax1.plot(df['time'], df['kijun_sen'], color='yellow', label='kijun_sen')
        # ax1.plot(df['time'], df['chikou_span'], color='brown', label='chikou_span')
        # ax1.plot(df['time'], df['tenkan_sen'], color='pink', label='tenkan_sen')
        # ax1.fill_between(df['time'], df['senkou_span_a'], df['senkou_span_b'], where=df['senkou_span_b'] >= df['senkou_span_a'],
        #                  facecolor='red', interpolate=True)
        # ax1.fill_between(df['time'], df['senkou_span_a'], df['senkou_span_b'], where=df['senkou_span_b'] <= df['senkou_span_a'],
        #                  facecolor='green', interpolate=True)
        ax1.plot(df['time'], df['EMA_12'], color='green', label='EMA_12')
        ax1.plot(df['time'], df['EMA_26'], color='blue', label='EMA_26')
        # ax1.plot(df['time'], df['SMA_200'], color='yellow', label='SMA_200')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
        plt.show()
