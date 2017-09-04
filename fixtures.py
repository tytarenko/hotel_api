import calendar
import random
import string
from datetime import date, timedelta

from faker import Faker

from models import Customer, Room, Type, Booking, Status


rooms = [
    ('standard', 20, 20.0, 'Standard options'),
    ('regular suite', 10, 40.0, 'Extension options'),
    ('deluxe suite', 5, 80.0, 'Premium options')
]


def rand_dates(max_days=None, year=None):
    y = year or date.today().year
    m = random.randint(1, 12)
    d = random.randint(1, calendar.monthrange(y, m)[1])
    days = random.randint(1, max_days or 28)
    from_date = date(y, m, d)
    return from_date, from_date + timedelta(days=days)


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_types():
    for name, _, _, _ in rooms:
        Type.create(name=name)


def generate_statuses():
    for name in ['reserved', 'paid']:
        Status.create(name=name)


def generate_rooms():
    for name, count, price, options in rooms:
        for _ in range(count):
            room_type = Type.select().where(Type.name == name).first()
            Room.create(type=room_type, price=price, options=options)


def generate_customers():
    faker = Faker()
    for _ in range(20):
        Customer.create(name=faker.name(), passport=id_generator())


def generate_booking():
    customers = list(Customer.select())
    rooms = list(Room.select())
    statuses = list(Status.select())
    random.shuffle(rooms)
    for customer in customers:
        from_date, to_date = rand_dates()
        room = rooms.pop()
        cost = (to_date - from_date).days * room.price
        Booking.create(
            customer=customer,
            room=room,
            status=random.choice(statuses),
            from_date=from_date,
            to_date=to_date,
            cost=cost)


def generate():
    generate_types()
    generate_statuses()
    generate_rooms()
    generate_customers()
    generate_booking()


if __name__ == "__main__":
    generate()

