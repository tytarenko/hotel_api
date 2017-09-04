import peewee

database = peewee.SqliteDatabase('hotel.db')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Type(BaseModel):
    name = peewee.CharField(index=True, unique=True)


class Status(BaseModel):
    name = peewee.CharField(index=True, unique=True)


class Room(BaseModel):
    type = peewee.ForeignKeyField(Type, null=True, default=None)
    # TODO should move to separate table for discount and etc.
    price = peewee.DecimalField()
    options = peewee.CharField()

    @classmethod
    def find_available_between_dates(cls, from_date, to_date):
        sql = """
            SELECT r2.*
            FROM room r2
            LEFT JOIN (
                SELECT r1.id
                FROM room r1
                JOIN booking b ON b.room_id = r1.id
                WHERE
                    b.from_date BETWEEN {interpolation} AND {interpolation}
                    OR
                    b.to_date BETWEEN {interpolation} AND {interpolation}
                ) r3
                ON r3.id = r2.id
            WHERE r3.id is NULL
        """.format(interpolation=database.interpolation)
        result = cls.raw(sql, from_date, to_date, from_date, to_date)
        return result

    @classmethod
    def get_available_between_dates_by_id(cls, room_id, from_date, to_date):
        sql = """
            SELECT r2.*
            FROM room r2
            LEFT JOIN (
                SELECT r1.id
                FROM room r1
                JOIN booking b ON b.room_id = r1.id
                WHERE
                    b.from_date BETWEEN {interpolation} AND {interpolation}
                    OR
                    b.to_date BETWEEN {interpolation} AND {interpolation}
                ) r3
                ON r3.id = r2.id
            WHERE
                r3.id is NULL
                AND
                r2.id = {interpolation}
        """.format(interpolation=database.interpolation)
        result = list(Room.raw(sql, from_date, to_date, from_date, to_date, room_id))
        return result.pop() if result else None


class Customer(BaseModel):
    name = peewee.CharField(index=True)
    passport = peewee.CharField(index=True, unique=True)


class Booking(BaseModel):
    room = peewee.ForeignKeyField(Room, related_name='booking', on_delete='CASCADE')
    customer = peewee.ForeignKeyField(Customer, related_name='booking', on_delete='CASCADE')
    status = peewee.ForeignKeyField(Status)
    from_date = peewee.DateField(index=True)
    to_date = peewee.DateField(index=True)
    # TODO should move to separate table for discount and etc.
    cost = peewee.DecimalField()
