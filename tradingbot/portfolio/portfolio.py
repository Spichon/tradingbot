from functools import reduce
from cvxpy import SolverError, SCS
import pandas as pd
import numpy as np
import cvxpy as cp
from numpy.lib.stride_tricks import as_strided as stride

from tradingbot.account import account_interface
from tradingbot.asset import asset_interface


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

    def get_account_balances(self):
        return self.__account.get_balances()

    def get_trade_balances(self, currency="ZEUR"):
        return self.__account.get_trade_balance(currency)

    def get_asset_balance(self, asset):
        balances = self.__account.get_balances()
        return float(balances[asset])

    def get_held_balance(self):
        assets = pd.DataFrame(index=[o.get_asset() for o in self.assets])
        balances = pd.DataFrame.from_dict(data=self.get_account_balances(), columns=["quantity_held"],
                                          orient='index').astype(float)
        dfs = pd.merge(assets, balances, left_index=True, right_index=True, how="left")
        dfs = dfs.fillna(0)
        return dfs

    def get_wish_balance(self, ticker):
        assets_returns = self.get_assets_return(ticker)
        wish_percent = self.get_percent_wish(assets_returns)
        last_values = self.get_assets_last_value()
        trade_balance = self.get_trade_balances()
        balance = float(trade_balance['eb']) - 5
        wish_balance = wish_percent.mul(balance)['percent_wish']/last_values['last_value']
        wish_balance = pd.DataFrame(wish_balance, columns=["wish_balance"])
        return wish_balance

    def get_assets_last_value(self, ticker=1):
        dfs = []
        for asset in self.assets:
            temp_asset = pd.DataFrame(index=[asset.get_asset()], columns=['last_value'],
                                      data=asset.get_last_value(ticker))
            dfs.append(temp_asset)
        return pd.concat(dfs)

    def get_open_orders(self):
        assets = pd.DataFrame(index=[o.get_asset() for o in self.assets], columns=['open_orders'])
        orders = self.__account.get_open_orders()
        for asset in assets.index:
            if asset in str(orders):
                assets.loc[asset] = True
            else:
                assets.loc[asset] = False
        return assets

    def reset_orders(self):
        orders = self.__account.get_open_orders()
        for order in orders.keys():
            self.__account.cancel_order(order)

    def get_equivalent_balance(self):
        balances = self.__account.get_balances()
        return float(balances['ZEUR'])

    def get_weights(self, assets_return: pd.DataFrame):
        weights = self.__optimize(assets_return)
        return weights

    def get_assets_return(self, ticker: int) -> pd.DataFrame:
        dfs = []
        for asset in self.assets:
            asset_OHLC = asset.get_OHLC(ticker)
            asset_return = asset.get_asset_return(asset_OHLC)
            dfs.append(asset_return)
        dfs = reduce(lambda df1, df2: pd.merge(df1, df2, left_index=True, right_index=True), dfs)
        dfs[[c for c in dfs if c.endswith('log_returns')]] = dfs[[c for c in dfs if c.endswith('log_returns')]].fillna(
            0)
        return dfs

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

    def get_percent_wish(self, assets_return):
        weights = self.get_weights(assets_return[[c for c in assets_return if c.endswith('log_returns')]])
        weights = weights
        names = [asset.get_asset() for asset in self.assets]
        return pd.DataFrame(weights, index=names, columns=['percent_wish'])

    def get_percent_held(self):
        portfolio_balances = self.get_held_balance()
        last_values = self.get_assets_last_value()
        trade_balance = self.get_trade_balances()
        dfs = pd.merge(portfolio_balances, last_values, left_index=True, right_index=True, how='outer')
        dfs['hold*price'] = dfs['quantity_held'] * dfs['last_value']
        balance = float(trade_balance['eb']) - 5
        dfs['percent_held'] = (dfs['hold*price'] / balance)
        return dfs['percent_held']

    def get_portfolio_return(self, ticker: int) -> pd.DataFrame:
        assets_return = self.get_assets_return(ticker)
        # temp_df = self.roll(assets_returns, 720).apply(lambda x: self.get_percent_wish(x, optimize, assets))
        weights = self.get_percent_wish(assets_return)
        weights = weights.values.reshape((1, -1))
        assets_return['portfolio_return'] = assets_return[[c for c in assets_return if c.endswith('log_returns')]].mul(
            weights).sum(1)
        return assets_return

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
