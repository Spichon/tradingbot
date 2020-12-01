from tradingbot.cotation import cotation_interface
from tradingbot.optimizer import optimizer_interface
from tradingbot.strategy import strategy_interface

import pandas as pd
import numpy as np


class asset_interface:
    def __init__(self, altname: str, base: str, quote: str, ordermin: float, lot_decimals: int,
                 cotation_place: cotation_interface, optimizer: optimizer_interface, strategies: [strategy_interface] = None):
        if strategies is None:
            strategies = []
        self.__altname = altname
        self.__base = base
        self.__quote = quote
        self.__ordermin = float(ordermin)
        self.__lot_decimals = int(lot_decimals)
        self.strategies = strategies
        self.__cotation_place = cotation_place
        self.__optimizer = optimizer

    def get_altname(self) -> str:
        """Get the tradable pair name"""
        return self.__altname

    def get_base(self) -> str:
        """Get base currency"""
        return self.__base

    def get_quote(self) -> str:
        """Get quote currency"""
        return self.__quote

    def get_ordermin(self) -> float:
        """Return the minimum quantity for an order that the asset can support"""
        return self.__ordermin

    def get_lot_decimals(self) -> int:
        """Return maximum decimals that an asset can handle"""
        return self.__lot_decimals

    def add_strategy(self, strategy: strategy_interface) -> []:
        """Add a strategy into the array of strategies"""
        return self.strategies.append(strategy)

    def remove_strategy(self, strategy: strategy_interface) -> []:
        """Remove a strategy of the array of strategies"""
        return self.strategies.remove(strategy)

    def get_OHLC(self, ticker: int) -> pd.DataFrame:
        """Return OHLC data for an asset"""
        ohlc = self.__cotation_place.get_ohlc(self.__altname, ticker)
        value_iterator = iter(ohlc)
        key = next(value_iterator)
        datas = ohlc[key]
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(datas, columns=columns)
        df = df.astype(float)
        df['time'] = pd.to_datetime(df['time'].astype(int), unit='s')
        df = df.set_index('time')
        df = df.fillna(method='ffill')
        return df[['open', 'high', 'low', 'close']]

    def get_last_value(self, ticker: int) -> float:
        """Return last value of the OHLC data"""
        return float(self.get_OHLC(ticker).tail(1)['close'].item())

    def calculate_strategies_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate the returns of each strategy given calculated position"""
        df = df.copy(deep=True)
        strategies = self.strategies
        for strategy in strategies:
            df = strategy.get_positions(df)
            df = strategy.get_strategy_return(df)
        df[[c for c in df if c.endswith('log_returns')]] = df[[c for c in df if c.endswith('log_returns')]].fillna(0)
        return df

    def get_weighted_position(self, strategies_return) -> [pd.Series, pd.Series]:
        """Weight the position of each stategy with a solver"""
        weights = self.__optimizer.optimize(strategies_return[[c for c in strategies_return if c.endswith('log_returns')]])
        names = ['{}_weights'.format(strategy.name) for strategy in self.strategies]
        weighted_position = strategies_return[[c for c in strategies_return if c.endswith('position')]].mul(
            weights).sum(1)
        return [weighted_position, pd.Series(weights, index=names)]

    def get_asset_return(self, df: pd.DataFrame) -> pd.DataFrame or None:
        """Return the asset_returns and its positions"""
        df = df.copy(deep=True)
        df = self.calculate_strategies_return(df)
        returns = self.get_weighted_position(df)
        positions = returns[0]
        if positions[-1] > 0:
            df['{}_position'.format(self.__base)] = positions
            df['{}_log_returns'.format(self.__base)] = np.log(df['close']).diff()
            df['{}_log_returns'.format(self.__base)] = df['{}_position'.format(self.__base)] * df[
                '{}_log_returns'.format(self.__base)]
            return df[['{}_log_returns'.format(self.__base), '{}_position'.format(self.__base)]]
