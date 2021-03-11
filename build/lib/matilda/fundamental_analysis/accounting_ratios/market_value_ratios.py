from datetime import timedelta
from matilda.fundamental_analysis.supporting_metrics import *
from matilda.fundamental_analysis.financial_statements import *
from matilda.data_pipeline.db_crud import read_market_price

'''
Market value ratios are used to evaluate the share price of a company’s stock.
'''


def dividend_payout_ratio(stock, date=None, lookback_period=timedelta(days=0),
                          period='', deduct_preferred_dividends=True, use_augmented_ratio=False):
    """
    The dividend payout ratio is the fraction of net income a firm pays to its stockholders in dividends.
    The part of earnings not paid to investors is *retained* i.e. left for investment to provide for future earnings growth.
    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param deduct_preferred_dividends:
    :param use_augmented_ratio: Some companies choose stock buybacks as an alternative to dividends; in such cases this ratio becomes less meaningful.
    The augmented ratio adds *Buybacks* to the Dividends in the numerator.
    :return: .. math:: \\text{Dividend Payout Ratio} = \\frac{\\text{Dividends}}{\\text{Net Income}}
    """
    dividends = payments_of_dividends(stock=stock, date=date, lookback_period=lookback_period, period=period)
    dividends -= abs(preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                         period=period)) if deduct_preferred_dividends else 0
    net_income_ = net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    return dividends / net_income_


def retention_ratio(stock, date=None, lookback_period=timedelta(days=0), period='FY',
                    deduct_preferred_dividends=True, use_augmented_ratio=False):
    """
    The **retention ratio** indicates the percentage of a company's earnings that are not paid out in dividends but
    credited to retained earnings. It is the opposite of the dividend payout ratio

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param deduct_preferred_dividends:
    :param use_augmented_ratio: Some companies choose stock buybacks as an alternative to dividends; in such cases this ratio becomes less meaningful.
        The augmented ratio adds *Buybacks* to the Dividends in the numerator.
    :return: .. math:: \\text{Retention Ratio} = 1 - \\text{Dividend Payout Ratio} = \\frac{\\text{Retained Earnings}}{\\text{Net Income}}
    """
    return 1 - dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                     deduct_preferred_dividends=deduct_preferred_dividends,
                                     use_augmented_ratio=use_augmented_ratio)


def dividend_coverage_ratio(stock, date=None, lookback_period=timedelta(days=0),
                            period='', deduct_preferred_dividends=True,
                            use_augmented_ratio=False):
    """
    The **dividend coverage ratio** is the ratio of company's earnings (net income) over the dividend paid to shareholders, calculated as net profit or loss attributable to ordinary shareholders by total ordinary dividend.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param use_augmented_ratio:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Dividend Coverage Ratio} = \\frac{\\text{Net Income}}{\\text{Dividends}}
    """
    return 1 / dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                     deduct_preferred_dividends=deduct_preferred_dividends,
                                     use_augmented_ratio=use_augmented_ratio)


def dividend_yield(stock, date=None, lookback_period=timedelta(days=0), period='TTM',
                   diluted_shares=False):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations. use diluted shares in the computations.
    :return: .. math:: \\text{Dividend Yield} = \\frac{\\text{Dividend-per-share}}{\\text{Share Price}}
    """
    return dividend_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                              diluted_shares=diluted_shares) \
           / read_market_price(stock=stock, date=date, lookback_period=lookback_period)


def earnings_per_share(stock, date=None, lookback_period=timedelta(days=0),
                       period='TTM', diluted_shares=False, use_income_from_operations=False,
                       deduct_preferred_dividends=True, weighted_average_shares=True,
                       as_reported=True):
    '''
    The earnings per share ratio measures the amount of net income earned for each share outstanding

    *Category:* Market Value Ratios
    *Subcategory:* Equity Value Ratios

    *Notes:* Compared with Earnings per share, a company's cash flow is better indicator of the company's earnings power.
    If a company's earnings per share is less than cash flow per share over long term, investors need to be cautious and find out why.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param as_reported: outputs the EPS as reported by the company in the 10-K or 10-Q filing.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations: Use income from continuing operations instead of Net Income in the numerator.
    :param deduct_preferred_dividends:
    :param weighted_average_shares:  It is more accurate to use a weighted average number of common shares over the reporting term because the number of shares can change over ti
    :return: .. math:: \\text{Earnings Per Share} = \\frac{\\text{Net Income}}{\\text{Total Shares Outstanding}}
    '''
    numerator = net_income(stock=stock, date=date, lookback_period=lookback_period, period=period)
    numerator -= abs(preferred_dividends(stock=stock, date=date, lookback_period=lookback_period,
                                         period=period)) if deduct_preferred_dividends else 0
    numerator += non_operating_income(stock=stock, date=date, lookback_period=lookback_period,
                                      period=period) if use_income_from_operations else 0

    shares_outstanding_ = total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                   period=period, diluted_shares=diluted_shares)
    return numerator / shares_outstanding_


def book_value_per_share(stock, date=None, lookback_period=timedelta(days=0), period='Q', diluted_shares=False,
                         tangible=False):
    '''
    The book value per share ratio calculates the per-share value of a company based on equity available to shareholders

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param tangible:
    :return: .. math:: \\text{Book Value Per Share} = \\frac{\\text{Shareholder's Equity}}{\\text{Total Shares Outstanding}}
    '''
    numerator = total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    if tangible:
        numerator = - total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period, period=period)

    return numerator / total_shares_outstanding(stock=stock, date=date, lookback_period=lookback_period,
                                                period=period, diluted_shares=diluted_shares)


def price_to_cash_flow_ratio(stock, date=None, lookback_period=timedelta(days=0), period='TTM', diluted_shares=False):
    """
    The **price/cash flow ratio** (or P/CF) is used to compare a company's market value to its cash flow; or, equivalently,
    divide the per-share stock price by the per-share operating cash flow.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:* A high P/CF ratio indicated that the specific firm is trading at a high price but is not generating enough
    cash flows to support the multiple—sometimes this is OK, depending on the firm, industry, and its specific operations.
    Smaller price ratios are generally preferred, as they may reveal a firm generating ample cash flows that are not yet
    properly considered in the current share price. Holding all factors constant, from an investment perspective, a smaller P/CF is preferred over a larger multiple

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Price-to-Cash Flow Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Operating Cash Flow}} =
    \\frac{\\text{Share Price}}{\\text{Operating Cash Flow per Share}}
    """
    return market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) \
           / cash_flow_operating_activities(stock=stock, date=date, lookback_period=lookback_period, period=period)


def price_to_book_ratio(stock, date=None, lookback_period=timedelta(days=0), period='Q',
                        diluted_shares=False, tangible_book_value=False):
    """
    The price-to-book ratio (or P/B ratio) is used to compare a company's current market capitalization to its book value;
    or, equivalently, divide the per-share stock price by the per-share book value.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*
        *   A higher P/B ratio implies that investors expect management to create more value from a given set of
            assets, all else equal (and/or that the market value of the firm's assets is significantly higher than their accounting
            value). P/B ratios do not, however, directly provide any information on the ability of the firm to generate profits
            or cash for shareholders.

        *   As with most ratios, it varies a fair amount by industry. Industries that require more infrastructure capital
            (for each dollar of profit) will usually trade at P/B ratios much lower than, for example, consulting firms. P/B
            ratios are commonly used to compare banks, because most assets and liabilities of banks are constantly valued at
            market values.

        *   This ratio also gives some idea of whether an investor is paying too much for what would be left if the company
            went bankrupt immediately. For companies in distress, the book value is usually calculated without the intangible
            assets that would have no resale value. In such cases, P/B should also be calculated on a "diluted" basis, because
            stock options may well vest on sale of the company or change of control or firing of management.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param tangible_book_value: P/B can be calculated either including or excluding intangible assets and goodwill. When intangible assets and goodwill are excluded,
        the ratio is often specified to be "price to tangible book value"
    :return: .. math:: \\text{Price-to-Book Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Book Value}} = \\frac{\\text{Share Price}}{\\text{Book Value per Share}}
    """
    denominator = total_shareholders_equity(stock=stock, date=date, lookback_period=lookback_period, period=period)
    if tangible_book_value:
        denominator -= total_intangible_assets(stock=stock, date=date, lookback_period=lookback_period,
                                               period=period)
    return market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) / denominator


def price_to_sales(stock, date=None, lookback_period=timedelta(days=0), period='TTM',
                   diluted_shares=False):
    """
    Price–sales ratio (or P/S ratio, or PSR) is used to compare a company's current market capitalization and the revenue in
    the most recent year; or, equivalently, divide the per-share stock price by the per-share revenue.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations. use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Price-to-Sales Ratio} = \\frac{\\text{Market Capitalization}}{\\text{Revenue}} = \\frac{\\text{Share Price}}{\\text{Per-Share Revenue}}
    """
    return market_capitalization(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares) \
           / net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def justified_price_to_sales(stock, date=None, lookback_period=timedelta(days=0), period='TTM',
                             diluted_shares=False):
    """
    The justified P/S ratio is calculated as the price-to-sales ratio based on the Gordon Growth Model.
    Thus, it is the price-to-sales ratio based on the company's fundamentals rather than .
    Here, *g* is the sustainable growth rate as defined below and *r* is the required rate of return.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :return: .. math:: \\text{Justified P/S} = \\text{Profit Margin} * \\text{Payout} * \\frac{1+g}{r-g} where .. math:: g = \\text{Retention Ratio} * \\text{Net Profit Margin} * \\frac{\\text{Sales}}{\\text{Assets}} * \\frac{\\text{Assets}}{\\text{Shareholders' Equity}}
    """
    # g = growth_rate_PRAT_model(stock=stock, date=date, lookback_period=lookback_period, period=period)
    # r = weighted_average_cost_of_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)
    # return net_profit_margin(stock=stock, date=date, lookback_period=lookback_period, period=period) \
    #        * dividend_payout_ratio(stock=stock, date=date, lookback_period=lookback_period, period=period) \
    #        * (1 + g) / (r - g)
    pass


def price_to_earnings(stock, date=None, lookback_period=timedelta(days=0),
                      period='TTM', diluted_shares=False,
                      use_income_from_operations=False, deduct_preferred_dividends=True):
    """
    The price-earnings ratio compares a company’s share price to its earnings per share

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Price-earnings ratio} = \\frac{\\text{Share Price}}{\\text{Earnings Per Share}}
    """
    market_price_ = read_market_price(stock=stock, date=date, lookback_period=lookback_period)
    earnings_per_share_ = earnings_per_share(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                             diluted_shares=diluted_shares,
                                             use_income_from_operations=use_income_from_operations,
                                             deduct_preferred_dividends=deduct_preferred_dividends)
    return market_price_ / earnings_per_share_


def earnings_yield(stock, date=None, lookback_period=timedelta(days=0),
                   period='', diluted_shares=False,
                   use_income_from_operations=False, deduct_preferred_dividends=True):
    """
    The **earnings yield** is the inverse of price to earnings.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{Earnings Yield} = \\frac{\\text{Earnings Per Share}}{\\text{Share Price}}
    """
    return 1 / price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
                                 diluted_shares=diluted_shares, use_income_from_operations=use_income_from_operations,
                                 deduct_preferred_dividends=deduct_preferred_dividends)


def greenblatt_earnings_yield(stock, date=None, lookback_period=timedelta(days=0), period='FY'):
    """

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return: .. math:: \\text{Greenblatt Earnings Yield} = \\frac{\\text{EBIT}}{\\text{EV}}
    """

    return earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period)


def price_to_earnings_to_growth(stock, date=None, lookback_period=timedelta(days=0),
                                period='TTM', growth_periods: int = 5, diluted_shares=False,
                                use_income_from_operations=False, deduct_preferred_dividends=True):
    """
    The price/earnings to growth ratio (or PEG ratio) is a valuation metric for determining the relative trade-off
    between the price of a stock, the earnings generated per share (EPS), and the company's expected growth.

    *Category:* Market Value Ratios

    *Subcategory:* Equity Value Ratios

    *Notes:*
        *   In general, the P/E ratio is higher for a company with a higher growth rate. Thus, using just the P/E ratio
            would make high-growth companies appear overvalued relative to others. It is assumed that by dividing the P/E
            ratio by the earnings growth rate, the resulting ratio is better for comparing companies with different growth
            rates. Therefore, a lower ratio is "better" (cheaper) and a higher ratio is "worse" (expensive).

        *   According to Peter Lynch in his book *One Up on Wall Street*, the P/E ratio of any company that's fairly
            priced will equal its growth rate", i.e., a fairly valued company will have its PEG equal to 1.

        *   The P/E ratio used in the calculation may be projected or trailing. The (annual) growth rate is expressed as
            a percent value, and should use real growth only, to correct for inflation. It may be the
            expected growth rate for the next year or the next five years.

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :param growth_periods:
    :param diluted_shares: use diluted shares instead of basic in calculations.
    :param use_income_from_operations:
    :param deduct_preferred_dividends:
    :return: .. math:: \\text{} = \\frac{\\text{}}{\\text{}}
    """
    # lookbacks = [timedelta(days=365 * i if period != 'Q' else 90 * i) for i in range(growth_periods)]
    # eps_series = [earnings_per_share(stock=stock, date=date, lookback_period=lookback, period=period,
    #                                  diluted_shares=diluted_shares,
    #                                  use_income_from_operations=use_income_from_operations,
    #                                  deduct_preferred_dividends=deduct_preferred_dividends) for lookback in lookbacks]
    # eps = FundamentalMetricsHelpers(stock=stock, date=date, metric=partial(earnings_per_share))
    # eps_growth = eps.mean_metric_growth_rate()
    # output = price_to_earnings(stock=stock, date=date, lookback_period=lookback_period, period=period,
    #                            diluted_shares=diluted_shares,
    #                            use_income_from_operations=use_income_from_operations,
    #                            deduct_preferred_dividends=deduct_preferred_dividends) / eps_growth
    # return output
    pass


'''Enterprise Value Ratios'''


def enterprise_value_to_revenue(stock, date=None, lookback_period=timedelta(days=0), period='TTM'):
    """
    The enterprise value-to-revenue multiple is a measure of the value of a stock that compares a company's enterprise value to its revenue.
    It is often used to determine a company's valuation in the case of a potential acquisition, and can be used for
    companies that do not generate income or profits.

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / net_sales(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_ebitda(stock, date=None, lookback_period=timedelta(days=0), period='TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / earnings_before_interest_and_taxes_and_depreciation_and_amortization(stock=stock, date=date,
                                                                                  lookback_period=lookback_period,
                                                                                  period=period)


def enterprise_value_to_ebit(stock, date=None, lookback_period=timedelta(days=0), period='TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / earnings_before_interest_and_taxes(stock=stock, date=date, lookback_period=lookback_period,
                                                period=period)


def enterprise_value_to_invested_capital(stock, date=None, lookback_period=timedelta(days=0),
                                         period='TTM'):
    """

    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / invested_capital(stock=stock, date=date, lookback_period=lookback_period, period=period)


def enterprise_value_to_free_cash_flow(stock, date=None, lookback_period=timedelta(days=0),
                                       period='TTM'):
    """
    *Category:* Enterprise Value Ratios

    *Subcategory:* Equity Value Ratios

    :param stock: ticker(s) in question. Can be a string (i.e. 'AAPL') or a list of strings (i.e. ['AAPL', 'BA']).
    :param date: Can be a datetime (i.e. datetime(2019, 1, 1)) or list of datetimes. The most recent date of reporting from that date will be used. By default, date=None.
    :param lookback_period: lookback from date (used to compare against previous year or quarter etc.) i.e. timedelta(days=90).
    :param period: 'FY' for fiscal year, 'Q' for quarter, 'YTD' for calendar year to date, 'TTM' for trailing twelve months.
    :return:
    """
    return enterprise_value(stock=stock, date=date, lookback_period=lookback_period, period=period) \
           / free_cash_flow(stock=stock, date=date, lookback_period=lookback_period, period=period)
