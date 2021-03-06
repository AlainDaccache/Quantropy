Fundamental Analysis
********************

Fundamental analysis assesses a company by looking at its financial statements to evaluate its health and value, and compares them across time and against
competitors.

Financial Statements
====================

Balance Sheet
-------------
.. py:currentmodule:: matilda.fundamental_analysis.financial_statements.balance_sheet

It's a snapshot of a company's position time, recording assets, liabillt.

Assets
++++++

.. autofunction:: cash_and_cash_equivalents

Income Statement
----------------

.. py:currentmodule:: matilda.fundamental_analysis.financial_statements.income_statement

Cash Flow Statement
-------------------

.. py:currentmodule:: matilda.fundamental_analysis.financial_statements.cash_flow_statement

Intermediary Metrics
====================


Accounting Ratios
=================

Liquidity Ratios
----------------
.. py:currentmodule:: matilda.fundamental_analysis.accounting_ratios.liquidity_ratios

These ratios measure the availability of cash to pay debt.

.. autofunction:: current_ratio
.. autofunction:: acid_test_ratio
.. autofunction:: cash_ratio
.. autofunction:: operating_cash_flow_ratio

Activity (Efficiency) Ratios
----------------------------
.. py:currentmodule:: matilda.fundamental_analysis.accounting_ratios.efficiency_ratios

These ratios measure how quickly a firm converts non-cash assets to cash assets.

.. autofunction:: degree_of_operating_leverage
.. autofunction:: asset_turnover_ratio
.. autofunction:: accounts_payables_turnover_ratio
.. autofunction:: payables_conversion_period
.. autofunction:: inventory_turnover_ratio
.. autofunction:: inventory_conversion_period
.. autofunction:: accounts_receivables_turnover_ratio
.. autofunction:: average_collection_period
.. autofunction:: cash_conversion_cycle

Profitability Ratios
--------------------

.. py:currentmodule:: matilda.fundamental_analysis.accounting_ratios.profitability_ratios

These ratios measure the firm's use of its assets and control of its expenses to generate an acceptable rate of return.
Profitability ratios measure a company’s ability to generate income relative to revenue, balance sheet assets, operating costs, and equity.

.. autofunction:: gross_profit_margin
.. autofunction:: net_profit_margin
.. autofunction:: operating_profit_margin
.. autofunction:: return_on_assets
.. autofunction:: return_on_equity
.. autofunction:: return_on_net_assets
.. autofunction:: return_on_invested_capital
.. autofunction:: return_on_capital_employed
.. autofunction:: cash_flow_return_on_investment
.. autofunction:: efficiency_ratio
.. autofunction:: net_gearing
.. autofunction:: basic_earnings_power

Market Ratios
-------------
.. py:currentmodule:: matilda.fundamental_analysis.accounting_ratios.market_value_ratios

These ratios measure investor response to owning a company's stock and also the cost of issuing stock.

.. autofunction:: dividend_payout_ratio
.. autofunction:: retention_ratio
.. autofunction:: dividend_coverage_ratio
.. autofunction:: dividend_yield
.. autofunction:: earnings_per_share
.. autofunction:: price_to_earnings
.. autofunction:: earnings_yield
.. autofunction:: greenblatt_earnings_yield
.. autofunction:: price_to_earnings_to_growth
.. autofunction:: book_value_per_share
.. autofunction:: price_to_book_ratio
.. autofunction:: price_to_sales
.. autofunction:: justified_price_to_sales
.. autofunction:: enterprise_value_to_revenue
.. autofunction:: enterprise_value_to_ebitda
.. autofunction:: enterprise_value_to_ebit
.. autofunction:: enterprise_value_to_invested_capital
.. autofunction:: enterprise_value_to_free_cash_flow

Equity Valuation Models
=======================

