import pandas as pd
import numpy as np
import yfinance as yf
import logging
import matplotlib.pyplot as plt
from scipy.optimize import minimize

"""
import importlib
imported_module = importlib.import_module("portfolio_optimization")
importlib.reload(imported_module)
from portfolio_optimization import *
"""

# {"AGG": "Investment-Grade Bonds",            # iShares Core U.S. Aggregate Bond ETF # LQD: iShares iBoxx $ Investment Grade Corporate Bond ETF
#  "IGOV": "International Sovereign Bonds",
#  "HYG": "High-Yield Bonds",
#  "IVV": "U.S. Equities",
#  "XEM": "Emerging Market Equities",          # iShares MSCI Emerging Markets Index ETF
#  "ACWX" "International Equities",            # iShares MSCI ACWI ex U.S. ETF
#  "IYR": "Real Estate"                        # iShares U.S. Real Estate ETF
#  "GSG": "Commodities"                        # iShares S&P GSCI Commodity-Indexed Trust
#  } 
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os
from typing import List

def download_tickers_returns(tickers: List[str], start_date=None, cache_path: str=None):
    if cache_path and os.path.exists(cache_path):
        returns_df = pd.read_csv(cache_path, index_col="Date")

        # Ensure the index of returns_df is of datetime type
        returns_df.index = pd.to_datetime(returns_df.index)
            
        # Ensure the data in returns_df is of float type
        returns_df = returns_df.astype(float)
        return returns_df
        
    returns_df = pd.DataFrame()

    # Fetch daily returns for each ticker
    for ticker, asset_class in tickers.items():
        try:
            # Fetch historical data for the ticker
            data = yf.download(ticker, start=start_date)
            
            # Check if the data is empty
            if data.empty:
                print(f"No data found for ticker: {ticker}")
                continue
            
            # Calculate daily returns
            data['Daily Return'] = data['Adj Close'].pct_change()
            
            # Add the daily returns to the returns DataFrame
            data = data[['Daily Return']].rename(columns={'Daily Return': asset_class})
            if returns_df.empty:
                returns_df = data
            else:
                returns_df = returns_df.join(data, how='outer')
           
        except Exception as e:
            print(f"Failed for ticker: {ticker}")
            print(e)
    # Ensure the index of returns_df is of datetime type
    returns_df.index = pd.to_datetime(returns_df.index)
        
    # Ensure the data in returns_df is of float type
    returns_df = returns_df.astype(float)
    # VERY IMPORTANT, OTHERWISE MANY COMPUTATIONS WOULD RETURN NONE, FROM 
    # PORT OPT, t orisk cont
    returns_df.fillna(0, inplace=True)
    # Drop the first row with NaN values
    returns_df = returns_df.iloc[1:]
    if cache_path:
        returns_df.to_csv(cache_path, index=True)
    return returns_df


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
from collections.abc import Iterable

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

def portfolio_return_from_weights(weights, returns):
    return np.dot(weights, returns)

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
    # DONT CHANGE ORDER OF ARGS OTEHERWISE WOULD AFFCT MIN VOL! MAYBE ADD ANOTHER Func
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


def portfolio_optimization(cov_matrix: pd.DataFrame,
                           expected_returns: pd.Series=None,
                           goal='minVol', 
                           risk_free_rate=0.01,
                           risk_budget = None,
                           target_return=None,
                           long_only=True,
                           total_weight=1.0,
                           min_exposure=0.0, max_exposure=1.0) -> pd.Series:
    
    def target_return_constraint(x):
        return portfolio_return_from_weights(weights=x, returns=returns) - target_return
        
    def total_weight_constraint(x):
        return np.sum(x)-total_weight
    
    def long_only_constraint(x):
        return x
        
    # Constraints and bounds for the optimization
    constraints= ({'type': 'eq', 'fun': total_weight_constraint}, )
    
    if long_only:
        constraints += ({'type': 'ineq', 'fun': long_only_constraint}, )
    if target_return:
        contraints += ({'type': 'eq', 'fun': target_return_constraint}, )
        
    # constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    num_assets = cov_matrix.shape[0]
    if 1 / num_assets > max_exposure:
        logging.warning(f"Max Exposure can't be {max_exposure} since there are only {num_assets} assets to optimize for with returns in this time period. Replacing max_exposure with 1 / {num_assets}")
    max_exposure = max(max_exposure, 1 / num_assets)
    bounds = tuple((min_exposure, max_exposure) for _ in range(num_assets))
    initial_guess = num_assets * [1. / num_assets]

    def sharpe_ratio_maximization(w, expected_returns, cov_matrix, risk_free_rate):
        port_return = portfolio_return_from_weights(weights=w, returns=expected_returns)
        port_vol = calculate_portfolio_volatility(weights=w, cov_matrix=cov_matrix)
        return - sharpe_ratio(expected_return=port_return, volatility_return=port_vol, risk_free_rate=risk_free_rate)
    
    def risk_budget_objective(w, cov_matrix, risk_budget=None):
        # calculate portfolio risk
        V = cov_matrix
        if risk_budget is None:
            risk_budget = np.array([1/num_assets] * num_assets)
        x_t = risk_targets
        x = w
        
        sig_p =  np.sqrt(calculate_portfolio_variance(x,V)) # portfolio sigma
    
        # compute proportion of total sigma (sums to total_sigma)
        risk_target = np.asmatrix(np.multiply(sig_p,x_t))        
        asset_RC = calculate_risk_contribution(x,V)
        J = np.sum((np.multiply(sig_p,x_t) - asset_RC) ** 2)
        return J
        
    if goal == "minVol":
        f = calculate_portfolio_volatility
        args = (cov_matrix)
        
    elif goal == 'maxSharpe':
        f = sharpe_ratio_maximization
        args = (expected_returns, cov_matrix, risk_free_rate)
        
    elif goal == 'riskParity':
        f = risk_budget_objective(w=w)
        args = (cov_matrix, risk_budget)
    else:
        raise ValueError("Invalid goal specified. Use 'minVol', 'maxSharpe', or 'riskParity'.")
    
    result = minimize(f, initial_guess, args=args, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimized_weights = result.x
        if isinstance(expected_returns, pd.Series):   
            assets = list(expected_returns.index)
            oppltimized_weights = pd.Series(optimized_weights, index=assets)            
    else:
        raise ValueError("Optimization did not converge")
    # return all result TODO
    return optimized_weights

def get_global_minimum_variance_portfolio(cov_matrix):
    return portfolio_optimization(goal='minVol', cov_matrix=cov_matrix)

def get_tangent_portfolio(expected_returns, cov_matrix, risk_free_rate=0.01):
    return portfolio_optimization(goal="maxSharpe", cov_matrix=cov_matrix, expected_returns=expected_returns, risk_free_rate=risk_free_rate)

def generate_portfolios(returns, cov_matrix, num_portfolios=10000, risk_free_rate=0.01, seed=42):
    # Seed for reproducibility
    np.random.seed(seed)
    num_assets = len(returns)
    results = np.zeros((3, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        weights_record.append(weights)
        port_return = portfolio_return_from_weights(weights=weights, returns=returns)
        port_volatility = calculate_portfolio_volatility(weights=weights, cov_matrix=cov_matrix)
        port_sharpe = sharpe_ratio(port_return, port_volatility, risk_free_rate)

        results[0, i] = port_volatility
        results[1, i] = port_return
        results[2, i] = port_sharpe

    return results, weights_record
    

def plot_efficient_frontier_and_portfolios(returns, cov_matrix, risk_free_rate=0.01):
    # Generate random portfolios
    results, weights_record = generate_portfolios(returns, cov_matrix)
    
    # Get the Global Minimum Variance Portfolio
    gmvp = get_global_minimum_variance_portfolio(cov_matrix)
    gmvp_return = portfolio_return_from_weights(weights=gmvp, returns=returns)
    gmvp_volatility = calculate_portfolio_volatility(weights=gmvp, cov_matrix=cov_matrix)
    
    # Get the Tangent Portfolio
    tangent_portfolio = get_tangent_portfolio(returns, cov_matrix, risk_free_rate)
    tangent_return = portfolio_return_from_weights(weights=tangent_portfolio, returns=returns)
    tangent_volatility = calculate_portfolio_volatility(weights=tangent_portfolio, cov_matrix=cov_matrix)
    
    # Plotting
    plt.figure(figsize=(14, 8))
    
    # Scatter plot of randomly generated portfolios
    plt.scatter(results[0, :], results[1, :], c=results[2, :], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
    plt.colorbar(label='Sharpe Ratio')
    
    # Plot the Efficient Frontier
    efficient_frontier_volatilities = []
    efficient_frontier_returns = []
    num_assets = len(returns)
    bounds = tuple((0, 1) for asset in range(num_assets))
    for target_return in np.linspace(gmvp_return, max(results[1, :]), 100):
        constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return_from_weights(weights=x, returns=returns) - target_return},
                       {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        result = minimize(calculate_portfolio_volatility, gmvp, args=cov_matrix,
                          method='SLSQP', bounds=bounds, constraints=constraints)
        efficient_frontier_volatilities.append(result.fun)
        efficient_frontier_returns.append(target_return)
    
    plt.plot(efficient_frontier_volatilities, efficient_frontier_returns, 'r-', lw=2)
    
    # Plot GMVP and Tangent Portfolio
    plt.scatter(gmvp_volatility, gmvp_return, marker='*', color='g', s=100, label='GMVP')
    plt.scatter(tangent_volatility, tangent_return, marker='*', color='r', s=100, label='Tangent Portfolio')
    
    plt.title('Efficient Frontier with GMVP and Tangent Portfolio')
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Return')
    plt.legend()
    plt.grid(True)
    plt.show()

def compute_weighted_returns(weights: pd.DataFrame, returns: pd.DataFrame):
    # Function to calculate portfolio return for a given date
    def calc_portfolio_return(date):
        w = weights.loc[date]
        returns_today = returns.loc[date]
        portfolio_return = portfolio_return_from_weights(weights=w.fillna(0), returns=returns_today.fillna(0))
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
    annual_factor = annualized_factor_from_freq[frequency]

    def compute_weights(date):
        end_date = date
        start_date = end_date - pd.Timedelta(days=lookback_period)
        
        if end_date <= returns.index[skip_first_n_periods]:
            stored_weights.loc[date] = pd.Series(np.nan, index=returns.columns)
        
        lookback_returns = returns.loc[start_date:end_date]
        # Get mean returns and covariance matrix
        expected_returns = annualized_expected_return(returns=lookback_returns)
        cov_matrix = lookback_returns.cov() * annual_factor
        # Identify valid assets (non-NaN or non-zero returns)
        assets = list(lookback_returns.columns)
        valid_assets = get_valid_assets(returns=lookback_returns)
        num_assets = len(valid_assets)
        if not num_assets:
            stored_weights.loc[date] = pd.Series(0.0, index=lookback_returns.columns)
            return 
        # Filter returns and covariance matrix to include only valid assets
        expected_returns_filtered = expected_returns[valid_assets]
        cov_matrix_filtered = cov_matrix.loc[valid_assets, valid_assets]
    
        from functools import partial
        try:
            if method == 'eqCont':
                weights = equal_contribution_weights(returns=lookback_returns)
            elif method in ('maxSharpe', 'minVol', 'riskParity'):
                weights = portfolio_optimization(expected_returns=expected_returns_filtered, 
                                                 cov_matrix=cov_matrix_filtered, 
                                                 goal=method,
                                                 min_exposure=min_exposure, max_exposure=max_exposure)
            else:
                raise ValueError()
            # Assign weights for valid assets
            final_weights = pd.Series(index=assets, dtype=float).fillna(0)
            final_weights.loc[valid_assets] = weights
            stored_weights.loc[date] = final_weights
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

def calculate_portfolio_cumulative_returns(portfolio_returns: pd.Series) -> pd.Series:
    return  (1 + portfolio_returns).cumprod() - 1
    
def portfolio_performance(portfolio_returns: pd.Series, frequency: str = "daily", risk_free_rate: float = 0.01):
    # Calculate performance for various periods
    periods = {
        "inception": portfolio_returns.index.min(),
        "1Y": portfolio_returns.index[-1] - pd.DateOffset(years=1),
        "3Y": portfolio_returns.index[-1] - pd.DateOffset(years=3),
        "5Y": portfolio_returns.index[-1] - pd.DateOffset(years=5),
        "10Y": portfolio_returns.index[-1] - pd.DateOffset(years=10)
    }
    
    performance_metrics = {}

    for period_name, start_date in periods.items():
        if start_date < portfolio_returns.index.min():
            start_date = portfolio_returns.index.min()

        returns_period = portfolio_returns[start_date:]
        
        # Calculate cumulative portfolio returns
        portfolio_returns_cum = calculate_portfolio_cumulative_returns(returns_period)
        
        # Calculate annualized expected return
        ann_return = annualized_expected_return(returns=returns_period, frequency=frequency)
        
        # Calculate annualized volatility
        ann_volatility = annualized_volatility(returns=returns_period, frequency=frequency)
        
        # Calculate Sharpe Ratio
        sharpe = sharpe_ratio(expected_return=ann_return, 
                                        volatility_return=ann_volatility, 
                                        risk_free_rate=risk_free_rate)
        
        performance_metrics[period_name] = {
            "annualized_return": ann_return,
            "annualized_volatility": ann_volatility,
            "sharpe_ratio": sharpe,
        }
    
    return pd.DataFrame(performance_metrics)

# Define the plotting function

def plot_portfolio_performance(portfolio_returns, benchmark_returns=None, portfolio_label='Portfolio', benchmark_labels=None):
    # Calculate cumulative returns for the portfolio
    port_cumul = calculate_portfolio_cumulative_returns(portfolio_returns)
    
    # Set up the plot
    plt.figure(figsize=(14, 8))
    
    # Plot the portfolio's cumulative returns
    plt.plot(port_cumul, label=f'{portfolio_label} (CAGR: {annualized_expected_return(portfolio_returns):.2%}, Sharpe: {sharpe_ratio(annualized_expected_return(portfolio_returns), annualized_volatility(portfolio_returns)):.2f})', linewidth=2)

    # Plot benchmark cumulative returns if provided
    if benchmark_returns is not None:
        if not isinstance(benchmark_returns, list):
            benchmark_returns = [benchmark_returns]
        if not benchmark_labels:
            benchmark_labels = [f'Benchmark {i+1}' for i in range(len(benchmark_returns))]
        
        for bench_return, label in zip(benchmark_returns, benchmark_labels):
            bench_cumul = calculate_portfolio_cumulative_returns(bench_return)
            plt.plot(bench_cumul, label=f'{label} (CAGR: {annualized_expected_return(bench_return):.2%}, Sharpe: {sharpe_ratio(annualized_expected_return(bench_return), annualized_volatility(bench_return)):.2f})', linewidth=2)
    
    # Enhance plot appearance
    plt.title('Portfolio Performance Comparison', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Cumulative Return', fontsize=14)
    plt.legend(fontsize=12)
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
    
def plot_piecharts(items, titles):
    fig, ax = plt.subplots(1, len(items), figsize=(12, 6))

    for i, it in enumerate(items):
        # Filter out zero values
        filtered_values = {k: v for k, v in it.items() if v > 0}

        # Plot the pie chart
        wedges, texts, autotexts = ax[i].pie(filtered_values.values(), 
                                             labels=filtered_values.keys(), 
                                             autopct='%1.1f%%', 
                                             startangle=140, 
                                             colors=plt.get_cmap('tab20').colors)
        
        # Adjust text size and label positions to avoid overlap
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(8)
        
        ax[i].set_title(titles[i])

    plt.tight_layout()
    plt.show()

def plot_rolling_correlations(returns_df, target_asset, comparison_assets, window_months=12, plots_per_row=3):
    """
    Plot the n-month rolling correlations between a target asset class and each comparison asset class in a grid of plots.

    Parameters:
    - returns_df (pd.DataFrame): DataFrame containing daily returns for various asset classes.
    - target_asset (str): The asset class to which correlations are computed.
    - comparison_assets (list of str): List of asset classes to compare against the target asset.
    - window_months (int): Rolling window size in months.
    - plots_per_row (int): Number of plots per row in the grid.
    """
    # Convert window size from months to trading days (approx. 21 trading days per month)
    window_days = window_months * 21
    
    # Determine the number of rows needed
    num_plots = len(comparison_assets)
    num_rows = int(np.ceil(num_plots / plots_per_row))
    
    plt.figure(figsize=(plots_per_row * 5, num_rows * 4))  # Adjust size for grid layout

    for i, asset in enumerate(comparison_assets):
        if asset in returns_df.columns:
            # Calculate rolling correlation with the target asset
            rolling_corr = returns_df[asset].rolling(window=window_days).corr(returns_df[target_asset])
            
            # Determine subplot position
            row = i // plots_per_row
            col = i % plots_per_row
            
            plt.subplot(num_rows, plots_per_row, i + 1)
            plt.plot(rolling_corr.index, rolling_corr, label=asset)
            plt.title(f'{asset}')
            plt.xlabel('Date')
            plt.ylabel('Rolling Correlation')
            plt.legend(loc='best')
            plt.grid(True)
        else:
            print(f"Warning: {asset} not found in returns_df")
    
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.suptitle(f'{window_months}-Month Rolling Correlations with {target_asset}', y=1.02)
    plt.show()
    
def plot_weight_allocations(weights: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    weights[weights.columns.sort_values()].plot(kind='area', stacked=True, ax=ax, cmap='tab20')
    ax.set_title('Weights of Each Asset Over Time')
    ax.set_ylabel('% Portfolio Allocation')
    ax.set_xlabel('Date')
    plt.legend(title='Assets', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    
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

