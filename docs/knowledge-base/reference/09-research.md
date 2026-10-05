# Empirical finance, factors and backtesting

An empirical result answers a defined question on a defined sample. Specify population, information date, hypothesis, economic mechanism and implementation assumptions before choosing a model. Correlation is not causation. A strategy discovered by testing many variants has a different evidential burden from a preregistered hypothesis tested once.

An asset-pricing regression often writes excess asset return as alpha+beta' f+error, where f are defined factor returns. Beta is conditional exposure; alpha is residual relative to that model, sample and estimation procedure. It is not automatically manager skill or a tradable anomaly. Cross-sectional pricing regressions, time-series exposure regressions and characteristic sorts answer different questions.

Factors such as value, momentum, profitability, investment, size and defensive characteristics need exact signal, universe, breakpoint, timing, weighting and rebalance definitions. A published long-short factor can require financing and shorting a retail account cannot obtain. Returns to equity, term, credit, liquidity, insurance, trend, carry and volatility exposures may compensate bad-state risk, exploit behavior, or reflect artifacts; labels alone do not establish the mechanism.

A backtest must reconstruct what was knowable and executable. Store economic observation date, publication date, vendor availability and revision vintage separately. Include delistings, bankruptcies, corporate actions and expired instruments. A signal based on a closing price generally cannot trade at that same close without a defensible order-information timeline. Adjusted research prices are not automatically executable prices.

**Example.** A financial year ends December 31, but statements become available February 20. A January rebalance must use earlier available information. Sorting January portfolios by the later statement creates look-ahead even though the observation period ended earlier. Restated numbers published the following year create an additional version problem.

Train preprocessing only on training information. For labels spanning time intervals, overlapping train/test label windows can leak information; remove training observations whose label-information intervals overlap the test intervals. Embargo addresses additional adjacent dependence under explicit assumptions. Walk-forward evaluation mimics successive fitting dates. Neither purging nor a fashionable validation acronym cures a wrongly timestamped dataset.

Costs include fees, spread, impact, borrowing, funding, roll and tax effects as appropriate. Fills require venue/session/order assumptions and available capacity. Performance should include exposure, turnover, drawdown, tail behavior, benchmark and uncertainty. Annualized Sharpe using square-root time scaling assumes suitable return dependence and conventions.

Freeze a genuinely untouched evaluation set, log all attempted variants, test stability across regimes and universes, and distinguish statistical significance from economic significance. PBO, deflated Sharpe and multiple-testing procedures need separate full definitions and inputs; they are evidence tools, not certificates of live profitability. Paper trading then tests operational assumptions that historical data cannot fully establish.

## Evidence and depth

Source map: [FRENCH](../sources.md#french), [FF5](../sources.md#ff5), [MULTIPLE-TESTS](../sources.md#multiple-tests), [OVERFIT](../sources.md#overfit), [SKLEARN](../sources.md#sklearn). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
