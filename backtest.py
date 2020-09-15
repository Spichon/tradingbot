import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.strategy import ema_strategy
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import os


if __name__ == '__main__':

    for file in os.listdir('backtesting'):
        df_initial = pd.read_csv('backtesting/'+ file)
        robot_ema = ema_strategy(df_initial, n1=12, n2=26)
        robot_ema.populate()
        robot_ema.get_signals()
        robot_ema.get_asset_return()
        df_ema = robot_ema.df
        df_initial['time'] = df_initial['time'].map(mdates.date2num)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))

        ax1.plot(df_initial['time'], df_ema['cum_strategy_asset_log_returns'], label='cum_ema_asset_log_returns', color='red')

        ax1.set_ylabel('Cumulative log-returns')
        ax1.legend(loc='best')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

        ax2.plot(df_initial['time'], 100 * df_ema['cum_strategy_asset_relative_returns'], label='cum_ema_asset_relative_returns', color='red')

        ax2.set_ylabel('Total relative returns (%)')
        ax2.legend(loc='best')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
        plt.xticks(rotation=45)
        plt.show()

    # fig, ax = plt.subplots(figsize=(16, 9))
    #
    # ax.plot(df['time'], 100 * df['cum_relative_return_exact'], label='Exact')
    # ax.plot(df['time'], 100 * df['cum_relative_return_approx'], label='Approximation')
    #
    # ax.set_ylabel('Total cumulative relative returns (%)')
    # ax.legend(loc='best')
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    #
    # plt.show()


    # budget = 100
    # position ='neutre'
    # qte = 0
    # for index, row in df.iterrows():
    #     if row['position'] == 1 and position != 'acheteuse':
    #         qte = budget / row['high']
    #         position = 'acheteuse'
    #         print('date : {} achat au cours de {}'.format(row['time'], (row['high']+ row['low'])/2))
    #     elif row['position'] == -1 or 0 and position != 'vendeuse':
    #         if qte > 0:
    #             print('date : {} vente au cours de {}'.format(row['time'], (row['high']+ row['low'])/2))
    #             budget = qte * row['high']
    #             position = 'vendeuse'
    #             qte = 0
    #             print(budget)
    # fig, ax = plt.subplots()
    # ax.plot(df['time'], df['stock_returns'].cumsum(), color='blue', label='stock_returns')
    # ax.plot(df['time'], df['strategy_returns'].cumsum(), color='red', label='strategy_returns')
    # ax.set(xlabel='time', ylabel='money',
    #        title='money vs time')
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M'))
    # plt.xticks(rotation=45)
    # plt.show()

