from typing import Dict, List, Union


class SafeWithdrawalRate:
    def __init__(self):
        pass

    @classmethod
    def rule_of_thumb(self):
        return 0.04

    def validator(self, n: int,
                  asset_class_returns: Dict[str, List[float]],
                  asset_class_allocations: Union[List[Dict[str, float]], Dict[str, float]],
                  inflation: List[float]):
        for r in asset_class_returns.values():
            assert n == len(r)
        assert n == len(inflation)
        assert isinstance(asset_class_allocations, List) or isinstance(asset_class_allocations, Dict)
        if isinstance(asset_class_allocations, List):
            for dictio in asset_class_allocations:
                assert isinstance(dictio, Dict)
                assert len(dictio.keys()) == len(asset_class_returns.keys())
                assert sorted(dictio.keys()) == sorted(asset_class_returns.keys())
        else:
            assert len(asset_class_allocations.keys()) == len(asset_class_returns.keys())
            assert sorted(asset_class_allocations.keys()) == sorted(asset_class_returns.keys())

        assert len(asset_class_allocations.keys()) == len(asset_class_returns.keys())

    def one_simulation(self, n: int,
                       asset_class_returns: Dict[str, List[float]],
                       asset_class_allocations: Dict[str, float],
                       inflation: List[float]):
        self.validator(n=n,
                       asset_class_returns=asset_class_returns, asset_class_allocations=asset_class_allocations,
                       inflation=inflation)
    from abc import ABC
    class Sampler(ABC):
        def __init__(self):
            pass
        def sample(self):
            pass

    class HistoricalReturnsSampler(Sampler):
        def sample(self):
            # samples from fitted (multivariate) distribution
            pass

    class FutureReturnsSampler(Sampler):
        def sample(self):
            # samples from multivariate time series model
            pass

    def pure_monte_carlo(self,
                         return_distributions: Sampler,
                         inflation: Sampler,
                         survival_probability: float,
                         number_of_years: int):

        """
        Based on risk tolerance and time horizon, output appropriate SWR
        Parameters
        ----------
        return_distributions
        inflation
        survival_probability
        number_of_years

        Returns
        -------

        """
        pass

    def monte_carlo(self,
                    m: int, # periods in future
                    n: int,
                    asset_class_returns: Dict[str, List[float]], asset_class_allocations: List[Dict[str, float]],
                    inflation: List[float]):

        self.validator(n=n, asset_class_returns=asset_class_returns, asset_class_allocations=asset_class_allocations,
                       inflation=inflation)
        # for each possible withdrawal rate, for each possible asset allocation, find the optimal SWR for each allocation
        # give SWR if you want to survive m years with a % Probability

def fire_number(swr: float, expected_periodic_expenses: float):
    """

    Parameters
    ----------
    swr
    expected_periodic_expenses: float
        Assume annual

    Returns
    -------

    """
    return expected_periodic_expenses / swr


def how_soon(
        annuity: float,
        rate_of_return: float,
        fire_number: float,
        inflation_rate: float = 0.00,
        initial_deposit: float = 0.0,
        mode="END"):
    periods = 0
    FV = initial_deposit

    while FV < fire_number:
        if mode == "BGN":
            FV += annuity
        FV *= (1 + (rate_of_return - inflation_rate))
        if mode == "END":
            FV += annuity
        periods += 1
    return periods
    # return math.log(1 + (FV * r) / P, base=10) / math.log(1 + r)


if __name__ == '__main__':
    import pandas as pd
    import os
    from pathlib import Path

    src_folder = Path(__file__).parent.parent
    df = pd.read_csv(os.path.join(src_folder, "data", "historical_returns.csv"))
    asset_class_returns = df.to_dict()

    # fire_no = fire_number(swr=0.04, expected_periodic_expenses=4000 * 12)
    # print(how_soon(initial_deposit=10000, annuity=750 * 26, rate_of_return=0.055,
    #                fire_number=fire_no))
