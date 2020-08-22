import numpy as np
import matplotlib.pyplot as plt
from cvxpy import *
import pandas as pd

np.random.seed(123)

# Turn off progress printing

'''
What do we need for optimization?
- Goal: Maximize or Minimize
- Objective Function: Markowitz's Efficiency Frontier
- Constraints:  - Sum of all weights equal to one, 
                - Maximum allocation to a stock or industry or sector or asset class is x %, ...
- 
'''

# TODO For now equal allocation
def optimal_portfolio(returns: pd.Series, longs: [], shorts: [], risk_measure):
    output = pd.Series()
    for ticker, stock_return in returns.iteritems():
        output[ticker] = 1 / len(returns)
    return output

