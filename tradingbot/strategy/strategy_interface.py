import pandas as pd
import numpy as np


class strategy_interface:
    def __init__(self, name: str):
        self.name = name

    def get_positions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate bullish or bearish signals"""
        pass

    def get_strategy_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate the asset log return"""
        df['{}_log_returns'.format(self.name)] = np.log(df['close']).diff()
        df['{}_log_returns'.format(self.name)] = df['{}_position'.format(self.name)] * df[
            '{}_log_returns'.format(self.name)]
        return df