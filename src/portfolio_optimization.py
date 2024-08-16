import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize

"""
import importlib
imported_module = importlib.import_module("portfolio_optimization")
importlib.reload(imported_module)
from portfolio_optimization import *
"""
# Define the function for downloading the data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data


from scipy.optimize import minimize
import numpy as np
import pandas as pd

annualized_factor_from_freq = {"daily": 252, "monthly": 12, "quarterly": 4, "yearly": 1}


def get_valid_assets(returns):
    # Remove columns where all values are NaN
    non_nan_assets = returns.dropna(axis=1, how='all')
    
    # Remove columns where all remaining values are 0
    cleaned_ret = non_nan_assets.loc[:, (non_nan_assets != 0).any()]
    
    # Return list of valid asset names
    return list(cleaned_ret.columns)
    
def equal_contribution_weights(returns):
    assets = get_valid_assets(returns=returns)
    num_assets = len(assets)
    
    # Create a Series with equal weights for valid assets only
    weights = pd.Series(1. / num_assets, index=assets)
    
    # Ensure that all columns are represented, including non-valid assets with weight 0
    full_weights = pd.Series(0., index=returns.columns)
    full_weights[assets] = weights
    
    return full_weights

def annualized_expected_return(returns, frequency="daily"):
    assert frequency in annualized_factor_from_freq
    annual_factor = annualized_factor_from_freq[frequency]
    ann_return = (1 + returns.mean()) ** annual_factor - 1
    return ann_return

def annualized_volatility(returns, frequency="daily"):
    assert frequency in annualized_factor_from_freq
    annual_factor = annualized_factor_from_freq[frequency]
    ann_vol = returns.std() * np.sqrt(annual_factor)
    return ann_vol

def portfolio_return_from_weights(weights, mean_returns):
    return np.dot(weights, mean_returns)

def calculate_covariance_matrix(returns_df: pd.DataFrame, end_date: pd.Timestamp) -> pd.DataFrame:
    return returns_df.loc[:end_date].cov()

# def calculate_portfolio_volatility(weights: np.ndarray, cov_matrix: pd.DataFrame) -> float:
#     return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def calculate_portfolio_variance(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    # Convert inputs to NumPy arrays if they are not already
    weights = np.array(weights)
    cov_matrix = np.array(cov_matrix)
    
    # Assertions to check shapes
    assert weights.ndim == 1, "Weights should be a 1D array"
    assert cov_matrix.ndim == 2, "Covariance matrix should be a 2D array"
    assert cov_matrix.shape[0] == cov_matrix.shape[1], "Covariance matrix should be square"
    assert len(weights) == cov_matrix.shape[0], "Length of weights should match dimensions of covariance matrix"
    
    # Calculate portfolio variance
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return portfolio_variance
    
def calculate_portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    portfolio_variance = calculate_portfolio_variance(weights=weights, cov_matrix=cov_matrix)
    # Return portfolio volatility
    return np.sqrt(portfolio_variance)

def calculate_marginal_risk_contribution(weights: np.ndarray, cov_matrix: pd.DataFrame) -> np.ndarray:
    return weights * np.dot(cov_matrix, weights)

    
def calculate_total_risk_contribution(marginal_risk_contrib: np.ndarray, portfolio_volatility: float) -> np.ndarray:
    return marginal_risk_contrib / portfolio_volatility

    
def calculate_risk_contribution(w,V):
    # function that calculates asset contribution to total risk
    # print("w", w)
    V = np.array(V)
    sigma = np.sqrt(calculate_portfolio_variance(w,V))
    # print("sigma", sigma)
    # print("V", V)
    # print("np.dot(cov_matrix, weights)", np.dot(V, w))
    marg = calculate_marginal_risk_contribution(weights=w.T, cov_matrix=V)
    risk_cont = calculate_total_risk_contribution(marginal_risk_contrib=marg, portfolio_volatility=sigma)
    return risk_cont
    # return risk_cont

def normalize_risk_contributions(total_risk_contrib: np.ndarray) -> np.ndarray:
    return total_risk_contrib / total_risk_contrib.sum()

def sharpe_ratio(expected_return, volatility_return, risk_free_rate=0.01):
    return (expected_return - risk_free_rate) / volatility_return

def get_valid_assets(returns):
    # Remove columns where all values are NaN
    non_nan_assets = returns.dropna(axis=1, how='all')
    
    # Remove columns where all remaining values are 0
    cleaned_ret = non_nan_assets.loc[:, (non_nan_assets != 0).any()]
    
    # Return list of valid asset names
    return list(cleaned_ret.columns)
def risk_parity_weights(cov_matrix: pd.DataFrame) -> pd.Series:
    # Invert the diagonal covariance matrix to get the risk contribution
    inv_cov_matrix = np.linalg.inv(cov_matrix)
    risk_contribution = inv_cov_matrix.diagonal() / inv_cov_matrix.sum()
    weights = risk_contribution / risk_contribution.sum()
    return weights
    # return pd.Series(weights, index=cov_matrix.columns)

def portfolio_optimization(returns: pd.DataFrame, frequency: str, goal='minVol', risk_free_rate=0.01,
                          min_exposure=0.0, max_exposure=1.0) -> pd.Series:
    annual_factor = annualized_factor_from_freq[frequency]
    # Get mean returns and covariance matrix
    mean_returns = annualized_expected_return(returns=returns)
    cov_matrix = returns.cov() * annual_factor

    # Identify valid assets (non-NaN or non-zero returns)
    valid_assets = get_valid_assets(returns=returns)
    num_assets = len(valid_assets)
    if not num_assets:
        return pd.Series(index=mean_returns.index, dtype=float).fillna(0)

    # Filter returns and covariance matrix to include only valid assets
    mean_returns_filtered = mean_returns[valid_assets]
    cov_matrix_filtered = cov_matrix.loc[valid_assets, valid_assets]
    def total_weight_constraint(x):
        return np.sum(x)-1.0
    
    def long_only_constraint(x):
        return x
    constraints = ({'type': 'eq', 'fun': total_weight_constraint},
            {'type': 'ineq', 'fun': long_only_constraint})
    # Constraints and bounds for the optimization
    # constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((min_exposure, max_exposure) for _ in range(num_assets))
    initial_guess = num_assets * [1. / num_assets]

    def sharpe_helper(w, mean_returns, cov_matrix, risk_free_rate):
        expected_return = portfolio_return_from_weights(weights=w, mean_returns=mean_returns)
        volatility_return = calculate_portfolio_volatility(weights=w, cov_matrix=cov_matrix)
        return sharpe_ratio(expected_return=expected_return, volatility_return=volatility_return, risk_free_rate=risk_free_rate)
    def risk_budget_objective(w, cov_matrix, risk_targets=None):
        # calculate portfolio risk
        V = cov_matrix
        if risk_targets is None:
            risk_targets = np.array([1/num_assets] * num_assets)
        x_t = risk_targets
        x = w
        
        sig_p =  np.sqrt(calculate_portfolio_variance(x,V)) # portfolio sigma
    
        # compute proportion of total sigma (sums to total_sigma)
        risk_target = np.asmatrix(np.multiply(sig_p,x_t))        
        # these sum to sigma
        asset_RC = calculate_risk_contribution(x,V)
        myJ = np.sum((np.multiply(sig_p,x_t) - asset_RC) ** 2)
 
        return myJ
        
    if goal == "minVol":
        f = lambda w: calculate_portfolio_volatility(weights=w, cov_matrix=cov_matrix_filtered)
    elif goal == 'maxSharpe':
        f = lambda w: - sharpe_helper(w=w, mean_returns=mean_returns_filtered, cov_matrix=cov_matrix_filtered, risk_free_rate=risk_free_rate)
    elif goal == 'riskParity':
        f = lambda w: risk_budget_objective(w=w, cov_matrix=cov_matrix_filtered)# np.sum((w - risk_parity_weights(cov_matrix_filtered)) ** 2)
    else:
        raise ValueError("Invalid goal specified. Use 'minVol', 'maxSharpe', or 'riskParity'.")
    
    result = minimize(f, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimized_weights = pd.Series(result.x, index=valid_assets)
    else:
        raise ValueError("Optimization did not converge")

    # Assign weights for valid assets
    final_weights = pd.Series(index=mean_returns.index, dtype=float).fillna(0)
    final_weights.loc[valid_assets] = optimized_weights

    return final_weights
    
def calculate_portfolio_return(weights, returns):
    return np.dot(weights.fillna(0), returns.fillna(0))

def compute_weighted_returns(weights, returns):
    # Function to calculate portfolio return for a given date
    def calc_portfolio_return(date):
        w = weights.loc[date]
        returns_today = returns.loc[date]
        portfolio_return = calculate_portfolio_return(w, returns_today)
        return portfolio_return
        
    # Map the function to calculate portfolio returns
    portfolio_returns = returns.index.to_series().map(calc_portfolio_return)
    # Convert portfolio_returns to a Series with the same index
    portfolio_returns = pd.Series(portfolio_returns.values, index=returns.index)
    return portfolio_returns

def portfolio_allocation(returns, 
                          method='minVol', 
                          rebalance_freq='Q', 
                          frequency='daily', 
                          skip_first_n_periods=365, 
                          lookback_period=1095, 
                          risk_free_rate=0.01,
                          min_exposure=0.0,
                          max_exposure=1.0):
    # Create DataFrames for storing results
    stored_weights = pd.DataFrame(index=returns.index, columns=returns.columns)
    portfolio_returns = pd.Series(index=returns.index)
    assert frequency in annualized_factor_from_freq
    
    def compute_weights(date):
        end_date = date
        start_date = end_date - pd.Timedelta(days=lookback_period)
        
        if end_date <= returns.index[skip_first_n_periods]:
            stored_weights.loc[date] = pd.Series(np.nan, index=returns.columns)
        
        lookback_returns = returns.loc[start_date:end_date]
        from functools import partial
        try:
            if method == 'eqCont':
                weights = equal_contribution_weights(returns=lookback_returns)
            elif method in ('maxSharpe', 'minVol', 'riskParity'):
                weights = portfolio_optimization(returns=lookback_returns, frequency=frequency, goal=method,
                                                 min_exposure=min_exposure, max_exposure=max_exposure)
            else:
                raise ValueError()
            stored_weights.loc[date] = weights
        except ValueError as e:
            print(f"Error in optimization for date {date}: {e}")
            stored_weights.loc[date] = pd.Series(np.nan, index=returns.columns)
    
    rebalance_dates = returns.index.to_series().to_period(rebalance_freq).to_timestamp(rebalance_freq).sort_index().index.drop_duplicates()
    rebalance_dates.map(compute_weights)
    
    stored_weights_shifted = stored_weights.shift(1)
    stored_weights_filled = stored_weights_shifted.ffill().fillna(0)

    # Reindex to match returns_df
    stored_weights_filled = stored_weights_filled.reindex(returns.index).ffill().fillna(0)
    
    portfolio_returns = compute_weighted_returns(weights=stored_weights_filled, returns=returns)
    return portfolio_returns, stored_weights_filled

def portfolio_performance(portfolio_returns: pd.Series, frequency: str = "daily", risk_free_rate: float = 0.01):
    # Calculate cumulative portfolio returns
    portfolio_returns_cum = (1 + portfolio_returns).cumprod() - 1
    
    # Calculate annualized expected return
    optimized_ann_return = annualized_expected_return(returns=portfolio_returns, frequency=frequency)
    
    # Calculate annualized volatility
    optimized_vol = annualized_volatility(returns=portfolio_returns, frequency=frequency)
    
    # Calculate Sharpe Ratio
    optimized_sharpe = sharpe_ratio(expected_return=optimized_ann_return, 
                                    volatility_return=optimized_vol, 
                                    risk_free_rate=risk_free_rate)
    
    # Return a dictionary with all calculated values
    performance_metrics = {
        "cumulative_returns": portfolio_returns_cum,
        "annualized_return": optimized_ann_return,
        "annualized_volatility": optimized_vol,
        "sharpe_ratio": optimized_sharpe,
        "portfolio_returns": portfolio_returns
    }
    
    return performance_metrics

# Define the plotting function
def plot_portfolio_performance(portfolio_cum, sharpe):
    plt.figure(figsize=(14, 8))
    # plt.plot(equal_contrib_portfolio_cum, label=f'Equal Contribution Portfolio (Sharpe: {equal_contrib_sharpe:.2f})', linewidth=2)
    plt.plot(portfolio_cum, label=f'Mean-Variance Optimized Portfolio (Sharpe: {sharpe:.2f})', linewidth=2)
    plt.title('Portfolio Performance Comparison')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_portfolio_allocation_history(weights_df):
    # Sort the DataFrame by columns to ensure consistent layering
    sorted_weights = weights_df[weights_df.columns.sort_values()]
    
    # Create the plot
    plt.figure(figsize=(14, 8))
    
    # Plot the stacked area chart with consistent layering
    plt.stackplot(sorted_weights.index, sorted_weights.T, labels=sorted_weights.columns)
    
    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Portfolio Weight')
    plt.title('Asset Allocation Over Time')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Assets')
    
    # Show the plot
    plt.show()

def calculate_risk_contributions_over_time(weights_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
    risk_contributions = pd.DataFrame(index=weights_df.index, columns=weights_df.columns)
    
    for date in weights_df.index:
        cov_matrix = calculate_covariance_matrix(returns_df, date)
        weights = weights_df.loc[date].values
        portfolio_volatility = calculate_portfolio_volatility(weights, cov_matrix)
        marginal_risk_contrib = calculate_marginal_risk_contribution(weights, cov_matrix)
        total_risk_contrib = calculate_total_risk_contribution(marginal_risk_contrib, portfolio_volatility)
        normalized_risk_contrib = normalize_risk_contributions(total_risk_contrib)
        
        risk_contributions.loc[date] = normalized_risk_contrib
        
    return risk_contributions

def plot_risk_contributions(risk_contributions: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    risk_contributions[risk_contributions.columns.sort_values()].plot(kind='area', stacked=True, ax=ax, cmap='tab20')
    ax.set_title('Normalized Risk Contribution of Each Asset Over Time')
    ax.set_ylabel('Risk Contribution')
    ax.set_xlabel('Date')
    plt.legend(title='Assets', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_portfolio_risk_contribution_history(weights_df: pd.DataFrame, returns_df: pd.DataFrame) -> None:
    risk_contributions = calculate_risk_contributions_over_time(weights_df, returns_df)
    plot_risk_contributions(risk_contributions)

