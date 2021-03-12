import json
import os
import pickle
from datetime import date, datetime, timedelta
import typing
import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import re
import pandas as pd

from matilda import config


class StockPriceScraper:

    def __init__(self, ticker, period='1mo', from_date=None, to_date=None, frequency='1d'):
        """
        For the illusion of real-time, call it with period='min'

        :param ticker: can be string (i.e. 'AAPL') or list of strings (i.e. ['AAPL', 'FB', 'MSFT']).
        :param period:  use instead of from_date and to_date. This is different than frequency. Period just says take date from now to `period`
                        time ago. Valid periods: min,1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,YTD,max.
                        By default, '1mo'. (NB: 'min' stands for minimum, not minute)
        :param from_date: if not selected, will use the default value of period
        :param to_date: if not selected, will use datetime.now()
        :param frequency:   specifies the time interval between two consecutive data points in the time series.
                            can be in ['1s', '5s', '15s', '30s', '1min', '5min', '15min', '30min',
                            '1h', '4h', '1d', '1w', '1mo', '1y'] according to implementation.
                            i.e. it can't be lower than the minimum frequency of the implementation.
        :return:
        """
        self.frequency_hierarchy = ['1s', '5s', '15s', '30s', '1min', '5min', '15min', '30min',
                                    '1h', '4h', '1d', '1w', '1mo', '1y']

        lookback_period_mapper = {'1d': timedelta(days=1), '5d': timedelta(days=5),
                                  '1mo': timedelta(days=30), '3M': timedelta(days=92),
                                  '6M': timedelta(days=183), '1Y': timedelta(days=365),
                                  '2Y': timedelta(days=730), '5Y': timedelta(days=1826),
                                  '10Y': timedelta(days=3652)}

        if frequency not in self.frequency_hierarchy:
            raise Exception('Invalid frequency')
        self.frequency = frequency

        if isinstance(ticker, str):
            self.ticker = [ticker]
        elif isinstance(ticker, list):
            self.ticker = ticker
        else:
            raise Exception('Invalid ticker type')

        if to_date is None:
            to_date = datetime.now()
        self.to_date = to_date

        if from_date is None:
            if period == 'YTD':
                from_date = datetime(year=to_date.year, month=1, day=1)
            elif period == 'max':
                from_date = date.min
            elif period == 'min':
                from_date = to_date
            else:
                from_date = to_date - lookback_period_mapper[period]

        self.from_date = from_date

    def convert_format(self, format):
        """

        :param format: 'dict', 'json', 'pandas'
        :return:
        """
        output = {}
        for date, open_, high, low, close, volume in zip(self.Dates, self.Open, self.High,
                                                         self.Low, self.Close, self.Volume):
            output[date] = {'Open': open_, 'High': high, 'Low': low, 'Close': close, 'Volume': volume}

        if re.match('dict', format, re.IGNORECASE):
            return output
        elif re.match('json', format, re.IGNORECASE):
            return json.dumps(output)
        elif re.match('pandas', format, re.IGNORECASE):
            return pd.DataFrame.from_dict(output, orient='index')
        else:
            raise Exception('Please input a valid `format`')


class AlphaVantage(StockPriceScraper):

    def __init__(self, ticker, period='1mo', from_date=None, to_date=datetime.now(), frequency='1d'):
        # TODO not supporting ticker lists yet
        super().__init__(ticker, period, from_date, to_date, frequency)
        intraday_frequency_mapper = {'1min': '1min', '5min': '5min', '15min': '15min', '30min': '30min', '1h': '60min'}
        ts = TimeSeries(config.ALPHAVANTAGE_API_KEY)

        df_cols = {'1. open': 'Open', '2. high': 'High', '3. low': 'Low',
                   '4. close': 'Close', '5. volume': 'Volume'}
        to_resample = False
        if self.frequency_hierarchy.index(frequency) < self.frequency_hierarchy.index('1min'):
            raise Exception("AlphaVantage can't support an interval lower than 1 minute")

        elif frequency in intraday_frequency_mapper.keys():  # AlphaVantage has a function to get intraday
            data, meta_data = ts.get_intraday(symbol=ticker, interval=intraday_frequency_mapper[frequency],
                                              outputsize='full')

        else:
            if frequency == '1d':  # AlphaVantage has another function to get daily
                data, meta_data = ts.get_daily_adjusted(symbol=ticker)
                df_cols = {'1. open': 'Open', '2. high': 'High', '3. low': 'Low',
                           '5. adjusted close': 'Close', '6. volume': 'Volume'}
            else:  # not supported, but can resample
                data, meta_data = ts.get_intraday(symbol=ticker, interval='60min', outputsize='full')
                to_resample = True

        df = pd.DataFrame.from_dict(data=data, orient='index')
        df.index = pd.to_datetime(df.index)
        if to_resample:
            df = df.resample(frequency).first().dropna(how='all')

        df = df[(df.index >= self.from_date) & (df.index <= self.to_date)]
        df = df.rename(columns=df_cols)
        df = df.iloc[::-1]  # AlphaVantage returns dates in reverse chronological order, so should reverse
        # with open('temp_prices.pkl', 'wb') as handle:
        #     pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # with open('temp_prices.pkl', 'rb') as handle:
        #     data = pickle.load(handle)

        self.Open, self.High, self.Low = df['Open'], df['High'], df['Low']
        self.Close, self.Volume, self.Dates = df['Close'], df['Volume'], df.index.to_list()


class YahooFinance(StockPriceScraper):

    def __init__(self, ticker, from_date=None, to_date=datetime.now(), period='1mo', frequency='1d'):
        super().__init__(ticker, period, from_date, to_date, frequency)
        if isinstance(ticker, typing.List):
            ticker = [stk.replace('.', '-') for stk in ticker]
        else:
            ticker = ticker.replace('.', '-')

        if self.frequency_hierarchy.index(frequency) < self.frequency_hierarchy.index('1min'):
            raise Exception("YahooFinance can't support an interval lower than 1 minute")

        resp = yf.Ticker(ticker).history(from_date=self.from_date, to_date=self.to_date,
                                         period=period, interval=frequency)
        self.Open = resp['Open']
        self.High = resp['High']
        self.Low = resp['Low']
        self.Close = resp['Close']
        self.Volume = resp['Volume']
        self.Dates = resp.index


class GoogleFinance(StockPriceScraper):
    def __init__(self, ticker, from_date, to_date=datetime.now(), period='1mo', frequency='1d'):
        super().__init__(ticker, period, from_date, to_date, frequency)
        rsp = requests.get(f'https://finance.google.com/finance?q={ticker}&output=json')
        if rsp.status_code in (200,):
            # Cut out various leading characters from the JSON response, as well as trailing stuff (a terminating ']\n'
            # sequence), and then we decode the escape sequences in the response
            # This then allows you to load the resulting string with the JSON module.
            print(rsp.content)
            fin_data = json.loads(rsp.content[6:-2].decode('unicode_escape'))


class Quandl(StockPriceScraper):
    def __init__(self, ticker, from_date, to_date=datetime.now(), period='1mo', frequency='1d'):
        super().__init__(ticker, period, from_date, to_date, frequency)


def get_prices_wrapper(source: str, ticker, period, from_date, to_date, frequency):
    if re.match('Quandl', source, re.IGNORECASE):
        pass
    elif re.match('Yahoo', source, re.IGNORECASE):
        pass
    elif re.match('Alpha Vantage', source, re.IGNORECASE):
        pass
    elif re.match('Google', source, re.IGNORECASE):
        pass
    else:
        raise Exception("Please make sure the `source` is either 'Quandl', 'Yahoo', 'Google', or 'Alpha Vantage'.")


if __name__ == '__main__':
    # not supporting list of tickers yet
    df = YahooFinance(ticker='AAPL', period='YTD').convert_format('pandas')
    print(df.index)

