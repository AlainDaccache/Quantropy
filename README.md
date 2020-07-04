# MAtilDA Overview
This project is the culmination of three years of learning about the financial markets, and a year of (on/off) developing a platform in order to provide a comprehensive and unified approach to trading the financial markets.

## Step #1: Data Gathering

Relevant historical data points are collected

- **Basic Stock Information**: ticker, name, cik, industry, sector, exchange traded in...
- **Financial Statements**: we scrape and normalize the main financial statements (Balance Sheet, Income Statement, Cash Flow Statement) from companies 10-K (yearly) and 10-Q (quarterly) filings using the SEC Archives, for **up to the last 20 years**. 
- **Price Action**: we scrape the open, high, low, close (adjusted) of stock prices, and trading volumes (for daily, weekly, monthly and yearly timeframes) from YahooFinance
- **Misc**: Insider Trading Reports (SEC Form 4), Gross National Product price index levels, risk-free rates...

## Step #2: Company Analysis

### Fundamental Analysis
In this section, we take the numerical values from the financial statements in order to analyse the companies behind those stocks.
#### Financial Ratios
Financial ratios are used in order to assess a company's performance, typically to track their changes in value over time and to compare them with those of competitors in the industry.

- **Liquidity ratios:** Current Ratio, Acid-Test Ratio, Cash Ratio, Operating Cash Flow Ratio
- **Leverage ratios:** Debt Ratio, Debt to Equity Ratio, Interest Coverage Ratio, Debt Service Coverage Ratio
- **Efficiency ratios:** Asset Turnover Ratio, Inventory Turnover Ratio, Receivables Turnover Ratio, Days Sales in Inventory Ratio
- **Profitability ratios:** Gross Margin Ratio, Operating Margin Ratio, Return on Assets Ratio, Return on Equity Ratio
- **Market value ratios:** Book Value per Share Ratio, Dividend Yield Ratio, Earnings per Share Ratio, Price to Earnings Ratio

#### Valuation Methods
There are two main categories when calculating the fair value of a business.

##### Absolute (Intrinsic) Valuation Models
- **Dividend discount models:** including the Gordon growth model and multi-stage dividend discount model
- **Discounted cash flow (DCF)**
- **Residual income**
- **Asset-based models**

##### Relative Valuation Models
- Comparable models: calculating multiples or ratios, such as the price-to-earnings or P/E multiple, and comparing them to the multiples of other comparable firms.

#### Scoring Systems
A plethora of financial models use financial ratios in order to identify whether companies are experiencing financial distress, manipulating their earnings... 
- **Financial Health Scores:** Piotroski's F-Score, Altman's Z-Score, Ohlson's O-Score
- **Earnings Manipulation Scores**: Beneish's M-Score, Montier's C-Score, Nichols O-Score
- **Misc**: Zacks Rank (uses earnings estimates and their revisions)

### Technical Analysis
In this section, we take the prices and volumes scraped from above. 

#### Technical Indicators

|           |   Indicators
|:----------:|:---------:|
|Trend|Moving Average Convergence Divergence (MACD)<br />Average Directional Movement Index (ADX)<br />Vortex Indicator (VI)<br />Trix (TRIX)<br />Mass Index (MI)<br />Commodity Channel Index (CCI)<br />Detrended Price Oscillator (DPO)<br />KST Oscillator (KST)<br />Ichimoku Kinkō Hyō (Ichimoku)<br />Parabolic Stop And Reverse (Parabolic SAR)|
|Momentum|Money Flow Index (MFI)<br />Relative Strength Index (RSI)<br />True strength index (TSI)<br />Ultimate Oscillator (UO)<br />Stochastic Oscillator (SR)<br />Williams %R (WR)<br />Awesome Oscillator (AO)<br />Kaufman's Adaptive Moving Average (KAMA)<br />Rate of Change (ROC)|
|Volume|Accumulation/Distribution Index (ADI)<br />On-Balance Volume (OBV)<br />Chaikin Money Flow (CMF)<br />Force Index (FI)<br />Ease of Movement (EoM, EMV)<br />Volume-price Trend (VPT)<br />Negative Volume Index (NVI)<br />Volume Weighted Average Price (VWAP)|
|Volatility|Average True Range (ATR)<br />Bollinger Bands (BB)<br />Keltner Channel (KC)<br />Donchian Channel (DC)|
|Others|Daily Return (DR)<br />Daily Log Return (DLR)<br />Cumulative Return (CR)|


#### Miscellaneous

- **Support and Resistance:** Trend lines, Pivots, Fibonacci lines, Moving Averages, Psychological levels
- **Trading Systems:** Bill Williams' Chaos Trading, Goichi Hosoda's Ichimoku Kinko Hyo, Scott Carney's Harmonic Trading

#### Candlestick Patterns
    
|           |   Bullish |   Bearish |
|:----------:|:---------:|:--------:|
|   Reversal |Three Line Strike,||
|   Continuation |||

#### Chart Patterns

|           |   Bullish |   Bearish |
|:----------:|:---------:|:--------:|
|   Reversal |||
|   Continuation |||


## Step #3 Portfolio Construction

When designing an investment strategy, we:
1. Screen Stocks based on some criteria. Some papers eliminate 
2. 
Strategies dictate the choice of the stocks, direction of the trade, allocation of portfolio balance to those stocks, as well as entry and exit conditions

### Stock Selection Strategies
Here, we filter stocks that fulfill criteria based on fundamental and technical analysis techniques gathered and computed above. This includes financial statements entries, price action, accounting ratios, scoring/ranking systems... 

Strategies either use values as **absolute** (i.e. a good Current Ratio is agreed to be between 1.2 to 2) or **relative** (i.e. total debt less than book value, a Price to Earnings Ratio < 4th decile in the industry segment etc., stability of growth of earnings...). Many investment philosophies arose depending on people's objectives, risk profile, and views on the market (I highly recommend reading about the [Efficient Market Hypothesis](https://en.wikipedia.org/wiki/Efficient-market_hypothesis)), mainly:

| Investing Style     | Common Metrics Used   | Popular Strategies / Investors / Funds |
|:--------------------:|:--------------------- |:--------------------------------------:|
| Value Investing| Price-to-Earnings<br />Price-to-Sales<br />Price-to-Book<br />Debt-to-Equity<br /> Price-to-Free Cash Flow|Enterprising vs Defensive Investor Criteria (Benjamin Graham, in *The Intelligent Investor*)<br />Magic Formula Investing (Joel Greenblatt, in *The Little Book that Beats the Market*)                                        |
| Growth Investing|Net Profit Margin<br />Sales Growth<br />Earnings Growth<br />Free Cash Flow Growth|CAN SLIM (William J. O'Neil, in *How to Make Money in Stocks: A Winning System In Good Times or Bad*)                                      |
| GARP Investing (Hybrid)|Price-to-Earnings-to-Growth|Lynch Fair Value (Peter Lynch, in *One Up on Wall Street* and *Learn to Earn*)                                     |
|Quality Investing|Operating Margin<br />ROE<br />ROI<br />||
| Momentum Investing|Momentum Indicators<br />Biggest Winners / Losers|Narasimhan Jegadeesh and Sheridan Titman, in *Returns to Buying Winners and Selling Losers*|  
| Income Investing|Dividend Yield<br />Payout Ratio<br />Dividend Growth<br />|                                        |

Definitely, the option to create your custom stock screener is available

### Portfolio Optimization

This section attempts to build a portfolio that maximizes the returns for the level of risk the investor is willing to take (i.e. risk-adjusted returns). Quantifying the risk of a portfolio of assets has been an area of research for several decades. 

#### Unsystematic Risk

**Unsystematic risk**, or that associated to a specific company or industry. It can be reduced by diversifying across uncorrelated assets. 

Originally, Markowitz's pioneering work on **Modern Portfolio Theory** modeled the risk of a portfolio to be equal to the standard deviation of its returns, in other words, how far, on average, were the returns of the portfolio dispersed from its mean. In the case of a combination of assets, risk would therefore be computed via the covariance between the pairs of investments.
This formalizes and extends diversification, because, an asset's risk and return should not be assessed by itself, but by how it contributes to a portfolio's overall risk and return. In other words, less correlation between pairs of assets would imply less risk of the overall portfolio. 

However, this methodology has several downfalls. Since it uses the standard deviation, the model assumes a Gaussian distribution of the returns, which is hardly the case. It thus considers returns above the mean to be risk as well. Since it is an average, it gives the same weight to both sides, effectively underestimating downside risk. Since investment returns tend to have a non-normal distribution, however, there in fact tend to be different probabilities for losses than for gains. Abnormalities like kurtosis, fatter tails and higher peaks, or skewness on the distribution can be problematic to risk measures based on volatility alone. 

Downside risk measures have since been developed. Also, improvements on this theory, such as *Post-Modern Portfolio Theory* and *Black–Litterman Model* optimization, help (1) adopt non-normally distributed, asymmetric, and fat-tailed measures of risk, and (2) incorporate relative and absolute 'views' on inputs of risk and returns from, respectively.


| Measure of Risk | Risk-adjusted Performance Measures |
|:---------------:|:-----:|
|Volatility|Treynor Ratio<br />Sharpe Ratio<br />Information Ratio<br />Modigliani Ratio|
|Downside Risk|Expected Shortfall<br /> Value at Risk (VaR)<br /> Roy's Safety First Ratio <br />Excess VaR<br />Conditional Sharpe Ratio<br />Sortino Ratio<br />Omega Ratio<br />Kappa Ratio<br />Gain-Loss Ratio<br />Upside Potential Ratio|
|Drawdown Risk|Calmar Ratio<br />Sterling Ratio<br />Burke Ratio|

Even then, downside measures would still suffer from something fundamental; they assume a constant long-term mean and variance, independent of time (*stationary process*), which isn't realistic, as *black-swan events* may occur. Techniques have been developed in order to transform the time series data so that it becomes stationary. 
- If the non-stationary process is a random walk with or without a drift, it is transformed to stationary process by differencing. 
- On the other hand, if the time series data analyzed exhibits a deterministic trend, the spurious results can be avoided by detrending. 
- Sometimes the non-stationary series may combine a stochastic and deterministic trend at the same time and to avoid obtaining misleading results both differencing and detrending should be applied, as differencing will remove the trend in the variance and detrending will remove the deterministic trend.


#### Systematic Risk

**Systematic risk**, or that inherent to the entire market or market segment. Systematic risk cannot be diversified away, but can be reduced (within one market) through market-neutral strategies, by using both long and short positions within one portfolio. Market neutral portfolios, therefore, will be uncorrelated with broader market indices. For example, in *pairs trading*, we would look for highly historically correlated assets, and when the correlation would temporarily weaken, we short the outperforming stock and long the underperforming one. The weights allocated would be such that the weighted average beta is zero, meaning the portfolio has no market exposure.

## Step #4: Backtesting and Tracking

To evaluate how a portfolio performs, we run regression models that use factors in an attempt to describe the returns of the portfolio with the returns of the market as a whole (i.e. a benchmark/index such as the S&P 500 for the American market, the FTSE 100 for the European market...). 
The *alpha* is the return on an investment that is not a result of the risk-factors in the model (i.e. for CAPM, the general movement in the greater market).

- Capital Asset Pricing Model
- Fama-French Three-Factor Model
- Carhart Four-Factor Model
- Fama-French Five-Factor Model

The software also allows developers to implement interfaces for entry and exit conditions, and observe how the portfolio has performed over time (as well as tracks i.e. *forward testing*)