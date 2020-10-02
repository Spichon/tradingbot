import pandas as pd
import numpy as np

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import style


class strategy_interface:
    def __init__(self, name: str):
        self.name = name

    def populate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add indicator columns"""
        pass

    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate bullish or bearish signals"""
        pass

    def get_signal(self, df: pd.DataFrame) -> int:
        """Get buy or sell signal relative to a strategy"""
        pass

    def get_strategy_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate the asset log return and the cumulative log return of a strategy"""
        df['{}_log_returns'.format(self.name)] = np.log(df['close']).diff()
        df['{}_log_returns'.format(self.name)] = df['{}_position'.format(self.name)] * df[
            '{}_log_returns'.format(self.name)]
        # df['cum_{}_log_returns'.format(self.name)] = df['{}_log_returns'.format(self.name)].cumsum()
        # df['cum_{}_relative_returns'.format(self.name)] = np.exp(
        #     df['cum_{}_log_returns'.format(self.name)]) - 1
        return df

    """
        It works, but useless since you have to call the function 
        asset.draw_asset_return(60, ['MY_STRAT']) if you want to g
        et the asset return given only one strat
        """
    # def draw_strat_return(self, df: pd.DataFrame):
    #     style.use('ggplot')
    #     df['time'] = df['time'].map(mdates.date2num)
    #     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))
    #     ax1.plot(df['time'], df['cum_{}_log_returns'.format(self.name)],
    #              label='cum_{}_log_returns'.format(self.name),
    #              color='red')
    #     ax1.set_ylabel('Cumulative log-returns')
    #     ax1.legend(loc='best')
    #     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    #     ax2.plot(df['time'], 100 * df['cum_{}_relative_returns'.format(self.name)],
    #              label='cum_{}_relative_returns'.format(self.name), color='red')
    #     ax2.set_ylabel('Total relative returns (%)')
    #     ax2.legend(loc='best')
    #     ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    #     plt.xticks(rotation=45)
    #     plt.show()
