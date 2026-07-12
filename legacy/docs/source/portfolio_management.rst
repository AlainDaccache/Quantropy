Portfolio Backtesting & Deployment Framework
********************************************

In this section, we investigate the framework that goes behind **researching** and **developing** investment strategies.
It ties the previous sections together,

There are several elements that are considered in academia and industry practice, which we discuss below.

Securities Universe
-------------------
.. py:currentmodule:: matilda.portfolio_management.stock_screener

The *securities universe* is a set of securities based on defined parameters.To apply this procedure,
we make use of a `StockScreener` object.

.. autoclass:: StockScreener

The process typically starts with first picking stocks that are trading in a specific region (i.e. USA, Canada, Asia...), exchange (i.e. NASDAQ, NYSE...), index (i.e. Dow Jones,
S&P 500...), sector, or industry.

.. autofunction:: Stock_Screener.filter_by_market

The process continues with conducting an initial filtering based on concerns like liquidity
(i.e. *market capitalization*, *volume traded*). Finally, narrowing down based on types of analysis such as
*technical*, *fundamental*, and *quantitative*, which we detail in their respective modules.

We use the metrics above (either as *raw*, *mean*, or *growth* values), then compare against either a *number*, *another metric*, or *percentile* against competitors.

.. autofunction:: Stock_Screener.run

Market Timing
-------------

It is important that these conditions are all re-evaluated when we rebalance the portfolio, to avoid succumbing
to mistakes like *survivorship bias*.

**Rebalancing Frequency**
**Trigger Based**: Define another `StockScreener` object


Portfolio Allocation
--------------------

Other Considerations
--------------------

* Reinvesting dividends
* Including capital gain taxes

Historical Simulation
=====================

Broker Deployment
=================
