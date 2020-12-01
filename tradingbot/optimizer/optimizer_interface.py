import pandas as pd

class optimizer_interface:
    def __init__(self, name: str):
        self.name = name

    def optimize(self, df: pd.DataFrame = None) -> []:
        """Return weights as Array to optimize returns"""
        pass