
from faker import Faker

from models2 import Room, Guest


def generate_rooms():
    for _ in range(25):
        Room.create(status=Room.STATUS_FREE)


def generate_guests():
    faker = Faker()
    for _ in range(10):
        Guest.create(name=faker.name())


def generate_busy_rooms():
    guests = list(Guest.select())
    for room in Room.select():
        if not guests:
            return
        guest = guests.pop()
        guest.room = room
        guest.save()
        room.status = Room.STATUS_BUSY
        room.save()


def generate():
    generate_rooms()
    generate_guests()
    generate_busy_rooms()


if __name__ == "__main__":
    generate()

