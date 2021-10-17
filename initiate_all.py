db.drop_all()
db.create_all()
from app import fake_data
fake_data.users()
fake_data.orders(880)
