# MAtilDA Overview
This project is the culmination of three years of learning about the financial markets, and a year of (on/off) developing a platform in order to provide a comprehensive and unified approach to trading the financial markets

## Step #1: Data Scraping

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
There are two main categories when estimating the value of a business.
- **Breakup Value**
- **Going Concern Value:** Discounted Cash Flow Analysis, Comparable Company Analysis, Precedent Transactions

#### Scoring Systems
A plethora of financial models use financial ratios in order to identify whether companies are experiencing financial distress, manipulating their earnings... 
- **Financial Health Scores:** Piotroski's F-Score, Altman's Z-Score, Ohlson's O-Score
- **Earnings Manipulation Scores**: Beneish's M-Score, Montier's C-Score, Nichols O-Score
- **Misc**: Zacks Rank (uses earnings estimates and their revisions)

### Technical Analysis
In this section, we take the prices and volumes scraped from above. 

#### Technical Indicators

Notice some indicators fit into more than one category. There are many, many others, but the following are the **most** widely used:
- **Trend Indicators:** Moving Averages (MA) (Simple, Smoothed, Exponential, Double Exponential, Kaufman's Adaptive), Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Bollinger Bands®, Parabolic SAR, On-Balance Volume (OBV)
- **Momentum Oscillators:** Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Stochastic Oscillator
- **Volume Indicators**: On-Balance Volume (OBV), Chaikin Money Flow, and Klinger Volume Oscillator
- **Volatility Indicators:** Volatility Index (VIX), Average True Range (ATR), and Bollinger Bands®


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

Strategies dictate the choice of the stocks, direction of the trade, allocation of portfolio balance to those stocks, as well as entry and exit conditions

### Stock Selection Strategies
Here, we filter stocks that fulfill criteria based on fundamental and technical analysis techniques gathered and computed above. This includes financial statements entries, price action, accounting ratios, scoring/ranking systems... 

Strategies either use values as **absolute** (i.e. a good Current Ratio is agreed to be between 1.2 to 2) or **relative** (i.e. total debt less than book value, a Price to Earnings Ratio < 4th decile in the industry segment etc., stability of growth of earnings...). Many investment philosophies arose depending on people's objectives, risk profile, and views on the market (I highly recommend reading about the [Efficient Market Hypothesis](https://en.wikipedia.org/wiki/Efficient-market_hypothesis)), mainly:

| Investing Style     | Common Metrics Used   | Popular Strategies / Investors / Funds |
|:--------------------:|:--------------------- |:--------------------------------------:|
| Value Investing| Price-to-Earnings<br />Price-to-Sales<br />Price-to-Book<br />Debt-to-Equity<br /> Price-to-Free Cash Flow|Enterprising vs Defensive Investor Criteria (Benjamin Graham, in *The Intelligent Investor*)<br />Magic Formula Investing (Joel Greenblatt, in *The Little Book that Beats the Market*)                                        |
| Growth Investing|Net Profit Margin<br />Sales Growth<br />Earnings Growth<br />Free Cash Flow Growth|CAN SLIM (William J. O'Neil, in *How to Make Money in Stocks: A Winning System In Good Times or Bad*)                                      |
| GARP Investing (Hybrid)|Price-to-Earnings-to-Growth|Lynch Fair Value (Peter Lynch, in *One Up on Wall Street* and *Learn to Earn*)                                     |
| Momentum Investing|Momentum Indicators<br />Biggest Winners / Losers|Narasimhan Jegadeesh and Sheridan Titman, in *Returns to Buying Winners and Selling Losers*|  
| Income Investing|Dividend Yield<br />Payout Ratio<br />Dividend Growth<br />|                                        |

Definitely, the option to create your custom stock screener is available

### Portfolio Allocation

It makes sense to invest in a portfolio of assets that would maximize returns and minimize risk, in other words maximize risk-adjusted returns. Several measures of risk exist in order to assess the risk-adjusted performance of a portfolio.

| Measure of Risk | Risk-adjusted Performance Measures |
|:---------------:|:-----:|
|Volatility|Treynor Ratio<br />Sharpe Ratio<br />Information Ratio<br />Modigliani Ratio|
|Expected Shortfall (Value at Risk (VaR))|Excess VaR<br />Conditional Sharpe Ratio
|Downside Risk|Sortino Ratio<br />Omega Ratio<br />Kappa Ratio<br />Gain-Loss Ratio<br />Upside Potential Ratio|
|Drawdown Risk|Calmar Ratio<br />Sterling Ratio<br />Burke Ratio|

#### Unsystematic Risk

Unsystematic risk, or that associated to a specific company or industry, can be reduced by diversifying across assets. 

Markowitz's pioneering work on **Modern Portfolio Theory** formalizes and extends diversification, using the variance of asset prices as a proxy for risk.  Its key insight is that an asset's risk and return should not be assessed by itself, but by how it contributes to a portfolio's overall risk and return. In other words, less correlation between pairs of assets would imply less risk of the overall portfolio. 

Improvements on this theory, such as *Post-Modern Portfolio Theory* and *Black–Litterman Model* optimization, help (1) adopt non-normally distributed, asymmetric, and fat-tailed measures of risk, and (2) incorporate relative and absolute 'views' on inputs of risk and returns from, respectively.

#### Systematic Risk

Systematic risk, or that inherent to the entire market or market segment, can be reduced by employing **market-neutral strategies**. For example, in *pairs trading*, we would look for highly historically correlated assets, and when the correlation would temporarily weaken, we short the outperforming stock and long the underperforming one. The weights allocated would be such that the weighted average beta is zero, meaning the portfolio has no market exposure.

## Step #4: Backtesting and Tracking

### Portfolio Evaluation

To evaluate how a portfolio performs, we run regression models that use factors in an attempt to describe the returns of the portfolio with the returns of the market as a whole (i.e. a benchmark/index such as the S&P 500 for the American market, the FTSE 100 for the European market...). 
The *alpha* is the return on an investment that is not a result of the risk-factors in the model (i.e. for CAPM, the general movement in the greater market).

- Capital Asset Pricing Model
- Fama-French Three-Factor Model
- Carhart Four-Factor Model
- Fama-French Five-Factor Model