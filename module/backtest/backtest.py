from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ema_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto

import pandas as pd
import pyfolio as pf
import matplotlib.pyplot as plt
import os

if __name__ == '__main__':
    public_kraken = cotation_kraken()
    sma_strat = sma_strategy('SMA', 12, 24)
    ema_strat = ema_strategy('EMA', 12, 24)
    ichimo_strat = ichimoku_kinko_hyo_strategy('ICHIMO')
    XETHZ = asset_crypto(asset='ETH', cotation_place=public_kraken)
    XETHZ.add_strategy(sma_strat)
    XETHZ.add_strategy(ema_strat)
    XETHZ.add_strategy(ichimo_strat)
    returns = XETHZ.get_asset_return(1440, optimize=True, rolling_optimization=False,
                                     from_directory=os.path.join(os.environ['PROJECT_PATH'], "backtesting"))
    pf.tears.create_full_tear_sheet(pd.Series(returns['ETH_log_returns']))
    plt.show()
