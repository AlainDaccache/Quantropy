# Factor research and empirical asset pricing

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Distinguish explanatory factors, security characteristics and investable strategies. Fama–French factors are constructed portfolios used to study returns; assigning a stock a value score is not the same operation as estimating its regression exposure. Market, size, value, profitability and investment appear in the five-factor model; momentum is a separate series/model choice. Pin region, sample and dataset release. [French library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), [five-factor paper](https://doi.org/10.1016/j.jfineco.2014.10.010).

Support excess-return regressions with matched frequencies/currencies/risk-free definitions, robust inference, rolling exposures, residuals and diagnostics. Alpha is relative to the chosen model and sample. Correlated factors, small samples, changing exposures and benchmark mismatch can create misleading significance.

For cross-sectional research, specify universe eligibility, availability lag, winsorization, industry/country neutrality, weighting, rebalance schedule and portfolio formation. Study value, momentum, quality, profitability, investment, size, low risk and other hypotheses separately before composites. Measure rank information coefficient, decay, turnover, concentration, factor crowding, capacity and implementable net performance. Delisted firms and historical membership must be included where relevant.

Use portfolio sorts and regressions as complementary diagnostics. Track every specification searched and hold out time periods. Ordinary significance for a single chosen factor is weak evidence after searching hundreds of alternatives. [Harvey, Liu and Zhu](https://www.nber.org/papers/w20592). Fama–MacBeth, shrinkage and robust covariance methods need separately reviewed statistical specifications, not names pasted onto ordinary least squares.

Acceptance: factors in percent are not confused with decimals; lagged fundamentals respect release dates; weights and sector exposures reconcile; independent regression fixtures agree; trial-selection history survives rejected experiments. Published factors are research inputs, not evidence of achievable retail returns.

## Coverage checklist

- CAPM and multifactor regression
- Fama French three and five factors
- Momentum and other documented factors
- Rolling exposures and attribution
- Cross-sectional portfolio sorts
- Rank IC decay and turnover
- Neutralization and composite factors
- Fama MacBeth and robust inference
- Factor crowding capacity and costs
- Point-in-time security universe
- Multiple-testing control and archives

## Research sources

- [FRENCH](sources.md#french)
- [FF5](sources.md#ff5)
- [MULTIPLE-TESTS](sources.md#multiple-tests)

[Knowledge base index](README.md)
