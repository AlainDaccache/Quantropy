<p align="center">
    <img width=60% src="https://github.com/AlainDaccache/Quantropy/blob/master/docs/source/images/quantropy_logo.PNG">
</p>

<!-- buttons -->
<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-v3-brightgreen.svg"
            alt="python"></a> &nbsp;
    <a href="https://travis-ci.com/github/AlainDaccache/Quantropy">
        <img src="https://shields.beevelop.com/travis/beevelop/docker-shields.svg?style=flat-square" alt="Travis">
        </a> &nbsp;
    <a href="https://pypi.org/project/Quantropy/0.0.1/">
        <img src="https://img.shields.io/badge/pypi-v1.4.1-brightgreen.svg" alt="pypi"></a> &nbsp;
    <a href="https://quantropy.readthedocs.io/">
        <img src="https://img.shields.io/badge/docs-passing-brightgreen.svg" 
        alt="docs"></a> &nbsp;
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg"
            alt="MIT license"></a> &nbsp;
    
</p>

The human mind is fascinating. Give it a series of observations, and it will attempt to find structure to it. 
It will find variables upon which the given data might depend on, and develop elaborate models 
in the hopes of predicting future observations. What if this search for the Holy Grail is all in vain? 
What if we have been fooled by randomness? 

## Table of Contents

- [Getting Started](#getting-started)
    - [Docker](#docker)
    - [Git](#git)
- [Proof of Concept](#proof-of-concept)
- [Architectural Design](#architectural-design)
- [Acknowledgment](#acknowledgment)
- [Contributing](#contributing)
- [Getting in Touch](#getting-in-touch)

## Getting Started

This project is an attempt on shedding light to this question that has puzzled researchers over the past century. 
It is the culmination of three years of learning about the financial markets, in order to develop a platform in the 
hopes of providing a comprehensive and unified approach to trading the financial markets. 

To fetch and run the project, you can choose one of the methods below. 
If successful, `Quantropy` should now be running [here](http://127.0.0.1:5000/).

### Docker

```bash
docker pull matilda
docker run -d -p 5000:5000 matilda
```

### Git

```bash
git clone https://github.com/AlainDaccache/Quantropy/
cd Quantropy
py -m pip install -r requirements.txt
set FLASK_APP=matilda
py -m flask run
```

## Proof of Concept

This open-source project is built with all types of users in mind. Whether you're a *seasoned trader* that wants to 
progressively learn how to code in order to automate your strategies, or vice-versa, the 
[documentation](https://quantropy.readthedocs.io/) covers both aspects. Through it, we synthesize the theoretical 
groundwork that was laid by academicians and industry practitioners for conducting fundamental, technical, and 
quantitative analysis, and using these for **stock picking**, **market timing**, 
and **portfolio allocation**. Alongside it, we provide an implementation that uses our API calls to apply and validate 
these models in real-life.

```bash
ff3 = FamaFrench_ThreeFactorModel(frequency='Monthly', to_date=datetime.today())
reg = ff3.regress_factor_loadings(portfolio=Portfolio(assets=['MSFT']))
pprint(reg.params)

stock_screener = StockScreener(securities_universe=config.MarketIndices.DOW_JONES)
stock_screener.filter_by_comparison_to_number(partial(ratios.price_to_earnings, period='FY'), '>', 5)
stock_screener.filter_by_sector(sector=config.GICS_Sectors.INFORMATION_TECHNOLOGY)
stock_screener.run()

lower_bounds = pd.Series(data=[40], index=['Alpha'])
upper_bounds = pd.Series(data=[80], index=['MKT'])
stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.CAPM,
                                                    lower_bounds=lower_bounds, upper_bounds=upper_bounds)
stock_screener.run(date=datetime(2018, 1, 1))
print(stock_screener.stocks)

class Alainps(Strategy):
    def is_time_to_reschedule(self, current_date, last_rebalancing_day):
        return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.Quarterly.value


strategy = Alainps(starting_date=datetime(2019, 1, 1), ending_date=datetime(2020, 12, 1),
                   starting_capital=50000, stock_screener=stock_screener, max_stocks_count_in_portfolio=12,
                   net_exposure=(100, 0), portfolio_allocation=EquallyWeightedPortfolio)
strategy.historical_simulation()
strategy.broker_deployment(Alpaca('YOUR_API_KEY', 'YOUR_SECRET_KEY'))
```

## Architectural Design

Essentially, we standardize algorithmic trading by decoupling analytics, data providers, and brokers, to allow the user to flexibly 
and comprehensively research models, develop strategies, and deploy them in real-time. The flow looks as such:

<img src="https://github.com/AlainDaccache/Quantropy/blob/master/docs/source/images/architecture_diagram.png" alt="Architecture Diagram">

The library attempts to:
- Implement the low-level work to achieve **abstraction**, so that the user can swiftly translate his insights into practice, 
without wasting time, energy, and money, reinventing the wheel.
- Follow good design practices to achieve **modularity**, allowing the user to swap in their components while still 
being able to reuse and extend on our framework.
- Make use of a DevOps pipeline to achieve **continuous integration and delivery**, integrating a stack of cutting-edge technologies.

<img src="" alt="DevOps Pipeline">

## Acknowledgment

Thanks to part of **McGill University**'s generous donation, I was able to acquire these books that I will use 
as reference throughout the implementation of this project:

* Andrew Ang. *Asset Management: A Systematic Approach to Factor Investing*
* Ernie Chan - *Algorithmic Trading: Winning Strategies and Their Rationale*
* Ernie Chan - *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*
* Stefan Jansen - *Machine Learning for Algorithmic Trading*
* Marcos Lopez de Prado - *Advances in Financial Machine Learning*
* Marcos Lopez de Prado - *Machine Learning for Asset Managers*
* Edward Qian - *Quantitative Equity Portfolio Management: Modern Techniques and Applications*

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 
Here is a list of areas that I think `Quantropy` can really benefit from:
- **Data Scraping**: Scrape alternative data (news sentiment analysis, web/app usage and reviews etc.), improve the HTML scraper for Edgar.
- **Factor Library**: Use our risk factor modeling interface to develop and publish your own factors! We can 
surely integrate them to develop our own community's asset pricing model (and perhaps our fund :smirk:).
- **Data Visualization**: Develop more visualizations using *Bokeh*. Integrate with *PowerBI*.
- **Portfolio management**: Implementing pre-defined strategies of fund managers (i.e. Warren Buffet, Benjamin Graham, Peter Lynch) 
based on books written and interviews. Extend broker deployment implementation.
- **Misc**: And of course, we can never get enough of *unit tests* and *documentation*!

## Getting in Touch

If you are having a problem with `Quantropy`, please raise a GitHub issue. For anything else, you can reach me at:

<img src="https://github.com/AlainDaccache/Quantropy/blob/master/docs/source/images/email.png" alt="email" class="center" style="width:50%;">
