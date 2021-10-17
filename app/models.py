import enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime, copy, random
from . import db, login_manager

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return self.name

class Organisation(db.Model):
    __tablename__ = 'organisations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='organisation', lazy='dynamic')
    tasks_assigned = db.relationship('Task', backref='organisation', lazy='dynamic')

    def __repr__(self):
        return self.name

users_skills = db.Table('users_skills',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('skill_id', db.Integer, db.ForeignKey('skills.id')))


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    # tasks_assigned = db.relationship('Task', backref='user', lazy='dynamic')
    tasks_assigned = db.relationship('Task', backref='user', lazy='dynamic')
    skills = db.relationship('Skill', secondary=users_skills, backref=db.backref('users'))


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.email

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    vat_number = db.Column(db.Integer, index=True)
    first_name = db.Column(db.String(64), index=True)
    surname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True)
    phone_number_1 = db.Column(db.String(64))
    phone_number_2 = db.Column(db.String(64))
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def __repr__(self):
        return '%r %r' % (self.surname, self.first_name)

class OrderType(enum.Enum):
    Pilot = 0
    Drop = 1

class OrderCategory(enum.Enum):
    Retail = 0
    Wholesale = 1
    Wholebuy = 2

class TaskType(db.Model):
    __tablename__ = 'task_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    label = db.Column(db.String(64), unique=True)
    short_label = db.Column(db.String(8), unique=True)
    default_duration = db.Column(db.Integer)
    tasks = db.relationship('Task', backref='task_type', lazy='dynamic')

    def __repr__(self):
        return self.name

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(64), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    task_type_id = db.Column(db.Integer, db.ForeignKey('task_types.id'))
    planned_start_dt = db.Column(db.DateTime)
    planned_end_dt = db.Column(db.DateTime)
    actual_start_dt = db.Column(db.DateTime)
    actual_end_dt = db.Column(db.DateTime)
    planned_date = db.Column(db.Date)
    insertion_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id'))
    status = db.Column(db.String(16), index=True)

    def start_time_index(self):
        if self.planned_start_dt:
            time_str = self.planned_start_dt.strftime("%H:%M")
            return time2index_dict[time_str]
        else:
            return ""

    def end_time_index(self):
        if self.planned_end_dt:
            time_str = self.planned_end_dt.strftime("%H:%M")
            return time2index_dict[time_str]
        else:
            return ""

    def schedule(self, earliest_start_dt, task_duration_hours_all, time_slots):
        slot_minimum_duration_hours = 3
        i = 0
        user_id = 0
        task_duration_hours = 3 # Site Survey duration
        if self.task_type_id > 1:
            user_id = self.order.tasks[0].user_id
            task_duration_hours = task_duration_hours_all[user_id-1]
        for time_slot in time_slots:
            if user_id == 0 or user_id == time_slot['user_id']:
                slot_duration = time_slot['slot_end_dt'] - time_slot['slot_start_dt']
                if earliest_start_dt <= time_slot['slot_start_dt'] and task_duration_hours*3600 <= slot_duration.total_seconds():
                    self.planned_start_dt = time_slot['slot_start_dt']
                    self.planned_end_dt = time_slot['slot_start_dt'] + datetime.timedelta(hours=task_duration_hours)
                    self.planned_date = self.planned_start_dt.date()
                    self.insertion_date = self.order.insertion_dt.date()
                    # self.user = User.query.filter_by(id=time_slot['user_id']).first()
                    self.user_id = time_slot['user_id']
                    self.organisation = self.user.organisation
                    self.status = 'Scheduled'
                    time_slots.insert_new_slot(i, self.planned_end_dt, slot_minimum_duration_hours)
                    time_slots.pop(i)
                    break
                elif time_slot['slot_start_dt'] <= earliest_start_dt and earliest_start_dt + datetime.timedelta(hours=task_duration_hours) < time_slot['slot_end_dt']:
                    self.planned_start_dt = earliest_start_dt
                    self.planned_end_dt = earliest_start_dt + datetime.timedelta(hours=task_duration_hours)
                    self.planned_date = self.planned_start_dt.date()
                    # self.user = User.query.filter_by(id=time_slot['user_id']).first()
                    self.user_id = time_slot['user_id']
                    self.organisation = self.user.organisation
                    self.status = 'Scheduled'
                    existing_slot_duration_new = earliest_start_dt - time_slot['slot_start_dt']
                    time_slots.insert_new_slot(i, self.planned_end_dt, slot_minimum_duration_hours)
                    if existing_slot_duration_new.total_seconds() > slot_minimum_duration_hours*3600:
                        time_slot['slot_end_dt'] = earliest_start_dt
                    else:
                        time_slots.pop(i)
                    break
            i += 1

class TimeSlots:

    def __init__(self, overall_start_dt, overall_end_dt, User):
        delta_dt = overall_end_dt - overall_start_dt
        delta_time = overall_end_dt - datetime.timedelta(days=delta_dt.days) - overall_start_dt
        self._slot_list = []
        for i in range(delta_dt.days):
            slot_start_dt = overall_start_dt + datetime.timedelta(days=i)
            random_hours_shorter = random.randint(0, 4)
            slot_end_dt = slot_start_dt + delta_time - datetime.timedelta(hours=random_hours_shorter)
            if slot_start_dt.weekday() < 5:
                for user in User.query.all():
                    slot = {'slot_start_dt': slot_start_dt,
                            'slot_end_dt': slot_end_dt,
                            'user_id': user.id
                            }
                    slot_dc = copy.deepcopy(slot)
                    self._slot_list.append(slot_dc)

    def __getitem__(self, position):
        return self._slot_list[position]

    def __len__(self):
        return len(self._slot_list)

    def __str__(self):
        for slot in self:
            print('Start Date/Time: {}, End Date/Time: {}, User: {}'.format(slot['slot_start_dt'], slot['slot_end_dt'], slot['user_id']))
        return 'Timeslots List Lenght={}'.format(len(self._slot_list))

    def remove(self, time_slot):
        self._slot_list.remove(time_slot)

    def pop(self, i):
        self._slot_list.pop(i)

    def insert(self, i, slot):
        self._slot_list.insert(i, slot)

    def insert_new_slot(self, i, task_planned_end_dt, slot_minimum_duration_hours):
        if (self[i]['slot_end_dt'] - task_planned_end_dt).total_seconds() >= slot_minimum_duration_hours*3600:
            new_time_slot = {'slot_start_dt': task_planned_end_dt,
                             'slot_end_dt': self[i]['slot_end_dt'],
                             'user_id': self[i]['user_id']}
        else:
            return
        for j in range(i+1, len(self)):
            if task_planned_end_dt < self[j]['slot_start_dt']:
                slot_dc = copy.deepcopy(new_time_slot)
                self.insert(j, slot_dc)
                break


time2index_dict = {'08:00': 1, '09:00': 2, '10:00': 3, '11:00': 4, '12:00': 5, '13:00': 6, '14:00': 7, '15:00': 8,
                     '16:00': 9, '17:00': 10, '18:00': 11, '19:00': 12, '20:00': 13, '21:00': 13, '22:00': 13,
                     '23:00': 13, '00:00': 13}

task_duration_matrix = [[3, 3, 3, 3, 3, 3, 3, 3, 3],
                        [6, 8, 8, 6, 6, 6, 8, 8, 8],
                        [6, 8, 8, 6, 6, 6, 8, 8, 8],
                        [3, 3, 3, 3, 3, 3, 3, 3, 3]]

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(64), index=True)
    type = db.Column(db.Enum(OrderType))
    category = db.Column(db.Enum(OrderCategory))
    central_office = db.Column(db.String(64), index=True)
    installation_address = db.Column(db.String(128), index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    insertion_dt = db.Column(db.DateTime)
    tasks = db.relationship("Task", backref='order')
    # site_survey_task_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    # infrastructure_construction_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    # opt_network_construction_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    # customer_connection_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def schedule(self, ord_index, in_ord_pd:'incoming orders per day', time_slots:'timeslot object'):
        start_dt = time_slots[0]['slot_start_dt']
        end_dt = time_slots[0]['slot_end_dt']
        hours_pd = int((end_dt - start_dt).total_seconds()/3600)
        day_offset = int(ord_index/in_ord_pd) + random.randint(0, 2) ########## Random insertion date
        # day_offset = 0
        hours_offset = random.randint(0, hours_pd)
        minutes_offset = random.randint(0, 60)
        seconds_offset = random.randint(0, 60)
        self.insertion_dt = start_dt + datetime.timedelta(days=day_offset, hours=hours_offset, minutes=minutes_offset, seconds=seconds_offset)

        if self.type == OrderType.Pilot:
            d = self.insertion_dt.date()
            t = start_dt.time()
            # earliest_start_dt = datetime.datetime.combine(d, t) + datetime.timedelta(days=random.randint(1, 4))

            for k in range(0, len(self.tasks)):
                task_duration_hours_all = task_duration_matrix[k]
                if k == 0:
                    earliest_start_dt = datetime.datetime.combine(d, t) + datetime.timedelta(days=1)
                else:
                    earliest_start_dt = self.tasks[k-1].planned_end_dt
                self.tasks[k].schedule(earliest_start_dt, task_duration_hours_all, time_slots)

    def __repr__(self):
        # return '<Order %r>' % self.order_id
        return self.order_id
