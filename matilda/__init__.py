from flask import Flask
from flask_login import LoginManager
import os
import sys


dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from matilda.config import *

from matilda.fundamental_analysis import *
from matilda.portfolio_management import *
from matilda.quantitative_analysis import *
from matilda.broker_deployment import *

from matilda.data_pipeline.object_model import User
from matilda.data_pipeline.db_crud import get_atlas_db_url, connect_to_mongo_engine
from matilda.api_routes.auth import auth as auth_blueprint
from matilda.api_routes.main import main as main_blueprint

atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
db = connect_to_mongo_engine(atlas_url)

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'secret-key-goes-here'

app.register_blueprint(auth_blueprint)  # blueprint for auth routes in our app
app.register_blueprint(main_blueprint)  # blueprint for non-auth parts of app

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the email is just the primary key of our user table, use it in the query for the user
    return User.objects(_id=user_id).first()


if __name__ == '__main__':
    stocks = companies_in_classification(class_=config.MarketIndices.DOW_JONES)
    stock_screener = StockScreener(securities_universe=stocks)
    stock_screener.filter_by_comparison_to_number(partial(price_to_earnings, period='FY'), '>', 5)
    stock_screener.filter_by_market(filter=config.GICS_Sectors.INFORMATION_TECHNOLOGY)
    stock_screener.run()

    lower_bounds = pd.Series(data=[40], index=['Alpha'])
    upper_bounds = pd.Series(data=[80], index=['MKT'])
    stock_screener.filter_by_exposure_from_factor_model(factor_model=FactorModels.CAPM,
                                                        lower_bounds=lower_bounds, upper_bounds=upper_bounds)
    stock_screener.run(date=datetime(2018, 1, 1))
    print(stock_screener.stocks)

    class Alainps(Strategy):
        def is_time_to_reschedule(self, current_date, last_rebalancing_day):
            return (current_date - last_rebalancing_day).days > config.RebalancingFrequency.Quarterly.value

        def allocation_regime(self, portfolio):
            return EquallyWeightedPortfolio(portfolio).solve_weights()


    strategy = Alainps(starting_date=datetime(2019, 1, 1), ending_date=datetime(2020, 12, 1),
                       starting_capital=50000, stock_screener=stock_screener, max_stocks_count_in_portfolio=12,
                       net_exposure=(100, 0))
    strategy.historical_simulation()
    from matilda.broker_deployment.alpaca import AlpacaBroker
    alpaca = AlpacaBroker(key_id='YOUR_API_KEY_ID', secret_key='YOUR_API_SECRET_KEY',
                          endpoint='https://paper-api.alpaca.markets')
    strategy.broker_deployment(broker=alpaca)
    # app.run(debug=True, host='0.0.0.0')
