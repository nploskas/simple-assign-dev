from flask import Flask
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
# from flask_mail import Mail
# from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
from flask_wtf import CsrfProtect

from config import config

bootstrap = Bootstrap()
# mail = Mail()
# moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
#csrf = CsrfProtect()
# login_manager.login_view = 'auth.login'

from .auth.views import MyAdminIndexView

class MyAdmin(Admin):
    def add_extra_view(self, view):
        '''Like Admin.add_view() method, but does not add an item to menu'''
        self._views.append(view)
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint(self))

admin = MyAdmin(name='Simple Assign', template_mode='bootstrap3', index_view=MyAdminIndexView(url='/'), base_template='admin/my_master.html', url='/')

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)

    # mail.init_app(app)
    # moment.init_app(app)
    db.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)
    #csrf.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
