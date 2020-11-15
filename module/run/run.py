from datetime import datetime
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd
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
my_portefolio = portfolio_manager(kraken_account)
with open(r'{}/{}.yml'.format("/Users/simon.a.pichon/Project/tradingbot", 'config')) as stream:
    try:
        data = yaml.load(stream, Loader=yaml.FullLoader)
        for asset in data['assets']:
            initialized_asset = asset_crypto(asset=asset, cotation_place=public_kraken)
            initialized_asset.add_strategy(sma_strat)
            initialized_asset.add_strategy(ema_strat)
            initialized_asset.add_strategy(ichimo_strat)
            my_portefolio.add_asset(initialized_asset)
    except yaml.YAMLError as exc:
        print(exc)
scheduler = BlockingScheduler()
ticker = 240


def robot_trading():
    log_file = open("/Users/simon.a.pichon/Project/tradingbot/log.txt", "a")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    orders = kraken_account.get_open_orders()
    log_file.write('current_time: {}'.format(current_time))
    wish = my_portefolio.get_wish_balance(ticker)
    held = my_portefolio.get_held_balance()
    state = pd.merge(wish, held, left_index=True, right_index=True, how="outer")
    state['diff'] = np.subtract(wish, held)
    my_portefolio.reset_orders()
    state = state.join(orders)
    for e in state['diff'].iteritems():
        asset = e[0]
        qty = e[1]
        ordermin, max_dec = public_kraken.get_minimum_trade(asset + 'EUR')
        ordermin = float(ordermin)
        qty = round(qty, max_dec)
        if qty < 0 and -qty > ordermin:
            print("Sell asset : {}, qty : {}".format(asset, qty))
            result = kraken_account.add_order(pair=asset + 'EUR',
                                              type='sell',
                                              ordertype='market',
                                              volume=-qty)
            print(result)
        if qty > 0 and qty >= ordermin:
            print("Buy asset : {}, qty : {}".format(asset, qty))
            result = kraken_account.add_order(pair=asset + 'EUR',
                                              type='buy',
                                              ordertype='market',
                                              volume=qty)
            print(result)
    log_file.close()


scheduler.add_job(robot_trading, 'interval', seconds=10)

if __name__ == '__main__':
    scheduler.start()
