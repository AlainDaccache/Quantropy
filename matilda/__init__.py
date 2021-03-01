from flask import Flask
from flask_login import LoginManager
from .database.object_model import User
from .database.db_crud import get_atlas_db_url, connect_to_mongo_engine
from .api_routes.auth import auth as auth_blueprint
from .api_routes.main import main as main_blueprint

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


