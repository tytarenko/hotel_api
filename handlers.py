from cerberus import Validator
from tornado import httputil
from tornado.escape import json_decode
from tornado.web import RequestHandler, HTTPError
import peewee

from helpers import model_to_dict, parse_date
from models import Room, Booking, Customer, Status, Type


class BaseHandler(RequestHandler):
    def reverse_url(self, name, *args, **kwargs):
        url = '{}://{}{}'.format(
            self.request.protocol,
            self.request.host,
            super(BaseHandler, self).reverse_url(name, *args))
        if not kwargs:
            return url
        return httputil.url_concat(url, kwargs)

    def get_only_fields(self):
        raw_fields = self.get_argument('fields', '')
        return filter(None, raw_fields.split(','))

    def set_response(self, content=None, headers=None, status=200):
        if content:
            self.write(content)
        if headers:
            for name, value in headers.items():
                self.set_header(name, value)
        if status:
            self.set_status(status)

    def valid_data(self, schema, data):
        validator = Validator(schema)
        if validator.validate(data):
            return True
        self.set_response(
            content={'message': 'incorrect params: {}'.format(validator.errors)},
            status=400)
        return False


class BookingHandler(BaseHandler):
    def _get_booking_date(self):
        from_date = self.get_argument('from', '')
        to_date = self.get_argument('to', '')
        if not (from_date or to_date):
            raise ValueError('Missing params: [from] or(and) [to]')
        from_date = parse_date(from_date)
        to_date = parse_date(to_date)
        if from_date >= to_date:
            raise ValueError('start date {} must be less stop date {}'.format(from_date, to_date))
        return from_date, to_date

    def _prepare_addition_attrs(self, room, count_booking_days):
        return {
            'url': self.reverse_url('room', room.id),
            'total_cost': '{0:.2f}'.format(room.price * count_booking_days),
            'count_booking_days': count_booking_days,}

    def get(self):
        try:
            from_date, to_date = self._get_booking_date()
            count_booking_days = (to_date - from_date).days
        except ValueError as e:
            self.set_response(dict(message=str(e)), status=400)
            return
        queryset = Room.find_available_between_dates(from_date.isoformat(), to_date.isoformat())
        rooms = map(lambda room: model_to_dict(
            room,
            append_attrs=self._prepare_addition_attrs(room, count_booking_days)
        ), queryset)
        self.set_response(dict(rooms=rooms))

    # need check auth
    def post(self):
        data = json_decode(self.request.body)
        schema = {
            # TODO get customer_id from session
            # and set like an additional(not required) field
            # if auth user is booking a room for third-part person
            'customer_id': {
                'type': 'integer',
                'required': True},
            'room_id': {
                'type': 'integer',
                'required': True},
            'from_date': {
                'type': 'string',
                'required': True},
            'to_date': {
                'type': 'string',
                'required': True},
        }
        if not self.valid_data(schema, data):
            return

        customer_id = data['customer_id']
        room_id = data['room_id']
        from_date = parse_date(data['from_date'])
        to_date = parse_date(data['to_date'])

        room = Room.get_available_between_dates_by_id(room_id, from_date.isoformat(), to_date.isoformat())

        if not room:
            self.set_response(
                content={'message': ('The room with id {} is not available '
                                     'for booking from {} to {}').format(room_id, from_date, to_date)},
                status=404)
            return

        # TODO add payment system
        # change on next step with payment system
        status = Status.get(name='reserved')

        # TODO get customer_id from session
        try:
            customer = Customer.get(id=customer_id)
        except Customer.DoesNotExist:
            self.set_response(
                {'message': 'Customer with id {} not found'.format(customer_id)},
                status=400)
            return

        booking = Booking.create(
            room=room,
            customer=customer,
            from_date=from_date,
            to_date=to_date,
            status=status)
        self.set_response(
            content=dict(booking=model_to_dict(booking)),
            status=201,
            headers={'Location': self.reverse_url('booking', booking.id)}
        )


class BookingOrderHandler(BookingHandler):
    # need check auth
    def get(self, booking_id):
        try:
            booking = Booking.get(id=booking_id)
            booking = model_to_dict(
                booking,
            )
            self.set_response(dict(booking=booking))
        except Booking.DoesNotExist:
            self.set_response(
                {'message': 'Booking with id {} not found'.format(booking_id)},
                status=404)

    # Booking instance only can create and get
    # if need change same data, need create new booking
    # because it is violation of data billing integrity if change dates etc.
    def put(self, *args, **kwargs):
        raise HTTPError(405)

    # need resolve conflict if booking has status paid and booking is still actuality
    def delete(self, booking_id):
        raise HTTPError(405)


class RoomsHandler(BaseHandler):
    def get(self):
        fields = self.get_only_fields()
        roomsset = Room.select()
        rooms = map(lambda room: model_to_dict(
            room,
            append_attrs={'url': self.reverse_url('room', room.id)},
            only=fields
        ), roomsset)
        self.set_response(dict(rooms=rooms))

    # need check auth
    def post(self):
        data = json_decode(self.request.body)
        schema = {
            'type': {
                'type': 'integer',
                'required': True},
            'price': {
                'type': 'float',
                'required': True},
            'options': {
                'type': 'string'}
        }
        if not self.valid_data(schema, data):
            return
        room = Room.create(**data)
        self.set_response(
            content=dict(room=model_to_dict(room)),
            status=201,
            headers={'Location': self.reverse_url('room', room.id)})


class RoomHandler(BaseHandler):
    def get(self, room_id):
        fields = self.get_only_fields()
        try:
            room = model_to_dict(
                Room.get(id=room_id),
                only=fields)
            self.set_response(dict(room=room))
        except Room.DoesNotExist:
            self.set_response(
                {'message': 'A room with id #{} not found'.format(room_id)},
                status=404)

    # For implementing PUT method need to make separate tables for prices and costs
    def put(self, room_id):
        raise HTTPError(405)

    # For implementing DELETE need resolving conflicts
    # when delete room which was paid and booking is still actuality
    def delete(self, room_id):
       raise HTTPError(405)


class RoomCustomersHandler(BaseHandler):
    def get(self, room_id):
        try:
            room = Room.get(id=room_id)
            customers = Customer.select().join(Booking).join(Room).where(Room.id == room_id)
            customers = map(lambda customer: model_to_dict(
                customer,
                append_attrs={'url': self.reverse_url('customer', customer.id)}),
                customers)
            room = model_to_dict(
                room,
                append_attrs=dict(customers=customers)
                )
            self.set_response(dict(room=room))
        except Room.DoesNotExist:
            self.set_response(
                {'message': 'A room with id #{} not found'.format(room_id)},
                status=404)


class RoomBookingHandler(BaseHandler):
    def get(self, room_id):
        try:
            room = Room.get(id=room_id)
            booking = Booking.select().where(Booking.room_id == room_id)
            booking = map(lambda item: model_to_dict(
                item,
                append_attrs={'url': self.reverse_url('booking_order', item.id)},
                exclude=[Booking.room]),
                booking)
            room = model_to_dict(
                room,
                append_attrs=dict(booking=booking)
                )
            self.set_response(dict(room=room))
        except Room.DoesNotExist:
            self.set_response(
                {'message': 'A room with id #{} not found'.format(room_id)},
                status=404)


class CustomersHandler(BaseHandler):
    def get(self):
        fields = self.get_only_fields()
        customers = Customer.select()
        customers = map(lambda customer: model_to_dict(
            customer,
            append_attrs={'url': self.reverse_url('customer', customer.id)},
            only=fields
        ), customers)
        self.set_response(dict(customers=customers))

    def post(self):
        data = json_decode(self.request.body)
        scheme = {
            'name': {
                'type': 'string',
                'required': True},
            'passport': {
                'type': 'string',
                'required': True}}
        if not self.valid_data(scheme, data):
            return
        try:
            customer = Customer.create(**data)
            self.set_response(
                content=dict(customer=model_to_dict(customer)),
                status=201,
                headers={'Location': self.reverse_url('customer', customer.id)})
        except peewee.IntegrityError:
            self.set_response(
                content={'message': 'Customer with passport code {} already exists'.format(data['passport'])},
                status=409)


class CustomerHandler(BaseHandler):
    def get(self, customer_id):
        fields = self.get_only_fields()
        try:
            customer = model_to_dict(
                Customer.get(id=customer_id),
                only=fields)
            self.set_response(dict(customer=customer))
        except Customer.DoesNotExist:
            self.set_response(
                {'message': 'A customer with id #{} not found'.format(customer_id)},
                status=404)

    def put(self, customer_id):
        data = json_decode(self.request.body)
        scheme = {
            'name': {
                'type': 'string'},
            'passport': {
                'type': 'string'}}
        if not self.valid_data(scheme, data):
            return
        try:
            customer = Customer.get(id=customer_id)
            if 'name' in data:
                customer.name = data['name']
            if 'passport' in data:
                customer.passport = data['pasport']
            customer.save()
            self.set_response(
                content=dict(customer=model_to_dict(customer)),
                status=200,
                headers={'Location': self.reverse_url('customer', customer.id)})
        except Customer.DoesNotExist:
            self.set_response(
                {'message': 'A customer with id #{} not found'.format(customer_id)},
                status=404)

    # for implementing DELETE need resolving conflicts
    # when delete customer had been booking and paid room and booking is still actuality
    def delete(self, customer_id):
        raise HTTPError(405)


class CustomerBookingHandler(BaseHandler):
    def get(self, customer_id):
        fields = self.get_only_fields()
        try:
            booking = Booking.select().where(Booking.customer_id == customer_id)
            booking = map(lambda item: model_to_dict(
                item,
                append_attrs={'url': self.reverse_url('booking_order', item.id)},
                exclude=[Booking.customer]),
                booking)
            customer = model_to_dict(
                Customer.get(id=customer_id),
                append_attrs=dict(booking=booking),
                only=fields)
            self.set_response(dict(customer=customer))
        except Customer.DoesNotExist:
            self.set_response(
                {'message': 'A customer with id #{} not found'.format(customer_id)},
                status=404)


class CustomerRoomsHandler(BaseHandler):
    def get(self, customer_id):
        fields = self.get_only_fields()
        try:
            rooms = Room.select().join(Booking).where(Booking.customer_id == customer_id)
            rooms = map(lambda item: model_to_dict(
                item,
                append_attrs={'url': self.reverse_url('room', item.id)},
                exclude=[Booking.customer]),
                rooms)
            customer = model_to_dict(
                Customer.get(id=customer_id),
                append_attrs=dict(rooms=rooms),
                only=fields)
            self.set_response(dict(customer=customer))
        except Customer.DoesNotExist:
            self.set_response(
                {'message': 'A customer with id #{} not found'.format(customer_id)},
                status=404)


class StatusesHandler(BaseHandler):
    def get(self):
        statuses = list(Status.select().dicts())
        self.set_response(dict(statuses=statuses))


class TypesHandler(BaseHandler):
    def get(self):
        types = list(Type.select().dicts())
        self.set_response(dict(types=types))
