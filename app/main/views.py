from flask import request, redirect, url_for, session
from flask_admin import BaseView, expose, helpers
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from datetime import date, datetime
from .. import admin
from ..models import db, User, Role, Customer, Order, TaskType, Task
from markupsafe import Markup
from .weekview import WeekView
from .monthview import MonthView
from .dateview import DateView

class MyRoleView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    column_list = ('name', 'users')
    column_editable_list = ('name', 'users')
    column_filters = ['name', 'users.email']
    filter_labels = {'users.email':''}
    column_searchable_list = ['name']
    # column_hide_backrefs = False

class MyUserView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    can_create = False
    column_list = ('username', 'email', 'organisation.name', 'role.name', 'skills')
    column_labels = {'organisation.name': 'Organisation', 'role.name': 'Role'}
    column_sortable_list = ('username', 'email', 'organisation.name', 'role.name')
    column_filters = ['username', 'email', 'organisation.name', 'role.name', 'skills.name']
    # form_excluded_columns = ('password_hash', 'tasks_assigned')
    column_filter_labels = {'organisation.name': 'Organisation', 'role.name': 'Role', 'skills.name': 'Skills'}

    def scaffold_filters(self, name):
        filters = super().scaffold_filters(name)
        if name in self.column_filter_labels:
            for f in filters:
                f.name = self.column_filter_labels[name]
        return filters

    def edit_form(self, obj):
        form = super(MyUserView, self).edit_form(obj)
        query = self.session.query(Task).filter((Task.user_id==None) | (Task.user_id==obj.id)  )
        form.tasks_assigned.query = query
        return form

class MyCustomerView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

class MyTaskView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    can_create = False
    can_delete = False
    can_edit = False
    can_export = True
    column_display_actions = False

    column_list = ('task_id', 'order.order_id', 'order.category', 'order.central_office', 'order.insertion_dt', 'task_type.name', 'user.email', 'organisation.name', 'status', 'planned_start_dt', 'planned_end_dt', 'actual_start_dt', 'actual_end_dt')
    column_sortable_list = ('task_id', 'order.order_id', 'order.category', 'order.central_office', 'order.insertion_dt', 'task_type.name', 'user.email', 'organisation.name', 'status', 'planned_start_dt', 'planned_end_dt', 'actual_start_dt', 'actual_end_dt')
    column_labels ={'order.order_id': 'Order', 'order.category': 'Category', 'order.central_office': 'Central Office', 'order.insertion_dt': 'Order Insertion Date/Time','task_type.name': 'Task Type', 'user.email': 'User', 'organisation.name':'Organisation', 'planned_start_dt': 'Planned Start Date/Time', 'planned_end_dt': 'Planned End Date/Time', 'actual_start_dt': 'Actual Start Date/Time', 'actual_end_dt': 'Actual End Date/Time'}

    column_filters = ['task_id', 'order.order_id', 'order.category', 'order.central_office', 'order.insertion_dt', 'task_type.name', 'user.email', 'organisation.name', 'status', 'planned_start_dt', 'planned_end_dt', 'actual_start_dt', 'actual_end_dt']
    # form_excluded_columns = ('', '')
    column_filter_labels = {'order.order_id': 'Order', 'order.category': 'Category', 'order.central_office': 'Central Office', 'order.insertion_dt': 'Order Insertion Date/Time', 'task_type.name': 'Task Type', 'user.email': 'User', 'organisation.name': 'Organisation', 'planned_start_dt': 'Planned Start Date/Time', 'planned_end_dt': 'Planned End Date/Time', 'actual_start_dt': 'Actual Start Date/Time', 'actual_end_dt': 'Actual End Date/Time'}

    def scaffold_filters(self, name):
        filters = super().scaffold_filters(name)
        if name in self.column_filter_labels:
            for f in filters:
                f.name = self.column_filter_labels[name]
        return filters

class MyOrderView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    can_create = False
    can_delete = False
    can_edit = False
    can_export = True
    column_display_actions = False

    column_list = ('order_id', 'insertion_dt', 'type', 'category', 'central_office', 'installation_address', 'customer.surname', 'customer.first_name')
    column_sortable_list = ('order_id', 'insertion_dt', 'type', 'category', 'central_office', 'installation_address', 'customer.surname', 'customer.first_name')
    column_filters = ['order_id', 'insertion_dt', 'type', 'category', 'central_office', 'installation_address', 'customer.surname', 'customer.first_name']
    column_labels = {'insertion_dt': 'Insertion Date/Time', 'customer.surname':'Surname', 'customer.first_name':'First Name'}

    def _format_order_id(view, context, model, name):
        _html = '''
            <script src="{script}"></script>
            <form action="/abpreview/" id="{order_id}" method="POST" style='padding:0px;'>
                <input name="order_id" value="{order_id}" type="hidden">
                <input class="order_list_url" name="order_list_url_name" type="hidden">
            </form>
            <button class="btn btn-secondary btn-sm" title="Open" onclick="on_order_open({order_id})">{order_id}</button>
        '''.format(script=url_for('static', filename='order_list.js'), order_id=model.order_id)
        return Markup(_html)

    column_formatters = {
        'order_id': _format_order_id #,
    }

def str2task_type(string):
    if string=='SS': return TaskType.query.filter_by(name='Site_Survey').first()
    elif string=='IC': return TaskType.query.filter_by(name='Infrastructure_Construction').first()
    elif string=='ONC': return TaskType.query.filter_by(name='Opt_Network_Construction').first()
    elif string=='CC': return TaskType.query.filter_by(name='Customer_Connection').first()

def str2date_time(date_str, time_int):

    time_str = []
    for i in range(16):
        string='{:02}:00'.format(i+8)
        time_str.append(string)
    for i in range(4):
        time_str.append('00:00')

    date_time_str=date_str+' '+time_str[int(time_int)]
    return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")

class ABView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/', methods=('POST', 'GET'))
    def index(self):
        order_list_url=session['order_list_url']
        order_id=session['order_id']
        order = Order.query.filter_by(order_id=order_id).first()
        if 'start_time_index' in session:
            if session['start_time_index']:
                task_id = session['task_id']
                task = Task.query.filter_by(task_id=task_id).first()
                task.planned_start_dt = str2date_time(session['date'], session['start_time_index'])
                task.planned_end_dt = str2date_time(session['date'], session['end_time_index'])
                task.planned_date = task.planned_start_dt.date()
                task.user = User.query.filter_by(email=session['user_email']).first()
                task.organisation = task.user.organisation
                task.status = 'Scheduled'
                db.session.add(task)
                db.session.commit()

        return self.render('admin/AB_action.html', order_list_url=order_list_url, order=order)

class ABpreView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/', methods=('POST', 'GET'))
    def index(self):
        for key in ['task_id', 'date', 'start_time_index', 'end_time_index', 'user_email']:
            if key in session:
                session.pop(key)

        if 'order_id' in request.form:
            session['order_id'] = request.form['order_id']
        if 'order_list_url_name' in request.form:
            session['order_list_url'] = request.form['order_list_url_name']
        # if 'datepicker' in request.form:
        #     session['date'] = request.form['datepicker']
        if 'start_time_index' in request.form:
            session['task_id']=request.form['task_id']
            session['date']=request.form['date']
            session['start_time_index']=request.form['start_time_index']
            session['end_time_index']=request.form['end_time_index']
            session['user_email']=request.form['user_email']
        return redirect('/abview/')

class GanttView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/', methods=('POST', 'GET'))
    def index(self):

        target_task = Task.query.filter_by(task_id=session['task_id']).first()

        date_picked = datetime.strptime(session['date_picked'], "%Y-%m-%d").date()

        tasks = Task.query.filter_by(planned_date=date_picked)

        existing = False
        for task in tasks:
            if task.task_id==target_task.task_id:
                existing = True
                break

        users = User.query.join(User.skills, aliased=True).filter_by(name=target_task.task_type.name)

        # print(target_task.task_id)
        # print(existing)
        return self.render('admin/Gantt.html', date_picked=date_picked, target_task=target_task, tasks=tasks, existing=existing, users=users)

class GanttpreView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/', methods=('POST', 'GET'))
    def index(self):
        if 'task_id' in request.form:
            session['task_id'] = request.form['task_id']
            target_task = Task.query.filter_by(task_id=session['task_id']).first()
            if 'date' in request.form:
                session['date_picked'] = request.form['date']
                    # //datetime.strptime(request.form['date'], "%Y-%m-%d").date()
            elif target_task.planned_start_dt:
                session['date_picked'] = target_task.planned_start_dt.date().strftime("%Y-%m-%d")
            else:
                session['date_picked'] = date.today().strftime("%Y-%m-%d")
        elif 'datepicker' in request.form:
            session['date_picked'] = request.form['datepicker']

        return redirect('/ganttview/')

admin.add_view(MyUserView(User, db.session, 'Users', category='Dispatcher'))
#admin.add_view(MyRoleView(Role, db.session))
admin.add_view(MyCustomerView(Customer, db.session, 'Customers', category='Dispatcher'))
admin.add_view(MyOrderView(Order, db.session, 'Orders', category='Dispatcher'))
admin.add_view(MyTaskView(Task, db.session, 'Tasks', category='Dispatcher'))
admin.add_view(DateView('Daily', category='Dashboard'))
admin.add_view(WeekView('Weekly', category='Dashboard'))
admin.add_view(MonthView('Monthly', category='Dashboard'))
admin.add_extra_view(ABView())
admin.add_extra_view(GanttView())
admin.add_extra_view(ABpreView())
admin.add_extra_view(GanttpreView())





