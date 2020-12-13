from portfolio_management.broker_deployment.broker_interface import Broker
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
                    order_type: str = 'Market', time_in_force: str = 'DAY'):
        return self.api.submit_order(symbol=symbol, qty=quantity, side=side, type=order_type,
                                     time_in_force=time_in_force)


if __name__ == '__main__':
    API_KEY_ID = 'PKOG800MQG7J30EZ1PJ0'
    API_SECRET_KEY = 'MED9IwqKOfZ1HYNa4Iy5BeJoR3yEPaP5d34TwnxY'
    API_ENDPOINT = 'https://paper-api.alpaca.markets'
    alpaca = AlpacaBroker(key_id=API_KEY_ID, secret_key=API_SECRET_KEY, endpoint=API_ENDPOINT)
    print(alpaca.list_positions())
