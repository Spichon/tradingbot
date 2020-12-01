from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

from tradingbot.optimizer import cplex_optimizer
from tradingbot.optimizer import markov_optimizer
from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ema_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto
from tradingbot.portfolio import portfolio_manager
from tradingbot.account import kraken_account_wrapper
import numpy as np

sma_strat = sma_strategy('SMA', 12, 24)
ema_strat = ema_strategy('EMA', 12, 24)
ichimo_strat = ichimoku_kinko_hyo_strategy('ICHIMO')
kraken_account = kraken_account_wrapper()
public_kraken = cotation_kraken()
m_optimizer = markov_optimizer('markov')
c_optimizer = cplex_optimizer('cplex')

my_portefolio = portfolio_manager(kraken_account, m_optimizer)
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
scheduler = BlockingScheduler()
ticker = 60


def robot_trading():
    wish = my_portefolio.get_wish_balance(ticker)
    held = my_portefolio.get_held_balance()
    state = pd.merge(wish, held, left_index=True, right_index=True, how="outer")
    state['diff'] = np.subtract(state['wish_balance'], state['quantity_held'])
    for asset in my_portefolio.assets:
        base = asset.get_base()
        altname = asset.get_altname()
        sub_df = state.loc[base, :]
        qty = sub_df['diff']
        ordermin = asset.get_ordermin()
        lot_decimals = asset.get_lot_decimals()
        qty = round(qty, lot_decimals)
        if qty < 0 and -qty > ordermin:
            print("Sell asset : {}, qty : {}".format(altname, qty))
            result = kraken_account.add_order(pair=altname,
                                              type='sell',
                                              ordertype='market',
                                              volume=-qty)
            print(result)
        if qty > 0 and qty >= ordermin:
            print("Buy asset : {}, qty : {}".format(altname, qty))
            result = kraken_account.add_order(pair=altname,
                                              type='buy',
                                              ordertype='market',
                                              volume=qty)
            print(result)


scheduler.add_job(robot_trading, 'interval', seconds=60)

if __name__ == '__main__':
    scheduler.start()
