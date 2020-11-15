from tradingbot.strategy import strategy_interface

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ichimoku_kinko_hyo_strategy(strategy_interface):
    def __init__(self, name):
        super().__init__(name)

    def get_positions(self, df: pd.DataFrame) -> pd.DataFrame:
        temp_df = df.copy(deep=True)
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        nine_period_high = temp_df['high'].rolling(window=9).max()
        nine_period_low = temp_df['low'].rolling(window=9).min()
        temp_df['tenkan_sen'] = (nine_period_high + nine_period_low) / 2
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = temp_df['high'].rolling(window=26).max()
        period26_low = temp_df['low'].rolling(window=26).min()
        temp_df['kijun_sen'] = (period26_high + period26_low) / 2
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        temp_df['senkou_span_a'] = ((temp_df['tenkan_sen'] + temp_df['kijun_sen']) / 2).shift(26)
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = temp_df['high'].rolling(window=52).max()
        period52_low = temp_df['low'].rolling(window=52).min()
        temp_df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(52)
        # The most current closing price plotted 26 time periods behind (optional)
        temp_df['chikou_span'] = temp_df['close'].shift(-26)
        temp_df['above_cloud'] = 0
        temp_df['above_cloud'] = np.where((temp_df['low'] > temp_df['senkou_span_a']) & (temp_df['low'] > temp_df['senkou_span_b']), 1,
                                     temp_df['above_cloud'])
        temp_df['above_cloud'] = np.where((temp_df['high'] < temp_df['senkou_span_a']) & (temp_df['high'] < temp_df['senkou_span_b']), -1,
                                     temp_df['above_cloud'])
        temp_df['A_above_B'] = np.where((temp_df['senkou_span_a'] > temp_df['senkou_span_b']), 1, -1)
        temp_df['tenkan_kiju_cross'] = np.NaN
        temp_df['tenkan_kiju_cross'] = np.where(
            (temp_df['tenkan_sen'].shift(1) <= temp_df['kijun_sen'].shift(1)) & (temp_df['tenkan_sen'] > temp_df['kijun_sen']), 1,
            temp_df['tenkan_kiju_cross'])
        temp_df['tenkan_kiju_cross'] = np.where(
            (temp_df['tenkan_sen'].shift(1) >= temp_df['kijun_sen'].shift(1)) & (temp_df['tenkan_sen'] < temp_df['kijun_sen']), -1,
            temp_df['tenkan_kiju_cross'])
        temp_df['price_tenkan_cross'] = np.NaN
        temp_df['price_tenkan_cross'] = np.where(
            (temp_df['open'].shift(1) <= temp_df['tenkan_sen'].shift(1)) & (temp_df['open'] > temp_df['tenkan_sen']), 1,
            temp_df['price_tenkan_cross'])
        temp_df['price_tenkan_cross'] = np.where(
            (temp_df['open'].shift(1) >= temp_df['tenkan_sen'].shift(1)) & (temp_df['open'] < temp_df['tenkan_sen']), -1,
            temp_df['price_tenkan_cross'])
        temp_df['buy'] = np.NaN
        temp_df['buy'] = np.where((temp_df['above_cloud'].shift(1) == 1) & (temp_df['A_above_B'].shift(1) == 1) & (
                (temp_df['tenkan_kiju_cross'].shift(1) == 1) | (temp_df['price_tenkan_cross'].shift(1) == 1)), 1, temp_df['buy'])
        temp_df['buy'] = np.where(temp_df['tenkan_kiju_cross'].shift(1) == -1, 0, temp_df['buy'])
        temp_df['buy'].ffill(inplace=True)
        temp_df['sell'] = np.NaN
        temp_df['sell'] = np.where((temp_df['above_cloud'].shift(1) == -1) & (temp_df['A_above_B'].shift(1) == -1) & (
                (temp_df['tenkan_kiju_cross'].shift(1) == -1) | (temp_df['price_tenkan_cross'].shift(1) == -1)), -1,
                              temp_df['sell'])
        temp_df['sell'] = np.where(temp_df['tenkan_kiju_cross'].shift(1) == 1, 0, temp_df['sell'])
        temp_df['sell'].ffill(inplace=True)
        df['{}_position'.format(self.name)] = temp_df['buy'] + temp_df['sell']
        return df
