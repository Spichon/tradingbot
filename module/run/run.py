from datetime import datetime

from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ema_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto
from tradingbot.portfolio import portfolio_manager
from tradingbot.account import kraken_account_wrapper
import matplotlib.pyplot as plt
import yaml
import pyfolio as pf
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

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
ticker = 60

def robot_trading():
    log_file = open("log.txt", "a")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    orders = kraken_account.get_open_orders()
    balances = kraken_account.get_balances()
    assets_returns = my_portefolio.get_assets_return(ticker)
    print(assets_returns)
    # weights = my_portefolio.get_weights(assets_returns.fillna(0))
    # print(weights)
    # weights = pd.DataFrame(weights.reshape(1, -1), columns=[col.split('_')[0] for col in assets_returns.columns])
    # weights = weights.T
    # print(weights)

    # relevant_asset = crypto_asset(asset=asset, ticker=ticker, k=kraken_account.get_api())
    # df = relevant_asset.get_OHLC()
    # strategy = ema_strategy(name='ema_strategy', df=df, n1=12, n2=26)
    # strategy.populate()
    # signal = strategy.get_signal()
    # if signal == 1:
    #     log_file.write('{} - {} : Bullish signal from strategy {},\n'.format(
    #         current_time,
    #         asset,
    #         strategy.name))
    #     if (asset + 'EUR' in str(orders)) is False:
    #         log_file.write('{} - {} : The asset is not present in any order,\n'.format(
    #             current_time,
    #             asset))
    #         if ((asset in str(balances)) is False) or (float(balances[asset]) == 0):
    #             log_file.write('{} - {} : The asset is not yet owned,\n'.format(
    #                 current_time,
    #                 asset))
    #             available = float(balances['ZEUR']) * 0.30
    #             ordermin, max_dec = kraken_account.get_minimum_trade(asset + 'EUR')
    #             qte = round(available / df['close'].iloc[-1], max_dec)
    #             if qte >= ordermin:
    #                 result = kraken_account.add_order(pair=asset + 'EUR',
    #                                                   type='buy',
    #                                                   ordertype='market',
    #                                                   volume=qte)
    #                 if result['error'] == []:
    #                     log_file.write('{} - {} : Asset purchase successful : {},\n'.format(
    #                         current_time,
    #                         asset,
    #                         result['result']))
    #                 else:
    #                     log_file.write('{} - {} : Asset purchase failure : {},\n'.format(
    #                         current_time,
    #                         asset,
    #                         result['error']))
    #
    #             else:
    #                 log_file.write(
    #                     '{} - {} : Asset purchase failure : Not enough volume : miss {},\n'.format(
    #                         current_time,
    #                         asset,
    #                         ordermin - qte))
    #         else:
    #             log_file.write('{} - {} : The asset is already owned,\n'.format(
    #                 current_time,
    #                 asset))
    #
    # if signal == -1:
    #     log_file.write('{} - {} : Bearish signal from strategy {},\n'.format(
    #         current_time,
    #         asset,
    #         strategy.name))
    #     if (asset + 'EUR' in str(orders)) is False:
    #         log_file.write('{} - {} : The asset is not present in any order,\n'.format(
    #             current_time,
    #             asset))
    #         if (asset in str(balances)) and (float(balances[asset]) > 0):
    #             log_file.write('{} - {} : The asset is owned so can be sold,\n'.format(
    #                 current_time,
    #                 asset))
    #             result = kraken_account.add_order(pair=asset + 'EUR',
    #                                               type='sell',
    #                                               ordertype='market',
    #                                               volume=balances[asset]
    #                                               )
    #             if result['error'] == []:
    #                 log_file.write('{} - {} : Asset sell successful : {},\n'.format(
    #                     current_time,
    #                     asset,
    #                     result['result']))
    #             else:
    #                 log_file.write('{} - {} : Asset sell failure : {},\n'.format(
    #                     current_time,
    #                     asset,
    #                     result['error']))
    #
    #         else:
    #             log_file.write('{} - {} : The asset is not owned so cannot be sold,\n'.format(
    #                 current_time,
    #                 asset))
    log_file.close()

scheduler.add_job(robot_trading, 'interval', seconds=ticker)

if __name__ == '__main__':
    scheduler.start()

