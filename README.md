# MAtilDA

(TODO): There are many other asset classes to consider, including bonds, real estate, commodities...

## Step #1: Data Scraping

### Financial Statements Scraping
Here, we scrape and normalize the main financial statements (balance sheet, income statement, cash flow statement) from company 10-K (yearly) and 10-Q (quarterly) filings using the SEC Archives.

### Price Action Scraping
Daily, monthly and yearly open, high, low, (adjusted) close, and trading valumes are scraped from Yahoo Finance

### Miscellaneous
Other relevant historical data points to collect are insider trading reports (SEC Form 4), Gross National Product price index levels, risk-free rates...

## Step #2: Company Analysis
In this section, we take the numerical values from the financial statements in order to analyse the companies behind those stocks.

### Financial Ratios
Financial ratios are used in order to assess a company's performance, typically to track their changes in value over time and to compare them with those of competitors in the industry.

- **Liquidity ratios:** Current Ratio, Acid-Test Ratio, Cash Ratio, Operating Cash Flow Ratio
- **Leverage ratios:** Debt Ratio, Debt to Equity Ratio, Interest Coverage Ratio, Debt Service Coverage Ratio
- **Efficiency ratios:** Asset Turnover Ratio, Inventory Turnover Ratio, Receivables Turnover Ratio, Days Sales in Inventory Ratio
- **Profitability ratios:** Gross Margin Ratio, Operating Margin Ratio, Return on Assets Ratio, Return on Equity Ratio
- **Market value ratios:** Book Value per Share Ratio, Dividend Yield Ratio, Earnings per Share Ratio, Price to Earnings Ratio

### Valuation Methods
There are two main categories when estimating the value of a business
- **Breakup Value**
- **Going Concern Value:** Discounted Cash Flow Analysis, Comparable Company Analysis, Precedent Transactions

### Scoring Systems
A plethora of financial models use financial ratios in order to identify whether companies are experiencing financial distress, manipulating their earnings... 
- **Financial Health Scores:** Piotroski's F-Score, Altman's Z-Score, Ohlson's O-Score
- **Earnings Manipulation Scores**: Beneish's M-Score, Montier's C-Score, Nichols O-Score
- **Misc**: Zacks Rank (uses earnings estimates and their revisions)

## Step #3 Portfolio Construction

### Stock Selection Strategies
Here, we filter stocks that fulfill criteria based on fundamental and technical analysis techniques gathered and computed above. This includes financial statements entries, price action, accounting ratios, scoring/ranking systems... 

Strategies either use values as **absolute** (i.e. a good Current Ratio is agreed to be between 1.2 to 2, a good Price to Earnings Ratio < 4th decile in the industry segment etc.) or **relative** (i.e. total debt less than book value, stability of growth of earnings...). Many investment philosophies arose, mainly:

- **Value Investing**: Enterprising vs Defensive Investor Criteria (Benjamin Graham, in *The Intelligent Investor*), Magic Formula Investing (Joel Greenblatt, in *The Little Book that Beats the Market*)
- **Growth Investing**: CANSLIM (William J. O'Neil, from *Investor's Business Daily*)
- **Momentum Investing**:
- **Income Investing**:

Definitely, the option to create your custom stock screener is available

### Portfolio Allocation
- Diversification: among assets, among asset classes, among strategies.

## Step #5: Backtesting and Tracking
