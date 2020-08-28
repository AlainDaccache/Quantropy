from functools import partial
import portfolio_management.portfolio_simulator as simulator
import fundamental_analysis.accounting_ratios as ratios
import fundamental_analysis.financial_metrics as metrics
import fundamental_analysis.financial_statements_entries as entries


def AQR_Momentum_Strategy():
    '''
    https://www.aqr.com/Insights/Datasets/Momentum-Indices-Monthly

    :return:
    '''
    pass


def LTCM_Delta_Hedging_Strategy():
    '''

    https://www.bauer.uh.edu/rsusmel/7386/ltcm-2.htm#:~:text=LTCM's%20main%20strategy%20was%20to,positions%20in%20the%20rich%20ones.&text=Long%20positions%20in%20emerging%20markets%20sovereigns%2C%20hedged%20back%20to%20dollars.
    :return:
    '''
    pass


def FFCM_Smart_Beta_Strategy():
    '''

    https://www.ishares.com/us/strategies/smart-beta-investing
    :return:
    '''
    pass


def Cigar_Butt_Investment_Strategy():
    '''Benjamin Graham and David Dodd - Security Analysis
    Style: Value Investing
    Graham suggests buying a well-diversified portfolio of stocks considered cheap because their
    Net Current Asset Value exceeds their Market Capitalization.'''
    return simulator.portfolio_simulator(pre_filter=[(partial(metrics.net_current_asset_value, annual=True, ttm=False),
                                                      '>', partial(metrics.market_capitalization))])


def Graham_Defensive_Investor_Strategy():
    '''Benjamin Graham - The Intelligent Investor

    Style: Value Investing

    Investment Goal: Preservation of Principal

    - There should be adequate though not excessive diversification.

        * Between 10 and 30 stocks [we pick 15, optimal].
        * With often more than the upper limit of stocks fit the below criteria, Graham allows the defensive investor to apply his own discretionary judgment as to which stocks to select out of this group.

            * For example, choosing least volatile stocks (as measured by 3-year Beta) [remember, we're Defensive in this strategy].
            * Using Momentum or Value criteria would result in better performance but in sake of the higher volatility.

    - Each company selected should be large and prominent
        * For example, define stock universe to be the S&P 500. All constituents are large and prominent companies.

    - Each company selected should be conservatively financed.
        * Current ratio should be more than 2
        * Debt to Current Asset should be less than 1.10 (or ~ Long-term debt is less than the net current assets)
        * Debt to Equity greater than 50%
        * Good Quality Rating: S&P Earnings and Dividend Rating of B or better (B+ to be on safe side)
                Applying further rules are not necessary. Such rules would be too restrictive and will result in losing good opportunities rather than avoiding bad companies.

    - Each company should have a long record of continuous dividend payments.
        * Uninterrupted payments for at least 20 years.
                Over the years, paying a dividend has become less popular and were substituted in part by repurchasing shares or re-investing in the firm. We require uninterrupted payments for only five years.

    - Each company should have growing and stable earnings
        * Earnings Stability: Positive net earnings figure in any of the last ten years.
                We are less stringent and require only five years with some net earnings in every year.
        * Earnings growth: minimum increase of at least 33% during the last ten years, using three-year averages at the beginning and the end.

    - The investor should impose some limit on the price he will pay for an issue in relation to its average earnings over, say, the past seven years. We suggest that this limit be set at 25 times such average earnings, and not more than 20 times those of the last twelve-month period. But such a restriction would eliminate nearly all the strongest and most popular companies from the portfolio. In particular, it would ban virtually the entire category of “growth stocks,” which have for some years past been the favorites of both speculators and institutional investors. We must give our reasons for proposing so drastic an exclusion.
        * Price to Earnings: current stock price should not be more than 15 times the average earnings of the past three years.
                Given the much lower interest rates these days than in Graham’s day, we relaxed the rule to P/E <= 20.
        * Price to Assets: Graham required that the multiple of P/E (using average earnings for the past three years) and P/B would be less than 22.5. This rule is interchangeable with the previous rule (OR function between them). We have relaxed it to P/E * P/B<= 30.

    Hold stocks until 50% return and then liquidate (or up to 2 years from initial investment, whichever comes first)
    Follow strategy for more than 5 years
    '''
    size = (partial(entries.net_sales, annual=True, ttm=True), '>', 100000000)
    pass


def Graham_Enterprising_Investor_Strategy():
    '''Benjamin Graham - The Intelligent Investor
    Style: Value Investing
    Investment Goal: Maximization of Investment Returns
    '''
    pass


def Graham_Net_Net_Strategy():
    '''Benjamin Graham - The Intelligent Investor
    Style: Value Investing
    '''
    pass


def Magic_Formula_Investing():
    '''Joel Greenblatt - The Little Book That Beats the Market
    - Establish a minimum market capitalization (usually greater than $50 million).
    - Exclude utility and financial stocks.
    - Exclude foreign companies (American Depositary Receipts).
    - Determine company's earnings yield = EBIT / enterprise value [valuation factor]
    - Determine company's return on capital = EBIT / (net fixed assets + working capital) [quality factor]
    - Rank all companies above chosen market capitalization by highest earnings yield and highest return on capital (ranked as percentages).
    - Invest in 20–30 highest ranked companies, accumulating 2–3 positions per month over a 12-month period.
    - Re-balance portfolio once per year, selling losers one week before the year-mark and winners one week after the year mark.
    - Continue over a long-term (5–10+ year) period.
    '''
    pass


def Cornerstone_Growth_Approach():
    '''
    James O'Shaughnessy - What Works on Wall Street
    Style: Growth Investing
    :return:
    '''
    pass


def Traditional_Defensive_Investing():
    '''A defensive investment strategy entails
     - regular portfolio rebalancing to maintain one's intended asset allocation;
     - buying high-quality, short-maturity bonds and blue-chip stocks;
     - diversifying across both sectors and countries;
     - placing stop loss orders; and holding cash and cash equivalents in down markets'''
    pass
