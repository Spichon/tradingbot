from cvxpy import SolverError, SCS

from tradingbot.cotation import cotation_interface
from tradingbot.strategy import strategy_interface
from numpy.lib.stride_tricks import as_strided as stride

import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
from mpl_finance import candlestick_ohlc
import cvxpy as cp
import pyfolio as pf


class asset_interface:
    def __init__(self, asset: str, cotation_place: cotation_interface, strategies: [strategy_interface] = None):
        if strategies is None:
            strategies = []
        self.__asset = asset
        self.strategies = strategies
        self.__cotation_place = cotation_place

    def get_asset(self) -> str:
        return self.__asset

    def get_OHLC(self, ticker: int, from_directory: str = None) -> pd.DataFrame:
        """Return OHLC data for an asset"""
        if from_directory is None:
            ohlc = self.__cotation_place.get_ohlc(self.__asset, ticker)
            datas = ohlc[self.__asset + 'EUR']
            columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
            df = pd.DataFrame(datas, columns=columns)
            df = df.astype(float)
            df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
            df['time'] = df['time'].dt.tz_convert('Europe/Paris')
            df['time'] = df['time'].dt.tz_localize(None)
            df = df.set_index('time')

        else:
            df = pd.read_csv('{}/{}.csv'.format(from_directory, self.__asset + 'EUR'), parse_dates=True,
                             names=["time", "price", "volume"])
            df['time'] = pd.to_datetime(df['time'].astype(int), unit='s')
            df = df.set_index('time')
            df = df.resample('{}Min'.format(ticker)).agg({'price': 'ohlc', 'volume': 'sum'})
            df = df.droplevel(0, axis=1)
        df = df.fillna(method='ffill')
        return df

    def add_strategy(self, strategy: strategy_interface) -> []:
        """Add a strategy into the array of strategies"""
        return self.strategies.append(strategy)

    def remove_strategy(self, strategy: strategy_interface) -> []:
        """Remove a strategy of the array of strategies"""
        return self.strategies.remove(strategy)

    def calculate_indicators(self, ticker: int, strategies: [strategy_interface] = None,
                             from_directory: str = None) -> pd.DataFrame:
        if strategies is None:
            strategies = self.strategies
        df = self.get_OHLC(ticker=ticker, from_directory=from_directory)
        for strategy in strategies:
            df = strategy.populate(df)
            df = strategy.get_signals(df)
        return df

    # def draw_OHLC(self, ticker: int):
    #     """Draw OHLC graph"""
    #     style.use('ggplot')
    #     df = self.get_OHLC(ticker)
    #     df['time'] = df['time'].map(mdates.date2num)
    #     ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
    #     ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    #     candlestick_ohlc(ax1, df.values, width=0.01, colorup='green',
    #                      colordown='red')
    #     ax2.bar(df['time'], df['volume'], 0.015, color='k')
    #     ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    #     plt.show()
    #     pass
    #
    # def draw_OHLC_with_strat_indicator(self, ticker: int, strategies: [strategy_interface] = None):
    #     if strategies is None:
    #         strategies = self.strategies
    #     style.use('ggplot')
    #     df = self.calculate_indicators(ticker)
    #     df['time'] = df['time'].map(mdates.date2num)
    #     ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
    #     ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
    #     candlestick_ohlc(ax1, df.values, width=0.01, colorup='green',
    #                      colordown='red')
    #     ax2.bar(df['time'], df['volume'], 0.015, color='k')
    #     ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    #     for strategy in strategies:
    #         strategy.draw_indicator(df=df, ax=ax1)
    #     plt.show()
    #     pass

    def get_weights(self, strategies_returns: pd.DataFrame, optimize: bool = True):
        if optimize:
            weights = self.__optimize(strategies_returns)
        else:
            weights = 1 / strategies_returns.shape[1]
        return weights

    def roll(self, df, w, **kwargs):
        v = df.values
        d0, d1 = v.shape
        s0, s1 = v.strides

        try:
            a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))
        except ValueError:
            a = stride(v, (d0, w, d1), (s0, s0, s1))
        rolled_df = pd.concat({
            row: pd.DataFrame(values, columns=df.columns)
            for row, values in zip(df.index, a)
        })
        return rolled_df.groupby(level=0, **kwargs)

    def get_weighted_mul(self, sub_df, optimize, strategies):
        weights = self.get_weights(sub_df[[c for c in sub_df if c.endswith('log_returns')]].fillna(0), optimize)
        names = []
        for strategy in strategies:
            names.append('{}_weights'.format(strategy.name))
        papa = sub_df[[c for c in sub_df if c.endswith('position')]].mul(weights).sum(1)
        return pd.concat(
            [pd.Series(weights, index=names), pd.Series(0 if papa.iloc[-1] < 0 else 1, index=['position'])], axis=0)

    def get_asset_return(self, ticker: int, strategies: [strategy_interface] = None, optimize: bool = True,
                         rolling_optimization: bool = True,
                         from_directory: str = None):
        if strategies is None:
            strategies = self.strategies
        df = self.calculate_indicators(ticker, strategies, from_directory)
        for strategy in strategies:
            df = strategy.get_strategy_return(df)
        print("Crypto {} en cours d'optimisation".format(self.get_asset()))
        if rolling_optimization:
            temp_df = self.roll(df, 720).apply(lambda x: self.get_weighted_mul(x, optimize, strategies))
            df = df.join(temp_df)
            df['position'] = df['position'].shift(periods=720)
            df[[c for c in df if c.endswith('weights')]] = df[[c for c in df if c.endswith('weights')]].shift(
                periods=720)
        else:
            weights = self.get_weights(df[[c for c in df if c.endswith('log_returns')]].fillna(0), optimize)
            df['position'] = df[[c for c in df if c.endswith('position')]].mul(weights).sum(1)
            df.loc[df.position < 0, "position"] = -1
            df.loc[df.position > 0, "position"] = 1
        df['{}_returns'.format(self.__asset)] = df['close'].diff()
        df['{}_returns'.format(self.__asset)] = df['position'] * df[
            '{}_returns'.format(self.__asset)]
        df['{}_log_returns'.format(self.__asset)] = np.log(df['close']).diff()
        df['{}_log_returns'.format(self.__asset)] = df['position'] * df[
            '{}_log_returns'.format(self.__asset)]
        df['{}_log_returns'.format(self.__asset)] = df['{}_log_returns'.format(self.__asset)].fillna(0)
        return df['{}_log_returns'.format(self.__asset)]

    def __optimize(self, strategies_returns: pd.DataFrame = None) -> []:
        no_of_strategies = strategies_returns.shape[1]
        weights = cp.Variable(no_of_strategies)
        asset_return = (np.array(strategies_returns) @ weights)
        final_asset_value = cp.sum(cp.log(1 + asset_return))
        objective = cp.Maximize(final_asset_value)
        constraints = [0.0 <= weights, cp.sum(weights) <= 1]
        problem = cp.Problem(objective, constraints)
        try:
            problem.solve()
        except SolverError:
            problem.solve(solver=SCS)
        return weights.value

    def create_asset_report(self, ticker: int, strategies: [strategy_interface] = None,
                            optimize: bool = True, rolling_optimization: bool = False, from_directory: str = None, df: pd.DataFrame = None):
        if df is None:
            if strategies is None:
                strategies = self.strategies
            asset_total_return = self.get_asset_return(ticker, strategies, optimize, rolling_optimization, from_directory)
        else:
            asset_total_return = df
        pf.tears.create_full_tear_sheet(pd.Series(asset_total_return))
