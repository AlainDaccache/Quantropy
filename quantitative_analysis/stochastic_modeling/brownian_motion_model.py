from quantitative_analysis.stochastic_modeling.base_models import ContinuousStochasticProcess
import math
import numpy as np
from scipy import stats


class BrownianMotionModel(ContinuousStochasticProcess):
    """
        Generate an instance of Brownian motion (i.e. the Wiener process):

            X(t) = X(0) + N(0, delta**2 * t; 0, t)

        where N(a,b; t0, t1) is a normally distributed random variable with mean a and
        variance b.  The parameters t0 and t1 make explicit the statistical
        independence of N on different time intervals; that is, if [t0, t1) and
        [t2, t3) are disjoint intervals, then N(a, b; t0, t1) and N(a, b; t2, t3)
        are independent.

        Written as an iteration scheme,

            X(t + dt) = X(t) + N(0, delta**2 * dt; t, t+dt)


        If `x0` is an array (or array-like), each value in `x0` is treated as
        an initial condition, and the value returned is a numpy array with one
        more dimension than `x0`.

        Arguments
        -----------------------------------------------------------------------------
        delta : float
            delta determines the "speed" of the Brownian motion.  The random variable
            of the position at time t, X(t), has a normal distribution whose mean is
            the position at time t=0 and whose variance is delta**2*t.

        Returns
        ------------------------------------------------------------------------------
        A numpy array of floats with shape `x0.shape + (n,)`.

        Note that the initial value `x0` is not included in the returned array.
        """
    def __init__(self, x0, delta=2):
        super().__init__(x0)
        self.delta = delta

    def sample_path_simulation(self):
        x0 = np.asarray(self.x0)
        # For each element of x0, generate a sample of n numbers from a normal distribution.
        r = stats.norm.rvs(size=x0.shape + (self.Nsim,), scale=self.delta * math.sqrt(self.dt))
        out = np.empty(r.shape)
        # This computes the Brownian motion by forming the cumulative sum of the random samples.
        np.cumsum(r, axis=-1, out=out)
        out += np.expand_dims(x0, axis=-1)  # Add the initial condition.

        return out
