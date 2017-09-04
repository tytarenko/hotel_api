from models2 import database, Guest, Room


def create_tables():
    database.connect()
    database.create_tables([Guest, Room])


if __name__ == "__main__":
    create_tables()
