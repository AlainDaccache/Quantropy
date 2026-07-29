import abc


class Broker(metaclass=abc.ABCMeta):
    def __init__(self, key_id, secret_key, endpoint):
        self.key_id = key_id
        self.secret_key = secret_key
        self.endpoint = endpoint

    @abc.abstractmethod
    def get_account(self):
        pass

    @abc.abstractmethod
    def list_positions(self):
        pass

    @abc.abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float = 1,
                    order_type: str = 'Market', time_in_force: str = 'DAY'):
        '''
        :param symbol:
        :param side: str    'buy', 'sell'
        :param quantity:
        :param order_type: Market, Limit, Stop, Stop Limit
        :param time_in_force: DAY, GTC (Good till Canceled), FOK (Fill or Kill), IOC (Immediate or Cancel), OPG (At-the-open)
        :return:
        '''
        pass
