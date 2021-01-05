# Quαntropy

The human mind is fascinating. Give it a series of observations, and it will attempt to find structure to it. 
It will find variables upon which the given data might depend on, and develop elaborate models, 
in the hopes of predicting future observations. What if this search for the Holy Grail is all in vain? 
What if we have been fooled by randomness? 

## Framework Description

This project is an attempt to shed light on this question that has puzzled researchers for the past century. It is the culmination of three years of learning about the financial markets, and almost a year of
developing a platform in order to provide a comprehensive and unified approach to trading the financial markets.

Essentially, we replicate the academia and industry methodologies into an open-source framework that our community 
can reuse and extend on, with the low-level work already done. Therefore, we standardize algorithmic trading by decoupling analytics, data providers, and brokers, to allow the user to flexibly 
and comprehensively research models, develop strategies, and deploy them in real-time. The pipeline looks as such:

1.  In the `historical_data_collection` package, we scrape data from various sources, including SEC Edgar for **financial statements** and **market classification**,
    YahooFinance for **asset prices**, FRED for **macroeconomic data**, and various datasets for **risk factors**. 
    *Currently migrating from Excel and Pickle files to MongoDB and Kafka for real-time streaming.*

2.  a.  In the `fundamental_analysis` package, we provide tools to assess a company's fair value (**equity valuation models**),
        and evaluate by looking at **accounting ratios**, and accompanying *financial distress* and *earnings manipulation* models,
        and compare across time and competitors. 
    
    b. In the `technical_analysis` package, we provide tools to detect geometric shapes (**chart patterns**, **candlestick patterns**) 
    and price characteristics (**technical indicators**). *Still under development, not a priority, but can use `TA-Lib` meanwhile.*
    
    c. In the `quantitative_analysis` package, we provide tools to model risk for **portfolio optimization**, as well 
    as research drivers of returns through **asset pricing models**, and forecast outcomes through **stochastic processes**.
    
3.  In the `portfolio_management` package, we construct portfolios by *selecting stocks* using the aforementioned analysis for **stock screening**, 
    and *allocating weights* through **portfolio optimization**. We then use our **backtester** to realistically evaluate historical performance,
    then **deploy** to a broker. Several **templates** for strategies are provided, including *style* (value, growth, momentum, quality), 
    *trend*, *mean-reversion*, *event-driven arbitrage*, *smart-beta*, and *pairs trading*. 

Note: I am currently focused in more of the *project management* aspects of the project, for writing unit and mock tests, DevOps and
documentation, as well as database migration. After I'm done (~ April 2021), I will extend the implementation based on the books I just ordered:
* Andrew Ang. *Asset Management: A Systematic Approach to Factor Investing*
* Ernie Chan - *Algorithmic Trading: Winning Strategies and Their Rationale*
* Ernie Chan - *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*
* Marcos Lopez de Prado - *Advances in Financial Machine Learning*
* Marcos Lopez de Prado - *Machine Learning for Asset Managers*
* Stefan Jansen - *Machine Learning for Algorithmic Trading*
* Edward Qian - *Quantitative Equity Portfolio Management: Modern Techniques and Applications*

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Current opportunities for contribution include:

* **Documentation**: For literally everything. 
* **Data collection**: Scraping *alternative data* (news sentiment analysis, web/app usage and reviews etc.), improve the *HTML scraper* for Edgar.
* **Fundamental analysis**: Using `matplotlib` for appropriate visualizations across time, industry, sector, and market.
* **Portfolio management**: Implementing risk parity models for portfolio optimization, and pre-defined strategies of 
superinvestors (i.e. Warren Buffet, Benjamin Graham, Peter Lynch) based on books written and interviews. Extending broker deployment implementation.

Please make sure to update tests as appropriate.