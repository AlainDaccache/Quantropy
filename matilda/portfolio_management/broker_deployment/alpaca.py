from matilda.portfolio_management.broker_deployment.broker_interface import Broker
import alpaca_trade_api as tradeapi


class AlpacaBroker(Broker):
    def __init__(self, key_id, secret_key, endpoint):
        super().__init__(key_id, secret_key, endpoint)
        self.api = tradeapi.REST(key_id=self.key_id, secret_key=self.secret_key, base_url=self.endpoint)

    def get_account(self):
        return self.api.get_account()

    def list_positions(self):
        return self.api.list_positions()

    def place_order(self, symbol: str, side: str, quantity: int = 1,
                    order_type: str = 'market', time_in_force: str = 'gtc'):
        return self.api.submit_order(symbol=symbol, qty=quantity, side=side, type=order_type,
                                     time_in_force=time_in_force)


if __name__ == '__main__':
    pass
