from pypfopt.exceptions import OptimizationError

from tradingbot.optimizer import optimizer_interface
import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

class markov_optimizer(optimizer_interface):
    def __init__(self, name):
        super().__init__(name)

    def optimize(self, df: pd.DataFrame = None) -> []:
        mu = expected_returns.mean_historical_return(df, returns_data=True)
        S = risk_models.sample_cov(df, returns_data=True)
        ef = EfficientFrontier(mu, S)
        raw_weights = ef.max_sharpe()
        ef.portfolio_performance(verbose=True)
        return raw_weights.values()