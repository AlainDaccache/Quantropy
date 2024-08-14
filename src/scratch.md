Diversification benefits of low-correlated assets in a portfolio


Investing Top Down or Bottom Up

Top Down: process for portfolio construction doesn't start at stock selection. 
Is more about analyzing market conditions (via macroeconomics) and identify given market cycle.

Then, given rationale and empirical evidence regarding what "asset segments" perform better during which cycle, they accordingly allocate weights to each over time. For instance, this segmentation can be 

- style-based e.g. value vs growth stocks, 

- class-based (equity vs. debt, or more granularity: U.S. Equities, Emerging Market Equities, International Equitieis, Commodities, Real Estate, High-Yield Bonds, Investment-Grade Bonds, and International Sovereign Bonds), 

- sector/industry based (cyclical or non-cyclical) 

- factor-based (size, value, volatility, dividend, momentum, quality)

Then, based on discretion of portfolio manager, can decide how to diverisfy the portfolio. Can be asset-class based (60% stocks, 40% bonds) or 15% in industry A, 20% in industry B etc.) or risk-based (e.g. risk parity: each element of portfolio contributes equally towardfactor tilt: more than 60% of overall portfolio risk contributed by value factor)


* Bottom up



Total Portfolio Risk is Measured by Portfolio Variance, measured by $w^T \Sigma w$, where $\Sigma$ is the covariance matrix.

Covariance matrix can be straightforward or include more robust estimators such as Minimum Covariance Determinant (MCD), Shrinkage Estimators (e.g. Ledoit-Wolf Shrinkage).

Thus, methods that use covariance matrix such as Risk Parity or Factor Tilting as measure of contribution towards overall risk (which depends on covariance matrix), will need the covariance matrix's computation to be easily swappable -> pass it as param everywhere.

Portfolio Expected Returns

Can take average (and even weighted average e.g. SMA, EMA) but history isn't a predictor of expected. Can also use a factor-based model (CAPM, FF3, etc.), but that also is a prediction that might not necessarily be accurate.

Mean-Variance Framework:

The original work was done by finding weights that maximizes risk-adjusted returns as measured by Sharpe Ratio, which uses average returns for expected, and standard covariance matrix for volatility measurements, with volatility being the proxy of risk.

It is therefore generalizable to include other measures for expected returns or risk, as well as 

- maximizing other risk-adjusted measures of return, including Treynor, Sortino, Jensen's Alpha, Information Ratio.

- minimizing risk like volatility, Beta, (C)VaR, Max Drawdown etc.

Risk Contribution Perspective

Another perspective is instead of focusing on allocation of capital, is to think of allocation of risk. 

* Minimum volatility / variance portfolio.

* Risk Parity: each portfolio element contributing equally to portfolio overall 

* Risk Budgeting: define allocation of risk not necessarily equal.

* Factor Tilt: budgeting based on bias towards factor(s). how much a factor could contribute towards total risk.

* Beta Neutral: portfolio allocates 0 risk to that factor.

Portfolio Risk can be evaluate via
- Covariance Matrix
- Factor Covariance Matrix, Idiosyncratic Variance Matrix, Idiosyncratic Variance Vector


Factor Research:
- Get universe of equities
- Specify Factor Model: fundamental (SMB, HML...), statistical (PCA)
- 
Side notes:

Risk "Premium" -> implies additional over something, which is the Risk Free Rate. An "equity risk premium" means, our alternative from going with a risk-free asset carries risk but is associated with a premium for going form riskless to risk-y.

