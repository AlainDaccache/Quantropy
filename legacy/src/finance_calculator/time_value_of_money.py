from typing import Union, List


def future_value_of_present_value(present_value: float,
                                  r: Union[float, List[float]],
                                  num_periods: int = None):
    """
    Calculate the future value of a present value.

    Formula:
    $$ FV = PV * (1 + r)^n $$

    Parameters:
    - present_value (float): The initial present value.
    - r (float or list): The interest rate (discount rate) per period. Can be a list of interest rates. Should
    - num_periods (int): The number of periods. If

    Returns:
    - future_value (float): The expected future value of the growth annuity.
    """
    if isinstance(r, List):
        if num_periods is not None:
            raise ValueError("Please provide either list of interest rates or float with number of periods")
        future_value = present_value
        for rate in r:
            future_value *= (1 + rate)
        return future_value

    fv_of_present_value = present_value * (1 + r) ** num_periods
    return fv_of_present_value


def future_value_annuity(contribution: float,
                         r: float,
                         num_periods: int,
                         growth_rate: float = 0,
                         present_value: float = 0,
                         mode: str = "END"):
    """
    Calculate the future value of a growth annuity. The payments are made at the end of each period for n periods.

    Formula:
    $$ FV = [PV * (1 + r)^n]  + P [(1 + i)^n - (1 + g)^n] / (r - g) $$

    Parameters:
    - present_value (float): The initial present value.
    - contribution (float): The periodic payment (contribution).
    - r (float): The interest rate per period.
    - growth_rate (float): The growth rate of contributions per period. Optional, default 0%
    - num_periods (int): The number of periods.
    - mode (str): An annuity due ("BGN") is an annuity with payment due or made at the beginning of the payment interval.
                  In contrast, an ordinary annuity ("END") generates payments at the end of the period.
    Returns:
    - future_value (float): The expected future value of the growth annuity.
    """
    if isinstance(r, List) or isinstance(growth_rate, List):
        if not isinstance(r, List):
            r = [r] * len(growth_rate)
        if not isinstance(growth_rate, List):
            growth_rate = [growth_rate] * len(r)

    fv_of_present_value = future_value_of_present_value(present_value=present_value,
                                                        r=r,
                                                        num_periods=num_periods)
    fv_of_annuity = contribution * (((1 + r) ** num_periods) - ((1 + growth_rate) ** num_periods)) / (r - growth_rate)
    if mode == "BGN":
        # FIXME this is wrong. Only support END for now.
        fv_of_annuity *= (1 + growth_rate)

    return fv_of_present_value + fv_of_annuity


print(future_value_annuity(contribution=8000, r=0.03, growth_rate=0.06, num_periods=10))
