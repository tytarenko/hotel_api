from models import database, Customer, Room, Type, Status, Booking


def create_tables():
    database.create_tables([Customer, Room, Type, Booking, Status])


if __name__ == "__main__":
    create_tables()
