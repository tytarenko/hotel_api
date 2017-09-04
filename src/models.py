import peewee
from playhouse.shortcuts import model_to_dict

database = peewee.SqliteDatabase('hotels.db', threadlocals=True)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Room(BaseModel):
    STATUS_FREE = 0
    STATUS_BUSY = 1
    STATUSES = (
        (STATUS_FREE, 'free'),
        (STATUS_BUSY, 'busy')
    )
    SINGLE_ROOM = 1
    DOUBLE_ROOM = 2
    TRIPLE_ROOM = 3
    TYPES = (
        (SINGLE_ROOM, 'single room'),
        (DOUBLE_ROOM, 'double room'),
        (TRIPLE_ROOM, 'triple room'),
    )

    status = peewee.SmallIntegerField(default=STATUS_FREE, choices=STATUSES, index=True)
    type = peewee.SmallIntegerField(choices=TYPES, index=True)

    @staticmethod
    def get_status(status_id):
        return dict(Room.STATUSES).get(status_id)

    @staticmethod
    def get_type(type_id):
        return dict(Room.TYPES).get(type_id)

class Guest(BaseModel):
    name = peewee.CharField(index=True, unique=True)
    room = peewee.ForeignKeyField(Room, related_name='guests', null=True, default=None)
