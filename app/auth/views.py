import flask_admin as admin
from flask import redirect, url_for, flash
from flask_admin import helpers, expose
from flask_login import login_user, current_user, logout_user
from .forms import LoginForm
from ..models import User

# Create customized index view class that handles login
class MyAdminIndexView(admin.AdminIndexView):

    def is_accessible(self):
        return not current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('order.edit_view'))

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return redirect(url_for('order.edit_view'))

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm()
        if helpers.validate_form_on_submit(form):
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(url_for('order.edit_view'))
            else:
                flash('Invalid email or password.')
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.login_view'))
