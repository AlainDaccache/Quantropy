Asset Pricing Models
********************

.. automodule:: matilda.quantitative_analysis.risk_factor_modeling

The Efficient Market Hypothesis
===============================

The **Efficient Market Hypothesis**, formulated by *Eugene Fama*, posits that asset prices
reflect all available information. And therefore, if markets are indeed efficient, asset prices
should only react to new information, and it would be impossible to beat the market, consistently, in a risk-adjusted basis.
In other words, you cannot consistently earn excess returns over the market if you were not to use leverage.

What does *all available information* entail, however? There are three types of market efficiency, and are explained in the context of what information sets are factored in price trend.
This hypothesis can thus be empirically tested in three forms:

    * *Weak-form*: these test take the information set to be only the historical prices.
      So, assuming the hypothesis is true, only historical prices are factored in current prices,
      i.e. prices reflect all past price movements.
      This means current prices can be predicted from historical price trend; thus, it is impossible
      to profit from just looking at historical prices. You will need more information (i.e. private).

    * *Semi-strong form*: in addition to historical prices, all information which is publicly available, is reflected in prices already, such as companies' announcements or annual earnings figures

    * *Strong-form*: these tests regard private information.

Market efficiency denotes how information is factored in price. Fama emphasizes that, to test the hypothesis of
market efficiency, you need to test it along a model of market equilibrium (i.e. an asset pricing model);
this the *Joint Hypothesis Problem*, the efficient market hypothesis on its own doesn't generate testable
predictions. So, if a certain model yields a predicted return significantly different
from the actual return (this difference is called the *alpha*), you can't be certain if it's because of (a) an
inefficient market, or (b) an imperfect model. So you cannot disprove market efficiency because the *alpha* might
be due to a wrong model. Researchers can only modify their models by adding different factors to eliminate any anomalies, in hopes of fully explaining (in other words, perfectly predicting)
the return within the model. If you find such model, this disproves market inefficiency (i.e. proves efficiency).

So take some time to wrap your head around it; we've all been there:

Capital Asset Pricing Model
===========================

.. py:currentmodule:: matilda.quantitative_analysis.risk_factor_modeling.asset_pricing_model

The Capital Asset Pricing Model, or CAPM for short, is a factor model that attempts to explain the returns
of a portfolio as a function of the overall market returns.

.. autoclass:: CapitalAssetPricingModel

The Intuition behind CAPM
--------------------------

Regardless of the companies that you choose to invest in, regardless of the diversification you achieved (in terms of industry,
sector etc. or some mean variance analysis to minimize correlation), each of those companies are to some degree exposed
to the risk of the overall market. For instance, the Covid-19 pandemic caused companies across the market to fall, even
if the cause of the fall itself isn't related to the company's operations (i.e. poor earnings, lawsuit etc.)

Therefore, there is a risk inherent when participating in the free market. This risk is called the **systematic risk** (often times
dubbed as non-diversifiable risk, or non-idiosyncratic risk), and you should be compensated for it.

We can use this risk exposure to measure the return you should expect from this security. As a risk averse investor,
you would like to be compensated for the additional risk you are taking by investing
in equities. So, you should expect at least the *risk-free rate of return* (i.e. Treasury bills as a proxy),
and, for each unit of risk (i.e. the Beta), you should be additionally compensated by the market returns (in excess of the risk-free rate)
This assumes that beta risk is the only kind of risk for which investors should receive an expected return higher than the risk-free rate of interest.
This forms the intuition behind the model most commonly used in asset pricing, the *Capital Asset Pricing Model*. It is a *single-factor model*.


The Derivation of CAPM
----------------------

Let's look at the effect of adding an asset *a* to a market portfolio *m*, under the Modern Portfolio Theory Model (more detail in the `Portfolio Optimization` module)

    * The expected return of the market portfolio is :math:`w_m * E(R_{m})`, and by adding an asset of expected return :math:`w_a * E(R_{m})`, that would be the added return to the market portfolio. So, the market portfolio's updated expected returns would be :math:`w_m * E(R_{m}) + w_a * E(R_{m})`

    * The risk of the market portfolio is :math:`w_{m}^2 * \sigma_{m}^2`. When adding an asset *a* of risk :math:`w_{a}^2 * \sigma_{a}^2` to the market portfolio, the added risk is :math:`w_{a}^2 * \sigma_{a}^2 + 2 * w_m * w_a * \rho_{am} * \sigma_{a} * \sigma_{m}`, but since the weight of the asset will be relatively low, :math:`w_{a}^2 \approx 0`, so the additional risk would be :math:`2 * w_m * w_a * \rho_{am} * \sigma_{a} * \sigma_{m}`. The updated market portfolio risk is then :math:`w_{m}^2 * \sigma_{m}^2 + 2 * w_m * w_a * \rho_{am} * \sigma_{a} * \sigma_{m}`

How do we use this to derive an appropriate discount rate for our asset?
The asset return depends on the amount paid for the asset today.
The price paid must ensure that the market portfolio's risk / return characteristics improve when the asset is added to it.
If an asset, a, is correctly priced, the improvement in its risk-to-expected return ratio achieved by adding it to the
market portfolio, m, will at least match the gains of spending that money on an increased stake in the market portfolio.
The assumption is that the investor will purchase the asset with funds borrowed at the risk-free rate, :math:`R_{f}`;
this is rational if :math:`E(R_a) > R_f`.

.. math:: \frac{w_{a} * (E(R_a) - R_f)}{2 * w_m * w_a * \rho_{am} * \sigma_{a} * \sigma_{m}} = \frac{w_a * (E(R_m) - R_f)}{2 * w_m * w_a * \sigma_m * \sigma_m}

.. math:: \implies E(R_a) = R_f + (E(R_m) - R_f) * \frac{\rho_{am} \sigma_a \sigma_m}{\sigma_m \sigma_m}

.. math:: \implies E(R_a) = R_f + (E(R_m) - R_f) * \frac{\sigma_{am}}{\sigma_{mm}}

Beta: A Proxy of Market Risk
----------------------------

The :math:`\frac{\sigma_{am}}{\sigma_{mm}}` is the 'beta', :math:`\beta`.
It is the covariance between the asset's return and the market's return divided by the variance of the market return.

.. math:: \beta_i = \frac{Covariance(E(R_a), E(R_m))}{Variance(E(R_m))}
    :label: covariance_method

In other words, it is the sensitivity of the asset price to movement in the market portfolio's value.
How does this asset *react* - on average - when the market goes up or down, or, how does it move with respect to the market.
An asset with a beta greater (less) than 1 means that, on average, its returns moves more (less) than 1-to-1 with the return of the market portfolio.

The CAPM formula becomes

.. math:: E(R_i) = \beta_i * (E(R_m) - R_f) + R_f
    :label: CAPM

What I found interesting, is that not only beta represents how much an asset is *exposed* to the market risk,
but also the *contribution* of an asset to the risk of the market portfolio, that was not reduced by diversification.
If we were to compute the value-weighted (market-cap weighted) average of the beta of all assets with respect to
the value-weighted portfolio, we would get 1. This is why Betas with respect to different market indexes are not comparable.

.. autofunction:: asset_pricing_model.CapitalAssetPricingModel.get_expected_returns

If the CAPM is correct, then using this rate of return to discount the future cash flows produced by the asset (DCF, to be covered
in another section) should give its actual price, according to the **Efficient Market Hypothesis**,
which staples that all assets are correctly priced.

This is the rate of return used in Discounted Cash Flow (DCF) analysis to discount the future
cash flows produced by the asset, which we cover in another section. Thus, **assuming** that the
CAPM is correct, an asset would be correctly priced if this discounted value is equal to its estimated price
based on either fundamental or technical analysis techniques, including P/E, M/B etc.

If the estimated price is higher (lower) than the

CAPM is not *just* a regression.
We can run a regression of your portfolio against the returns of the market.
Alphas from a time-series regression are error terms in the cross-sectional, linear relationship between expected returns and factor betas. If a factor model were correct those error terms (the alphas) would be zero.

The Security Market Line
------------------------
The CAPM formula can be visualized through the Security Market Line, which computes the
expected rate of returns (`y-axis`) for different values of :math:`\beta` (`x-axis`). The slope
is thus the market premium, :math:`(E(R_m) - R_f)`.

.. autofunction:: asset_pricing_model.CapitalAssetPricingModel.security_market_line

The Capital Allocation Line
---------------------------

A Tale of Asset Pricing Models
==============================

The idea of being paid a *premium* for additional risk you're exposed to inspired many researchers to empirically expand on
the simplistic CAPM, which failed to capture other sources of risk that must be 'factored' in to explain market returns.

Fama-French Three Factor Model (1992)
-------------------------------------

CAPM posited that a stock's beta alone should explain its average return.

The Capital Asset Pricing Model contains one factor,
    - The **market factor**, R_m - R_f is the excess return on the market

    The Fama French 3 Factor model adds 2 factors to the CAPM:
    - The **size factor**, 'SMB' for Small Minus Big [returns spread between small and large stocks]
    - The **value** factor,'HML' for High Minus Low [returns spread between cheap and expensive stocks]

    Carhart adds another factor to the Fama-French 3, the **momentum factor**, 'UMD' for Up Minus Down

    Fama French neglects the validity of Carhart's factor, but add two new factors to their original model.
    However, more is not necessarily better.

    - The **profitability factor**, 'RMW' for Robust Minus Weak
    - The ** factor**, 'CMA' for Conservative Minus Aggressive [returns spread of firms that invest conservatively and aggressively]

AQR Capital Management, namely
    - 'QMJ' (Quality Minus Junk)
    - 'BAB' (Betting Against Beta)
    - 'HML Devil' (High Minus Low Devil)

Pastor and Stambaugh add another factor to Fama-French 3, the **liquidity factor** LIQ.

Stambaugh_and_Yuan: Four factor model: Excess market returns, SMB, MGMT, PERF

Fama and French found two anomalies:

historical-average returns on stocks of small firms and on stocks with high ratios of
book equity to market equity (B/M) are higher than predicted by the security market line of the CAPM.
The reason pointed out by FF that firms with high ratios of book-to-market value are more likely to be
in financial distress and small stocks may be more sensitive to changes in business conditions and thus
provide higher historical-average return than predicted by CAPM.
They justified their model on empirical grounds.

.. autoclass:: FamaFrench_ThreeFactorModel

Carhart Four Factor Model (1997)
--------------------------------
.. autoclass:: Carhart_FourFactorModel

Pastor-Stambaugh Model (2003)
-----------------------------
.. autoclass:: Q_FactorModel

AQR Factors (2013-2014)
-----------------------
.. autoclass::  AQR_FactorModel

Fama-French Five Factor Model (2015)
------------------------------------
.. autoclass:: FamaFrench_FiveFactorModel

Constructing your Asset Pricing Model
=====================================

.. autoclass:: CustomAssetPricingModel
.. autofunction:: CustomAssetPricingModel.pre_filter_universe
.. autofunction:: CustomAssetPricingModel.compute_raw_factors
.. autofunction:: CustomAssetPricingModel.normalize_factors
.. autofunction:: CustomAssetPricingModel.factor_weighted_sum
.. autofunction:: CustomAssetPricingModel.portfolio_cross_section