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

    def get_OHLC(self, ticker: int) -> pd.DataFrame:
        """Return OHLC data for an asset"""
        ohlc = self.__cotation_place.get_ohlc(self.__asset, ticker)
        datas = ohlc[self.__asset + 'EUR']
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(datas, columns=columns)
        df = df.astype(float)
        df['time'] = pd.to_datetime(df['time'].astype(int), unit='s')
        df = df.set_index('time')
        df = df.fillna(method='ffill')
        return df[['open', 'high', 'low', 'close']]

    def get_last_value(self, ticker: int) -> float:
        """Return OHLC data for an asset"""
        ohlc = self.__cotation_place.get_ohlc(self.__asset, ticker)
        datas = ohlc[self.__asset + 'EUR']
        value = float(list(datas)[-1][-4])
        return value


    def add_strategy(self, strategy: strategy_interface) -> []:
        """Add a strategy into the array of strategies"""
        return self.strategies.append(strategy)

    def remove_strategy(self, strategy: strategy_interface) -> []:
        """Remove a strategy of the array of strategies"""
        return self.strategies.remove(strategy)

    def calculate_strategies_return(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        strategies = self.strategies
        for strategy in strategies:
            df = strategy.get_positions(df)
            df = strategy.get_strategy_return(df)
        df[[c for c in df if c.endswith('log_returns')]] = df[[c for c in df if c.endswith('log_returns')]].fillna(0)
        return df

    def get_weights(self, strategies_return: pd.DataFrame):
        weights = self.__optimize(strategies_return)
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

    def get_weighted_mul(self, strategies_return):
        weights = self.get_weights(strategies_return[[c for c in strategies_return if c.endswith('log_returns')]])
        names = ['{}_weights'.format(strategy.name) for strategy in self.strategies]
        weighted_position = strategies_return[[c for c in strategies_return if c.endswith('position')]].mul(
            weights).sum(1)
        return [weighted_position, pd.Series(weights, index=names)]

    def __optimize(self, strategies_return: pd.DataFrame = None) -> []:
        no_of_strategies = strategies_return.shape[1]
        weights = cp.Variable(no_of_strategies)
        asset_return = (np.array(strategies_return) @ weights)
        final_asset_value = cp.sum(cp.log(1 + asset_return))
        objective = cp.Maximize(final_asset_value)
        constraints = [0.0 <= weights, cp.sum(weights) <= 1]
        problem = cp.Problem(objective, constraints)
        try:
            problem.solve()
        except SolverError:
            problem.solve(solver=SCS)
        return weights.value

    def get_asset_return(self, df: pd.DataFrame):
        df = df.copy(deep=True)
        df = self.calculate_strategies_return(df)
        # temp_df = self.roll(df, 720).apply(lambda x: self.get_weighted_mul(x))
        returns = self.get_weighted_mul(df)
        positions = returns[0]
        weights = returns[1]
        df['{}_position'.format(self.__asset)] = positions
        df['{}_log_returns'.format(self.__asset)] = np.log(df['close']).diff()
        df['{}_log_returns'.format(self.__asset)] = df['{}_position'.format(self.__asset)] * df[
            '{}_log_returns'.format(self.__asset)]
        return df[['{}_log_returns'.format(self.__asset), '{}_position'.format(self.__asset)]]
