# MAtilDA Overview

There are many other asset classes to consider, including bonds, real estate, commodities...

## Step #1: Data Scraping

Relevant historical data points are collected

- **Basic Stock Information**: ticker, name, cik, industry, sector, exchange traded in...
- **Financial Statements**: we scrape and normalize the main financial statements (Balance Sheet, Income Statement, Cash Flow Statement) from companies 10-K (yearly) and 10-Q (quarterly) filings using the SEC Archives, for **up to the last 20 years**. 
- **Price Action**: we scrape the open, high, low, close (adjusted) of the price, and trading volumes (for daily, monthly and yearly timeframes) from Yahoo Finance
- **Misc**: insider trading reports (SEC Form 4), Gross National Product price index levels, risk-free rates...

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

#### Technical Indicators

Notice some indicators fit into more than one category. There are many, many, many others, but the followin are the **most** widely used:
- **Trend Indicators:** Moving Averages (MA) (Simple, Smoothed, Exponential, Double Exponential, Kaufman's Adaptive), Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Bollinger Bands®, Parabolic SAR, On-Balance Volume (OBV)
- **Momentum Oscillators:** Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Stochastic Oscillator
- **Volume Indicators**: On-Balance Volume (OBV), Chaikin Money Flow, and Klinger Volume Oscillator
- **Volatility Indicators:** Volatility Index (VIX), Average True Range (ATR), and Bollinger Bands®

## Step #3 Portfolio Construction

### Stock Selection Strategies
Here, we filter stocks that fulfill criteria based on fundamental and technical analysis techniques gathered and computed above. This includes financial statements entries, price action, accounting ratios, scoring/ranking systems... 

Strategies either use values as **absolute** (i.e. a good Current Ratio is agreed to be between 1.2 to 2, a good Price to Earnings Ratio < 4th decile in the industry segment etc.) or **relative** (i.e. total debt less than book value, stability of growth of earnings...). Many investment philosophies arose, mainly:

| Investing Style     | Common Metrics Used   | Popular Strategies / Investors / Funds |
|:--------------------:|:--------------------- |:--------------------------------------:|
| Value Investing      | Price-to-Earnings<br />Price-to-Sales<br />Price-to-Book<br />Debt-to-Equity<br /> Price-to-Free Cash Flow<br /><br />|                                        |
| Growth Investing     |Net Profit Margin<br />Sales Growth<br />Earnings Growth<br />Free Cash Flow Growth<br />                                       |
| GARP Investing       |Price-to-Earnings-to-Growth<br />|                                        |
| Momentum Investing   |                |                                        |  
| Income Investing     |Dividend Yield<br />Payout Ratio<br />Dividend Growth<br />|                                        |


Enterprising vs Defensive Investor Criteria (Benjamin Graham, in *The Intelligent Investor*), Magic Formula Investing (Joel Greenblatt, in *The Little Book that Beats the Market*)
- **Growth Investing**: CAN SLIM (William J. O'Neil, in *How to Make Money in Stocks: A Winning System In Good Times or Bad*)
- **Growth At A Reasonable Price (GARP)**: Lynch Fair Value (Peter Lynch, in *One Up on Wall Street* and *Learn to Earn*)
- **Momentum Investing**:
- **Income Investing**:     

Definitely, the option to create your custom stock screener is available

### Portfolio Allocation
- Diversification: among assets, among asset classes, among strategies.

## Step #4: Evaluation and Tracking

### Backtesting
