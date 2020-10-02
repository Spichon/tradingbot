from tradingbot.strategy import strategy_interface

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ichimoku_kinko_hyo_strategy(strategy_interface):
    def __init__(self, name):
        super().__init__(name)

    def populate(self, df: pd.DataFrame) -> pd.DataFrame:
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        nine_period_high = df['high'].rolling(window=9).max()
        nine_period_low = df['low'].rolling(window=9).min()
        df['tenkan_sen'] = (nine_period_high + nine_period_low) / 2
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = df['high'].rolling(window=26).max()
        period26_low = df['low'].rolling(window=26).min()
        df['kijun_sen'] = (period26_high + period26_low) / 2
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = df['high'].rolling(window=52).max()
        period52_low = df['low'].rolling(window=52).min()
        df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(52)
        # The most current closing price plotted 26 time periods behind (optional)
        df['chikou_span'] = df['close'].shift(-26)
        return df

    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df['above_cloud'] = 0
        df['above_cloud'] = np.where((df['low'] > df['senkou_span_a']) & (df['low'] > df['senkou_span_b']), 1,
                                     df['above_cloud'])
        df['above_cloud'] = np.where((df['high'] < df['senkou_span_a']) & (df['high'] < df['senkou_span_b']), -1,
                                     df['above_cloud'])
        df['A_above_B'] = np.where((df['senkou_span_a'] > df['senkou_span_b']), 1, -1)
        df['tenkan_kiju_cross'] = np.NaN
        df['tenkan_kiju_cross'] = np.where(
            (df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1)) & (df['tenkan_sen'] > df['kijun_sen']), 1,
            df['tenkan_kiju_cross'])
        df['tenkan_kiju_cross'] = np.where(
            (df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1)) & (df['tenkan_sen'] < df['kijun_sen']), -1,
            df['tenkan_kiju_cross'])
        df['price_tenkan_cross'] = np.NaN
        df['price_tenkan_cross'] = np.where(
            (df['open'].shift(1) <= df['tenkan_sen'].shift(1)) & (df['open'] > df['tenkan_sen']), 1,
            df['price_tenkan_cross'])
        df['price_tenkan_cross'] = np.where(
            (df['open'].shift(1) >= df['tenkan_sen'].shift(1)) & (df['open'] < df['tenkan_sen']), -1,
            df['price_tenkan_cross'])
        df['buy'] = np.NaN
        df['buy'] = np.where((df['above_cloud'].shift(1) == 1) & (df['A_above_B'].shift(1) == 1) & (
                (df['tenkan_kiju_cross'].shift(1) == 1) | (df['price_tenkan_cross'].shift(1) == 1)), 1, df['buy'])
        df['buy'] = np.where(df['tenkan_kiju_cross'].shift(1) == -1, 0, df['buy'])
        df['buy'].ffill(inplace=True)
        df['sell'] = np.NaN
        df['sell'] = np.where((df['above_cloud'].shift(1) == -1) & (df['A_above_B'].shift(1) == -1) & (
                (df['tenkan_kiju_cross'].shift(1) == -1) | (df['price_tenkan_cross'].shift(1) == -1)), -1,
                              df['sell'])
        df['sell'] = np.where(df['tenkan_kiju_cross'].shift(1) == 1, 0, df['sell'])
        df['sell'].ffill(inplace=True)
        df['{}_position'.format(self.name)] = df['buy'] + df['sell']
        return df

    def get_signal(self, df: pd.DataFrame) -> int:
        return int(df['{}_position'.format(self.name)].tail(1).values[0])

    def draw_indicator(self, df: pd.DataFrame, ax: plt.subplot2grid):
        ax.plot(df['time'], df['senkou_span_a'], color='blue', label='senkou_span_a')
        ax.plot(df['time'], df['senkou_span_b'], color='red', label='senkou_span_b')
        ax.plot(df['time'], df['kijun_sen'], color='yellow', label='kijun_sen')
        ax.plot(df['time'], df['chikou_span'], color='brown', label='chikou_span')
        ax.plot(df['time'], df['tenkan_sen'], color='pink', label='tenkan_sen')
        ax.fill_between(df['time'], df['senkou_span_a'], df['senkou_span_b'],
                        where=df['senkou_span_b'] >= df['senkou_span_a'],
                        facecolor='red', interpolate=True)
        ax.fill_between(df['time'], df['senkou_span_a'], df['senkou_span_b'],
                        where=df['senkou_span_b'] <= df['senkou_span_a'],
                        facecolor='green', interpolate=True)
