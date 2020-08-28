# https://en.wikipedia.org/wiki/Wiener_process
# https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model
# https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation
# https://en.wikipedia.org/wiki/Implied_volatility

from datetime import datetime, timedelta
import numpy as np
import scipy.stats as si
from fundamental_analysis import financial_statements_entries as fi
from fundamental_analysis import financial_metrics as me
from fundamental_analysis import macroeconomic_factors as macro
from options_scraper.scraper import NASDAQOptionsScraper
from options_scraper.utils import batched


def black_scholes_model_non_dividend_paying(spot_price, strike_price, time_to_maturity, interest_rate,
                                            volatility, option='call'):
    d1 = (np.log(spot_price / strike_price)
          + (interest_rate + 0.5 * volatility ** 2) * time_to_maturity) \
         / (volatility * np.sqrt(time_to_maturity))
    d2 = (np.log(spot_price / strike_price)
          + (interest_rate - 0.5 * volatility ** 2) * time_to_maturity) \
         / (volatility * np.sqrt(time_to_maturity))

    if option == 'call':
        return (spot_price * si.norm.cdf(d1, 0.0, 1.0)
                - strike_price * np.exp(-interest_rate * time_to_maturity) * si.norm.cdf(d2, 0.0, 1.0))
    elif option == 'put':
        return (strike_price * np.exp(-interest_rate * time_to_maturity) * si.norm.cdf(-d2, 0.0, 1.0)
                - spot_price * si.norm.cdf(-d1, 0.0, 1.0))
    else:
        return Exception


def black_scholes_model_dividend_paying(spot_price, strike_price, time_to_maturity, interest_rate, volatility,
                                        dividend_rate, option='call'):
    d1 = (np.log(spot_price / strike_price)
          + (interest_rate - dividend_rate + 0.5 * volatility ** 2) * time_to_maturity) \
         / (volatility * np.sqrt(time_to_maturity))
    d2 = (np.log(spot_price / strike_price)
          + (interest_rate - dividend_rate - 0.5 * volatility ** 2) * time_to_maturity) \
         / (volatility * np.sqrt(time_to_maturity))

    if option == 'call':
        return (spot_price * np.exp(-dividend_rate * time_to_maturity) * si.norm.cdf(d1, 0.0, 1.0)
                - strike_price * np.exp(-interest_rate * time_to_maturity) * si.norm.cdf(d2, 0.0, 1.0))
    elif option == 'put':
        return (strike_price * np.exp(-interest_rate * time_to_maturity) * si.norm.cdf(-d2, 0.0, 1.0)
                - spot_price * np.exp(-dividend_rate * time_to_maturity) * si.norm.cdf(-d1, 0.0, 1.0))
    else:
        return Exception


def black_scholes_wrapper(stock, date=datetime.now(), lookback_period=timedelta(days=0), annual=True, ttm=True,
                          diluted=True, option='call'):
    spot_price = me.market_price(stock=stock, date=date, lookback_period=lookback_period)
    strike_price = 0
    time_to_maturity = 0
    interest_rate = macro.cumulative_risk_free_rate(from_date=date - lookback_period - timedelta(days=365),
                                                    to_date=date - lookback_period)
    volatility = 0
    # if the stock doesn't pay dividends
    if not np.isnan(
            fi.payments_for_dividends(stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)):
        return black_scholes_model_non_dividend_paying(spot_price=spot_price, strike_price=strike_price,
                                                       time_to_maturity=time_to_maturity, interest_rate=interest_rate,
                                                       volatility=volatility, option=option)
    else:
        dividend_rate = 0
        return black_scholes_model_dividend_paying(spot_price=spot_price, strike_price=strike_price,
                                                   time_to_maturity=time_to_maturity, interest_rate=interest_rate,
                                                   volatility=volatility, dividend_rate=dividend_rate, option=option)
