# MAtilDA Overview
This project is the culmination of three years of learning about the financial markets, and a year of (on/off) developing a platform in order to provide a comprehensive and unified approach to trading the financial markets
Hearing about the recent tragic events surrounding the Robinhood platform and general (mis/dis)information in the trading world, we should all try to 


This incident could have been avoided, so let us try our best to NOT LET THIS HAPPEN AGAIN.
From now on, we as a community should be held accountable

This especially goes to the people that are getting into the hype train after the recent surge in the market, to the people with less stable jobs trying to make extra income, or the people trying to beat boredom during stay-at-home orders. 

And going online welcomes us with a learning barrier; one with misinformation and disinformation. One with either oversimplified or overly complex articles, one with websites trying to sell to us.

And most likely, you will be led to the lauded Robinhood accounts (because they're commission-free), 
penny stocks (because they're cheap), and options trading (because of the risk profile flexibility). 
Uninformed r/wallstreetbets advice (ref. "The Infinite Money Cheat Code")
But to each its catch. Catches that, especially if combined together, are recipe for disaster


Times are very unpredictable, the markets are volatile, opinions are mixed, and whichever the outcome, proponents of the right side will be lauded as Oracles, having credentials to predict the next stock market crash or boom. 
So do not listen to anyone (which means don't listen to me either but oh well), the best thing I personally recommend is to watch 



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

Notice some indicators fit into more than one category. There are many, many others, but the following are the **most** widely used:
- **Trend Indicators:** Moving Averages (MA) (Simple, Smoothed, Exponential, Double Exponential, Kaufman's Adaptive), Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Bollinger Bands®, Parabolic SAR, On-Balance Volume (OBV)
- **Momentum Oscillators:** Moving Average Convergence Divergence (MACD), Ichimoku Kinko Hyo, Relative Strength Index (RSI), Average Directional Index (ADX), Stochastic Oscillator
- **Volume Indicators**: On-Balance Volume (OBV), Chaikin Money Flow, and Klinger Volume Oscillator
- **Volatility Indicators:** Volatility Index (VIX), Average True Range (ATR), and Bollinger Bands®

## Step #3 Portfolio Construction

### Stock Selection Strategies
Here, we filter stocks that fulfill criteria based on fundamental and technical analysis techniques gathered and computed above. This includes financial statements entries, price action, accounting ratios, scoring/ranking systems... 

Strategies either use values as **absolute** (i.e. a good Current Ratio is agreed to be between 1.2 to 2) or **relative** (i.e. total debt less than book value, a Price to Earnings Ratio < 4th decile in the industry segment etc., stability of growth of earnings...). Many investment philosophies arose depending on people's objectives, risk profile, and views on the market (I highly recommend reading about the [Efficient Market Hypothesis](https://en.wikipedia.org/wiki/Efficient-market_hypothesis), mainly:

| Investing Style     | Common Metrics Used   | Popular Strategies / Investors / Funds |
|:--------------------:|:--------------------- |:--------------------------------------:|
| Value Investing      | Price-to-Earnings<br />Price-to-Sales<br />Price-to-Book<br />Debt-to-Equity<br /> Price-to-Free Cash Flow|Enterprising vs Defensive Investor Criteria (Benjamin Graham, in *The Intelligent Investor*)<br />Magic Formula Investing (Joel Greenblatt, in *The Little Book that Beats the Market*)                                        |
| Growth Investing     |Net Profit Margin<br />Sales Growth<br />Earnings Growth<br />Free Cash Flow Growth|CAN SLIM (William J. O'Neil, in *How to Make Money in Stocks: A Winning System In Good Times or Bad*)                                      |
| GARP Investing (Hybrid)       |Price-to-Earnings-to-Growth|Lynch Fair Value (Peter Lynch, in *One Up on Wall Street* and *Learn to Earn*)                                     |
| Momentum Investing   |                |                                        |  
| Income Investing     |Dividend Yield<br />Payout Ratio<br />Dividend Growth<br />|                                        |

Definitely, the option to create your custom stock screener is available

### Portfolio Allocation
- Diversification: among assets, among asset classes, among strategies.

## Step #4: Evaluation and Tracking

### Portfolio Evaluation

To evaluate how a portfolio performs, we run regression models that use variables in an attempt to describe the returns of the portfolio with the returns of the market as a whole (i.e. a benchmark/index such as the S&P 500 for the American market, the FTSE 100 for the European market...). 
The 'alpha' is the return on an investment that is not a result of the risk-factors in the model (i.e. for CAPM, the general movement in the greater market).

- Capital Asset Pricing Model
- Fama-French Three-Factor Model
- Carhart Four-Factor Model
- Fama-French Five-Factor Model


### Backtesting
