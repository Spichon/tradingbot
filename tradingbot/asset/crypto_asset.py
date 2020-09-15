import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib import style

class crypto_asset:
    def __init__(self, asset, ticker, k):
        self.asset = asset
        self.k = k
        self.ticker = ticker
        self.ohlc = self.get_OHLC(self.ticker)

    def get_asset(self):
        return self.asset

    def set_ticker(self, ticker):
        self.ticker = ticker

    def get_OHLC(self, ticker=None) -> pd.DataFrame:
        if ticker is None:
            ticker = self.ticker
        ohlc = self.k.query_public('OHLC', {'pair': self.asset + 'EUR', 'interval': ticker})['result']
        datas = ohlc[self.asset + 'EUR']
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(datas, columns=columns)
        df = df.astype(float)
        df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
        df['time'] = df['time'].dt.tz_convert('Europe/Paris')
        df['time'] = df['time'].dt.tz_localize(None)
        return df

    def draw_OHLC(self):
        style.use('ggplot')
        df = self.ohlc
        df['time'] = df['time'].map(mdates.date2num)
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        candlestick_ohlc(ax1, df.values, width=0.01, colorup='green',
                         colordown='red')
        ax2.bar(df['time'], df['volume'], 0.015, color='k')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
        plt.show()
