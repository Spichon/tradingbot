import pandas as pd
from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.strategy import ema_strategy

from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto
from tradingbot.portfolio import portfolio_manager
from tradingbot.account import kraken_account_wrapper
import yaml
import matplotlib.pyplot as plt

if __name__ == '__main__':

    kraken_acount = kraken_account_wrapper()
    public_kraken = cotation_kraken()
    my_portefolio = portfolio_manager(kraken_acount)

    sma_strat = sma_strategy('SMA', 12, 24)
    ema_strat = ema_strategy('EMA', 12, 24)
    ichimo_strat = ichimoku_kinko_hyo_strategy('ICHIMO')

    with open(r'config.yml') as file:
        assets = yaml.load(file, Loader=yaml.FullLoader)['assets']
        for asset in assets:
            temp_asset = asset_crypto(asset=asset, cotation_place=public_kraken)
            temp_asset.get_OHLC(1440, from_directory="backtesting")
            temp_asset.add_strategy(sma_strat)
            temp_asset.add_strategy(ema_strat)
            temp_asset.add_strategy(ichimo_strat)
            my_portefolio.add_asset(temp_asset)
        df = my_portefolio.get_portfolio_return(1440, optimize=True, rolling_optimization=True,
                                              from_directory="backtesting")

        plt.show()
