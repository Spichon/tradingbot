import pandas as pd
import numpy as np
from cvxpy import SolverError, SCS
import cvxpy as cp
from tradingbot.optimizer import optimizer_interface


class cplex_optimizer(optimizer_interface):
    def __init__(self, name):
        super().__init__(name)

    def optimize(self, df: pd.DataFrame = None) -> []:
        shape = df.shape[1]
        weights = cp.Variable(shape)
        returns = (np.array(df) @ weights)
        final_return = cp.sum(cp.log(1 + returns))
        objective = cp.Maximize(final_return)
        constraints = [0 <= weights, cp.sum(weights) <= 1]
        problem = cp.Problem(objective, constraints)
        try:
            problem.solve()
        except SolverError:
            problem.solve(solver=SCS)
        return weights.value