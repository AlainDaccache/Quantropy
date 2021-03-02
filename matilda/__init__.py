from flask import Flask
from flask_login import LoginManager
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from matilda.database.object_model import User
from matilda.database.db_crud import get_atlas_db_url, connect_to_mongo_engine
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


"""
You can run the flask app in terminal with the commands 'set FLASK_APP=matilda', then 'py -m flask run'
When it says 'Running on http://0.0.0.0:5000/', it means it is accepting connections on any network adapter,
not a specific one. Use 127.0.0.1 i.e. 'http://localhost:5000/' to actually connect to a server running on your machine.
"""
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
