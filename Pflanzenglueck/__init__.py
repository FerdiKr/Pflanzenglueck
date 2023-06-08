# init.py

import mimetypes
mimetypes.add_type('application/javascript','.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from werkzeug.security import generate_password_hash
from sqlalchemy.orm.exc import NoResultFound
import secrets
import click
import json

import os

# init SQLAlchemy so we can use it later in our models 
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Die diversen Keys etc. einrichten, entweder per envvar (praktisch beim deployen) oder direkt
    configure_from_envvars = int(os.environ.get('CONFIGURE_FROM_ENVVARS','0'))
    app.config['SECRET_KEY'] = os.environ.get('FLASKAPP_SECRET_KEY') if configure_from_envvars else 'YOUR_SUPER_SECRET_KEY'
    app.config['TESTING'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEFAULT_LANGCODE'] = "de_DE"

    from .storage import FS_Storage as Storage
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path,"rule_data")
    app.config['STORAGE_HANDLER'] = Storage(data_path)
    
    from .localization import Localization
    @app.context_processor
    def inject_variables():
        localization = Localization(request.cookies.get('langcode',app.config['DEFAULT_LANGCODE']),fallback_order=['en_US','de_DE'])
        app.config['LOCALIZATION_OBJECT'] = localization
        return dict(loc=localization,globalloc=localization)
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @click.command('adduser')
    @click.argument('username',nargs=1)
    @click.argument('password',nargs=1)
    def add_user_command(username,password):
        strg = Storage(os.path.join(os.path.dirname(os.path.abspath(__file__)),"rule_data"))
        db.session.add(User(name=username,password=generate_password_hash(password),api_key=secrets.token_urlsafe(20)))
        strg.mkdir(username)
        user_rules_path = strg.path_join(strg.base_path,username,'rules.json')
        strg.write_file(user_rules_path,json.dumps([]))
        db.session.commit()
        print('User added')

    app.cli.add_command(add_user_command)

    @click.command('deluser')
    @click.argument('username', nargs=1)
    def remove_user_command(username):
        try:
            # Create a new scoped session for deletion
            session = db.create_scoped_session()

            # Query the user to be deleted within the new session
            user = session.query(User).filter_by(name=username).one()

            # Remove user directory
            storage = Storage(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rule_data"))
            user_rules_path = storage.path_join(storage.base_path, username)
            if storage.exists(user_rules_path):
                storage.delete(user_rules_path)

            # Remove user from database
            session.delete(user)
            session.commit()
            print(f'User {username} removed successfully')
        except NoResultFound:
            print(f'User {username} not found')

    app.cli.add_command(remove_user_command)
    

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @login_manager.request_loader
    def load_user_from_request(request):
        # tut das selbe wie user_loader (nämlich Nutzer einloggen), nur eben über den api_key
        # first, try to login using the api_key url arg
        api_key = request.args.get('api_key')
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # otherwise, return none
        return None

    # blueprint for most parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Blueprint für die API (die Teile, auf die die Bewässerungsgeräte zugreifen)
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Blueprint für den Authentifizierungskram
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint für mein WebComponent-System
    from .components import components as components_blueprint
    app.register_blueprint(components_blueprint)

    return app