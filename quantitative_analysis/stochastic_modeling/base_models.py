import abc
import time

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


class StochasticProcess:
    def __init__(self, x0, Nsim=10000, Nsteps=252, T=1, seed=None, alpha=0.05):
        """

        :param xO: The current asset price.
        :param Nsim: The number of Monte Carlo simulations (at least 10,000 required to generate stable results).
        :param Nsteps: The number of time steps, or the number of monitoring dates (default is 252, equivalent to the number of trading days in a year).
        :param T: The total time, or the maturity of the option contract, i.e. the final monitoring date.
        :param seed: Set random seed, for reproducibility of the results. Default value is None (the best seed available is used, but outcome will vary in each experiment).
        """
        np.random.seed(seed)
        self.x0 = x0
        self.Nsim = Nsim
        self.Nsteps = Nsteps
        self.T = T
        self.alpha = alpha

    @abc.abstractmethod
    def sample_path_simulation(self):
        pass

    def compute_simulations(self):
        '''
        Generate an Nsim x (Nsteps+1) array of zeros to preallocate the simulated
        paths of the Monte Carlo simulation. Each row of the matrix represents a
        full, possible path for the stock, each column all values of the asset at
        a particular instant in time.
        '''
        current_time = time.time()  # Time the whole path-generating process
        # Populate the matrix with Nsim randomly generated paths of length Nsteps
        simulated_paths = np.zeros([self.Nsim, self.Nsteps + 1])
        for i in range(self.Nsim):
            simulated_paths[i:] = self.sample_path_simulation()
        # Time and print the elapsed time
        print('Total running time: {:.2f} ms'.format((time.time() - current_time) * 1000))

    def compute_statistics(self, final_prices):
        # Compute mean, variance, standard deviation, skewness, excess kurtosis
        mean_jump = np.mean(final_prices)
        var_jump = np.var(final_prices)
        std_jump = np.std(final_prices)
        skew_jump = stats.skew(final_prices)
        kurt_jump = stats.kurtosis(final_prices)

        # Calculate confidence interval for the mean
        ci_low = mean_jump - std_jump / np.sqrt(self.Nsim) * stats.norm.ppf(1 - 0.5 * self.alpha)
        ci_high = mean_jump + std_jump / np.sqrt(self.Nsim) * stats.norm.ppf(1 - 0.5 * self.alpha)

        # Print statistics, align results
        return {'Monte Carlo Estimates': {'Mean': mean_jump, 'Variance': var_jump, 'Standard Deviation': std_jump,
                                          'Skewness': skew_jump, 'Excess Kurtosis': kurt_jump},
                'Confidence Interval': {'Alpha': self.alpha, 'Lower Bound': ci_low, 'Upper Bound': ci_high}}

    def plot_simulations(self, simulated_paths):
        # Choose palette, figure size, and define figure axes
        sns.set(palette='viridis')
        plt.figure(figsize=(10, 8))
        ax = plt.axes()

        t = np.linspace(0, self.T, self.Nsteps + 1) * self.Nsteps  # Generate t, the time variable on the abscissae
        jump_diffusion = ax.plot(t, simulated_paths.transpose())  # Plot the Monte Carlo simulated stock price paths
        plt.setp(jump_diffusion, linewidth=1)  # Make drawn paths thinner by decreasing line width

        # Set title (LaTeX notation) and x- and y- labels
        ax.set(title="Monte Carlo simulated stock price paths", xlabel='Time (days)', ylabel='Stock price')
        plt.show()


class ContinuousStochasticProcess(StochasticProcess):
    def __init__(self, x0):
        super().__init__(x0)
        self.dt = self.T / self.Nsteps  # length of time step


class DiscreteStochasticProcess(StochasticProcess):
    pass
