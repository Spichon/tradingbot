from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ema_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto
from tradingbot.portfolio import portfolio_manager
from tradingbot.optimizer import cplex_optimizer
from tradingbot.optimizer import markov_optimizer
from tradingbot.account import kraken_account_wrapper
import os
import pandas as pd
import numpy as np
os.environ['key'] = '++UMX5o2Y/wYNe6c5bh3RHkOhtsXQJgnWoKyKylfvLxH8EotobLKT5vP'
os.environ['secret'] = 'KObDBcajmeCLRGHmPUf4qhd0nO4yGd/B9ii47esXPIdsXKgyxTeHMmdxF/QpzMeNfbST4oPkJhAcPJc5e5ZpWQ=='
kraken_account = kraken_account_wrapper()
public_kraken = cotation_kraken()
m_optimizer = markov_optimizer('markov')
c_optimizer = cplex_optimizer('cplex')

my_portefolio = portfolio_manager(kraken_account, m_optimizer)

sma_strat = sma_strategy('SMA', 12, 24)
ema_strat = ema_strategy('EMA', 12, 24)
ichimo_strat = ichimoku_kinko_hyo_strategy('ICHIMO')

assets = public_kraken.get_available_assets()
for asset in assets:
    if (assets[asset]['quote']) == 'ZEUR':
        if (assets[asset]['altname']).endswith('.d') is False:
            temp_asset = asset_crypto(altname=assets[asset]['altname'],
                                      base=assets[asset]['base'],
                                      quote=assets[asset]['quote'],
                                      ordermin=assets[asset]['ordermin'],
                                      lot_decimals=assets[asset]['lot_decimals'],
                                      optimizer=c_optimizer,
                                      cotation_place=public_kraken)
            temp_asset.add_strategy(sma_strat)
            temp_asset.add_strategy(ema_strat)
            temp_asset.add_strategy(ichimo_strat)
            my_portefolio.add_asset(temp_asset)

wish = my_portefolio.get_wish_balance(60)
held = my_portefolio.get_held_balance()
state = pd.merge(wish, held, left_index=True, right_index=True, how="outer")
state['diff'] = np.subtract(wish, held)

for e in state['diff'].iteritems():
    asset = e[0]
    info = public_kraken.get_asset_info(asset)
    altname = info[asset]['altname']
    ordermin, max_dec = public_kraken.get_minimum_trade(altname + 'EUR')
    print(ordermin, max_dec)