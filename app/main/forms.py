from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, Form
from wtforms.validators import DataRequired
from flask_admin.form.fields import DateTimeField

class OrderInfoForm(FlaskForm):
    order_id = StringField(render_kw={'readonly': True})
    central_office = StringField(render_kw={'readonly': True})
    type = StringField(render_kw={'readonly': True})
    category = StringField(render_kw={'readonly': True})
    installation_address = StringField(render_kw={'readonly': True})
    surname = StringField(render_kw={'readonly': True})
    first_name = StringField(render_kw={'readonly': True})
    vat_number = IntegerField(render_kw={'readonly': True})
    phone_number_1 = IntegerField(render_kw={'readonly': True})
    phone_number_2 = IntegerField(render_kw={'readonly': True})

class OrderSSForm(FlaskForm):
    start_dt = DateTimeField('Site Survey Start Date/Time', format="%d%b%Y %H:%M", render_kw={'readonly': True})
    end_dt = DateTimeField('Site Survey End Date/Time', format="%d%b%Y %H:%M", render_kw={'readonly': True})
    assigned_to = StringField('Assigned to', render_kw={'readonly': True})
    status = StringField('Status', render_kw={'readonly': True})

class OrderICForm(FlaskForm):
    start_dt = DateTimeField('Infrastructure Construction Start Date/Time', render_kw={'readonly': True})
    end_dt = DateTimeField('Infrastructure Construction End Date/Time', render_kw={'readonly': True})
    assigned_to = StringField('Assigned to', render_kw={'readonly': True})
    status = StringField('Status', render_kw={'readonly': True})

class OrderONCForm(FlaskForm):
    start_dt = DateTimeField('Opt. Network Construction Start Date/Time', render_kw={'readonly': True})
    end_dt = DateTimeField('Opt. Network Construction End Date/Time', render_kw={'readonly': True})
    assigned_to = StringField('Assigned to', render_kw={'readonly': True})
    status = StringField('Status', render_kw={'readonly': True})

class OrderCCForm(FlaskForm):
    start_dt = DateTimeField('Customer Connection Start Date/Time', render_kw={'readonly': True})
    end_dt = DateTimeField('Customer Connection End Date/Time', render_kw={'readonly': True})
    assigned_to = StringField('Assigned to', render_kw={'readonly': True})
    status = StringField('Status', render_kw={'readonly': True})
