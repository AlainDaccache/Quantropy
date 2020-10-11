import numpy as np
from stochastic_modeling.base_models import ContinuousStochasticProcess
from stochastic_modeling.brownian_motion_model import BrownianMotionModel


class MertonJumpDiffusionModel(ContinuousStochasticProcess):
    def __init__(self, x0, brownian_delta, drift=0.12, volatility=0.3, Lambda=0.25, a=0.2, b=0.2):
        super().__init__(x0)
        self.drift = drift
        self.volatility = volatility
        self.brownian_motion = BrownianMotionModel(x0=x0, delta=brownian_delta)
        self.Lambda = Lambda
        self.a = a
        self.b = b
        '''
        Compute mean and variance of the multiplicative jumps by standard lognormal distribution from user defined 
        parameters a and b. The latter are useful to simulate the jump component in Monte Carlo.
        a and b are chosen such that log(Y(j)) ~ N(a, b**2)
        '''
        mean_Y = np.exp(a + 0.5 * (b ** 2))
        variance_Y = np.exp(2 * a + b ** 2) * (np.exp(b ** 2) - 1)
        self.M = self.x0 * np.exp(self.drift * self.T + Lambda * self.T * (mean_Y - 1))
        self.V = self.x0 ** 2 * (np.exp((2 * self.drift + self.volatility ** 2) * self.T
                                        + Lambda * self.T * (variance_Y + mean_Y ** 2 - 1))
                                 - np.exp(2 * self.drift * self.T + 2 * Lambda * self.T * (mean_Y - 1)))

    """
    Monte Carlo simulation [1] of Merton's Jump Diffusion Model [2].
    The model is specified through the stochastic differential equation (SDE):

                        dS(t)
                        ----- = mu*dt + sigma*dW(t) + dJ(t)
                        S(t-)
    with:
        - mu, sigma: constants, the drift and volatility coefficients of the stock price process;
        - W: a standard one-dimensional Brownian motion;
        - J: a jump process, independent of W, with piecewise constant sample paths.
        It is defined as the sum of multiplicative jumps Y(j).

    Input
    ---------------------------------------------------------------------------

    mu, sigma: float. Respectively, the drift and volatility coefficients of
               the asset price process.
    Lambda: float. The intensity of the Poisson process in the jump diffusion
            model ('lambda' is a protected keyword in Python).
    a, b: float. Parameters required to calculate, respectively, the mean and
          variance of a standard lognormal distribution, log(x) ~ N(a, b**2).
          (see code).
    alpha: float. The confidence interval significance level, in [0, 1].
    References
    ---------------------------------------------------------------------------
    [1] Glasserman, P. (2003): 'Monte Carlo Methods in Financial Engineering',
        Springer Applications of Mathematics, Vol. 53
    [2] Merton, R.C. (1976): 'Option Pricing when Underlying Stock Returns are
        Discontinuous', Journal of Financial Economics, 3:125-144.
    [3] Hull, J.C. (2017): 'Options, Futures, and Other Derivatives', 10th
        Edition, Pearson.
    """

    def sample_path_simulation(self):
        Z_1, Z_2 = np.random.normal(size=[self.Nsteps]), np.random.normal(size=[self.Nsteps])
        Poisson = np.random.poisson(self.Lambda * self.dt, [self.Nsteps])
        simulated_path = np.asarray(self.x0)
        for i in range(self.Nsteps + 1):
            simulated_path[i + 1] = simulated_path[i] * np.exp(
                (self.drift - self.volatility ** 2 / 2) * self.dt + self.volatility * np.sqrt(self.dt)
                * Z_1[i] + self.a * Poisson[i] + np.sqrt(self.b ** 2) * np.sqrt(Poisson[i]) * Z_2[i])

        return simulated_path
