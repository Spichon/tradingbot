from cvxpy import SolverError, SCS

from tradingbot.account import account_interface
from tradingbot.asset import asset_interface
# from tradingbot.position import position_wrapper
import pandas as pd
import pandas as pd
import numpy as np
import datetime
import math
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
import cvxopt as opt
from cvxopt import blas, solvers
import cvxpy as cp
import pyfolio as pf

from tradingbot.strategy import strategy_interface

from numpy.lib.stride_tricks import as_strided as stride


class portfolio_manager:
    def __init__(self, account: account_interface, assets: [asset_interface] = None):
        if assets is None:
            assets = []
        self.__account = account
        self.positions = []
        self.assets = assets

    def get_account(self):
        return self.__account

    def add_asset(self, asset: asset_interface) -> []:
        """Add an asset into the array of assets"""
        return self.assets.append(asset)

    def remove_asset(self, asset: asset_interface) -> []:
        """Remove an asset of the array of assets"""
        return self.assets.remove(asset)

    def get_balances(self):
        return self.__account.get_balances()

    def get_asset_balance(self, asset):
        balances = self.__account.get_balances()
        return float(balances[asset])

    def get_asset_value(self, asset, ticker=1):
        balances = self.__account.get_balances()
        amount = float(balances[asset])
        ohlc = self.__account.get_ohlc(asset=asset, ticker=ticker)
        datas = ohlc[asset + 'EUR']
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(datas, columns=columns)
        df = df.astype(float)
        value = df.tail(1)['open']
        return amount * value

    def get_open_orders(self):
        return self.__account.get_open_orders()

    def get_available_fund(self):
        balances = self.__account.get_balances()
        return float(balances['ZEUR'])

    def get_weights(self, assets_returns: pd.DataFrame, optimize: bool = True):
        if optimize:
            weights = self.__optimize(assets_returns)
        else:
            weights = 1 / assets_returns.shape[1]
        return weights

    def get_assets_return(self, ticker: int, assets: [asset_interface] = None, strategies: [strategy_interface] = None,
                          asset_optimization: bool = True,
                          rolling_optimization: bool = True,
                          from_directory: str = None) -> pd.DataFrame:
        if assets is None:
            assets = self.assets
        dfs = []
        for asset in assets:
            dfs.append(
                asset.get_asset_return(ticker, strategies, asset_optimization, rolling_optimization, from_directory))
        assets_returns = pd.concat(dfs, axis=1)
        assets_returns = assets_returns.fillna(0)
        return assets_returns

    def roll(self, df, w, **kwargs):
        v = df.values
        d0, d1 = v.shape
        s0, s1 = v.strides

        a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))
        rolled_df = pd.concat({
            row: pd.DataFrame(values, columns=df.columns)
            for row, values in zip(df.index, a)
        })
        return rolled_df.groupby(level=0, **kwargs)

    def get_weighted_mul(self, sub_df, optimize, assets):
        weights = self.get_weights(sub_df.fillna(0), optimize)
        names = []
        for asset in assets:
            names.append('{}_weights'.format(asset.get_asset()))
        papa = sub_df.mul(weights).sum(1)
        return pd.concat(
            [pd.Series(weights, index=names), pd.Series(papa.iloc[-1], index=['portfolio_return'])], axis=0)

    def get_portfolio_return(self, ticker: int, assets: [asset_interface] = None,
                             strategies: [strategy_interface] = None,
                             optimize: bool = True,
                             rolling_optimization: bool = True,
                             from_directory: str = None) -> pd.DataFrame:
        if assets is None:
            assets = self.assets
        dfs = []
        for asset in assets:
            dfs.append(
                asset.get_asset_return(ticker, strategies, optimize, rolling_optimization, from_directory))
        assets_returns = self.get_assets_return(ticker, assets, strategies, optimize, rolling_optimization, from_directory)
        if rolling_optimization:
            temp_df = self.roll(assets_returns, 720).apply(lambda x: self.get_weighted_mul(x, optimize, assets))
            assets_returns = assets_returns.join(temp_df)
            assets_returns['portfolio_return'] = assets_returns['portfolio_return'].shift(periods=720)
            assets_returns[[c for c in assets_returns if c.endswith('weights')]] = assets_returns[
                [c for c in assets_returns if c.endswith('weights')]].shift(
                periods=720)
        else:
            weights = self.get_weights(assets_returns.fillna(0), optimize)
            assets_returns['portfolio_return'] = np.sum(weights * assets_returns, axis=1)
        return assets_returns

    def __optimize(self, assets_returns: pd.DataFrame = None) -> []:
        no_of_stocks = assets_returns.shape[1]
        weights = cp.Variable(no_of_stocks)
        portfolio_returns = (np.array(assets_returns) @ weights)
        final_portfolio_value = cp.sum(cp.log(1 + portfolio_returns))
        objective = cp.Maximize(final_portfolio_value)
        constraints = [0.0 <= weights, cp.sum(weights) <= 1]
        problem = cp.Problem(objective, constraints)
        try:
            problem.solve()
        except SolverError:
            problem.solve(solver=SCS)
        return weights.value

    def create_portfolio_report(self, ticker: int, assets: [asset_interface] = None,
                                strategies: [strategy_interface] = None,
                                optimize: bool = True,
                                rolling_optimization: bool = True,
                                from_directory: str = None) -> None:
        portefolio_return = self.get_portfolio_return(ticker, assets, strategies, optimize, rolling_optimization,
                                                      from_directory)['portfolio_return']
        pf.tears.create_full_tear_sheet(pd.Series(portefolio_return))
