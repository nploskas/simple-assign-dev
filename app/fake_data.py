from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError
from faker import Faker
import random,datetime
from random import randint
import pandas as pd

from . import db
from .models import User, Role, Order, Customer, OrderType, OrderCategory, Organisation, Skill, TaskType, Task, TimeSlots

def users():
    admin_role = Role(name='Admin')
    dispatcher_role = Role(name='Dispatcher')
    field_role = Role(name='Field')
    db.session.add_all([admin_role, dispatcher_role, field_role])

    company01 = Organisation(name='Company01')
    company02 = Organisation(name='Company02')
    company03 = Organisation(name='Company03')
    company04 = Organisation(name='Company04')
    company05 = Organisation(name='Company05')
    db.session.add_all([company01, company02, company03, company04, company05])

    Site_Survey_skill = Skill(name='Site_Survey')
    Infrastructure_Construction_skill = Skill(name='Infrastructure_Construction')
    Opt_Network_Construction_skill = Skill(name='Opt_Network_Construction')
    Customer_Connection_skill = Skill(name='Customer_Connection')
    db.session.add_all([Site_Survey_skill, Infrastructure_Construction_skill, Opt_Network_Construction_skill, Customer_Connection_skill])

    Site_Survey_task_type = TaskType(name='Site_Survey', label='Site Survey', short_label='SS', default_duration=3)
    Infrastructure_Construction_task_type = TaskType(name='Infrastructure_Construction', label='Infrastructure Construction', short_label='IC', default_duration=8)
    Opt_Network_Construction_task_type = TaskType(name='Opt_Network_Construction', label='Opt. Network Construction', short_label='ONC', default_duration=8)
    Customer_Connection_task_type = TaskType(name='Customer_Connection', label='Customer Connection', short_label='CC', default_duration=2)
    db.session.add_all([Site_Survey_task_type, Infrastructure_Construction_task_type, Opt_Network_Construction_task_type, Customer_Connection_task_type])

    db.session.commit()

    user_nikif = User()
    user_nikif.email = 'nikif@gmail.com'
    user_nikif.username = 'nikif'
    user_nikif.password = 'test'
    user_nikif.role = admin_role
    user_nikif.organisation = company01

    user_john = User()
    user_john.email = 'john@gmail.com'
    user_john.username = 'john'
    user_john.password = 'test'
    user_john.role = dispatcher_role
    user_john.organisation = company01

    user_susan = User()
    user_susan.email = 'susan@gmail.com'
    user_susan.username = 'susan'
    user_susan.password = 'test'
    user_susan.role = field_role
    user_susan.organisation = company02

    user_user01 = User()
    user_user01.email = 'user01@gmail.com'
    user_user01.username = 'user01'
    user_user01.password = 'test'
    user_user01.role = field_role
    user_user01.organisation = company02

    user_user02 = User()
    user_user02.email = 'user02@gmail.com'
    user_user02.username = 'user02'
    user_user02.password = 'test'
    user_user02.role = field_role
    user_user02.organisation = company03

    user_user03 = User()
    user_user03.email = 'user03@gmail.com'
    user_user03.username = 'user03'
    user_user03.password = 'test'
    user_user03.role = field_role
    user_user03.organisation = company03

    user_user04 = User()
    user_user04.email = 'user04@gmail.com'
    user_user04.username = 'user04'
    user_user04.password = 'test'
    user_user04.role = field_role
    user_user04.organisation = company04

    user_user05 = User()
    user_user05.email = 'user05@gmail.com'
    user_user05.username = 'user05'
    user_user05.password = 'test'
    user_user05.role = field_role
    user_user05.organisation = company04

    user_user06 = User()
    user_user06.email = 'user06@gmail.com'
    user_user06.username = 'user06'
    user_user06.password = 'test'
    user_user06.role = field_role
    user_user06.organisation = company05

    for user in User.query.all():
        for skill in Skill.query.all():
            user.skills.append(skill)

    # db.session.add_all([user_nikif, user_john, user_susan])
    db.session.commit()

central_office_list = ['SOUROTI', 'NRYSIO', "PEREA", 'NKALIKRATIA', 'NIKITI']

def generate_type(type, category):
    if category==OrderCategory.Wholebuy:
        return OrderType.Drop
    else:
        return type

# def str_time_prop(start, end, format, prop):
#     """Get a time at a proportion of a range of two formatted times.
#
#     start and end should be strings specifying times formated in the
#     given format (strftime-style), giving an interval [start, end].
#     prop specifies how a proportion of the interval to be taken after
#     start.  The returned time will be in the specified format.
#     """
#     stime = time.mktime(time.strptime(start, format))
#     etime = time.mktime(time.strptime(end, format))
#
#     ptime = stime + prop * (etime - stime)
#
#     return time.strftime(format, time.localtime(ptime))
#
# def random_date(start, end, prop):
#     return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)

def orders(count=100):

    fake = Faker()
    i = 0

    while i < count:

        c = Customer(
                vat_number=1351234500+randint(1, 1351234500),
                first_name=fake.first_name(),
                surname=fake.last_name(),
                email=fake.email(),
                phone_number_1=2399027715+randint(0, 999999),
                phone_number_2=6976451455+randint(0, 999999)
        )
        db.session.add(c)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            break
        # print(c.id)

        category_inst = random.choice(list(OrderCategory))
        type_inst = generate_type(random.choice(list(OrderType)), category_inst)

        o = Order(
                order_id=2234500 + i*100,
                category=category_inst,
                type=OrderType.Pilot,
                # type=type_inst, !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                central_office=central_office_list[randint(0, 4)],
                installation_address=fake.address(),
                customer_id=c.id
        )
        # print(o.order_id)
        db.session.add(o)

        # if type_inst == OrderType.Pilot:  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if True:
            j=0
            for task_type in TaskType.query.all():
                j+=1
                t = Task(order=o, task_id=1111111+i*100+j, task_type=task_type, status="Not Scheduled")
        else:
            t = Task(order=o, task_id=1111111 + i * 100 + 4, task_type=TaskType.query.filter_by(name='Customer_Connection').first(), status="Not Scheduled")
        db.session.add(t)
        try:
            db.session.commit()
            i+=1
        except IntegrityError:
            db.session.rollback()


    overall_start_dt = datetime.datetime(2020, 1, 8, 8, 0, 0)
    overall_end_dt = datetime.datetime(2020, 12, 31, 20, 0, 0)
    time_slots = TimeSlots(overall_start_dt, overall_end_dt, User)
    print(time_slots)


    i=0
    for order in Order.query.all():
        order.schedule(ord_index=i, in_ord_pd=3, time_slots=time_slots)
        print('order_index=%d' %i)
        i += 1
    db.session.commit()

    print(time_slots)

    data = db.session.query(Task).all()

    df = pd.DataFrame([(d.id, d.task_id, d.order.order_id, d.order.category, d.order.central_office, d.task_type.name, d.order.insertion_dt, d.planned_start_dt,
    d.planned_end_dt, d.actual_start_dt, d.actual_end_dt, d.planned_date, d.insertion_date,
    d.user.email, d.organisation.name, d.status) for d in data],
    columns=['id', 'task_id', 'order_id', 'category', 'central_office', 'task_type', 'insertion_dt', 'planned_start_dt',
    'planned_end_dt', 'actual_start_dt', 'actual_end_dt', 'planned_date', 'insertion_date',
    'user', 'organisation', 'status'])

    df.to_excel('try.xls')

    # df = pd.DataFrame([(d.candid, d.rank, d.user_id) for d in data],
    #                   columns=['candid', 'rank', 'user_id'])