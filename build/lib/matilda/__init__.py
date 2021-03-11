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
    print(total_current_assets(stock='AAPL'))
    # app.run(debug=True, host='0.0.0.0')
