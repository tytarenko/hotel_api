import functools

from cerberus import Validator
from tornado.escape import json_decode
from tornado.web import RequestHandler

import models
from paginators import Paginator


class BaseHandler(RequestHandler):
    def formate_room(self, room, with_guests=False):
        if not with_guests:
            guests = self.get_guests_url(room.id)
        else:
            self.formate_guest = functools.partial(self.formate_guest, recurse=False, exclude=[models.Guest.room])
            guests = map(self.formate_guest, room.guests.select())
        formatted_room = room.as_dict()
        formatted_room.update(dict(
            url=self.get_room_url(room.id),
            guests=guests))
        return formatted_room

    def formmated_guest(self, guest, recurse=True, exclude=None):
        formatted_guest = guest.as_dict(recurse=recurse, exclude=exclude)
        formatted_guest['url'] = self.get_guest_url(guest.id)
        return formatted_guest

    # response helper
    def set_response(self, response=None, status=None, headers=None):
        if headers:
            for key, value in headers.items():
                self.set_header(key, value)
        if status:
            self.set_status(status)
        if response:
            self.write(response)

            # validating helper

    def valid_data(self, schema, data):
        validator = Validator(schema)
        if validator.validate(data):
            return True
        self.set_response(
            response={'message': 'incorrect params: {}'.format(validator.errors)},
            status=400)
        return False

    # url helpers
    def get_full_url(self, url):
        return '{}://{}{}'.format(self.request.protocol, self.request.host, url)

    def get_room_url(self, room_id):
        return self.get_full_url(self.reverse_url('room', room_id))

    def get_guests_url(self, room_id):
        return self.get_full_url(self.reverse_url('room_guests', room_id))

    def get_guest_url(self, guest_id):
        return self.get_full_url(self.reverse_url('guest', guest_id))

    def get_current_url(self):
        return self.get_full_url(self.request.uri)


class RoomsHandler(BaseHandler):
    post_schema = {
        'type': {
            'type': 'integer',
            'required': True},
        'status': {
            'type': 'integer'}}

    put_schema = {
        'type': {
            'type': 'integer'},
        'status': {
            'type': 'integer'}}

    def get(self, room_id=None):
        ############################
        # TODO 1
        ############################
        with_guests = bool(self.get_argument('with_guests', False))
        page = int(self.get_argument('page', 1))
        count_per_page = int(self.get_argument('count', 10))
        # if room_id is not None:
        #     try:
        #         room = models.Room.get(id=room_id)
        #         self.set_response(response={'room': self.formate_room(room, with_guests=with_guests)})
        #         return
        #     except models.Room.DoesNotExist:
        #         self.set_response(
        #             response={'message': 'A room with id #{} not found'.format(room_id)},
        #             status=404)
        #         return
        self.formate_room = functools.partial(self.formate_room, with_guests=with_guests)
        rooms = map(self.formate_room, models.Room.select().paginate(page, count_per_page))
        ############################
        # TODO 2
        ############################
        # paginator = Paginator(models.Room, self.get_current_url(), page, count_per_page)
        self.set_response(response=dict(
            rooms=rooms,
        ))

    def post(self):
        data = json_decode(self.request.body)
        if not self.valid_data(self.schema, data):
            return
        room = models.Room.create(**data)
        self.set_response(
            response={'room': self.formate_room(room)},
            status=201,
            headers={'Location': self.get_room_url(room.id)})

    def put(self, room_id):
        try:
            data = json_decode(self.request.body)
            if not self.valid_data(self.schema, data):
                return
            models.Room.update(**data).where(models.Room.id == room_id).execute()
            room = models.Room.get(id=room_id)
            self.set_response(
                response={'room': self.formate_room(room)},
                status=200,
                headers={'Location': self.get_room_url(room.id)})
        except models.Room.DoesNotExist:
            self.set_response(
                response={'message': 'A room with id #{} not found'.format(room_id)},
                status=404)

    def delete(self, room_id):
        try:
            room = models.Room.get(id=room_id)
            ############################
            # TODO 3
            ############################
            if room.guests.exists():
                self.set_response(
                    response={
                        'message': 'Cannot delete room with guests. At first, need to unlink guests from the room.'},
                    status=409)
                return
            room.delete_instance()
            self.set_response(status=204)
        except models.Room.DoesNotExist:
            self.set_response(
                response={'message': 'A room with id #{} not found'.format(room_id)},
                status=404)


class RoomGuestsHandler(BaseHandler):
    def get(self, room_id):
        room = models.Room.get(id=room_id)
        self.formate_guest = functools.partial(self.formate_guest, recurse=False, exclude=[models.Guest.room])
        self.set_response(response={'guests': map(self.formate_guest, room.guests.select())})


class RoomStatusHandler(BaseHandler):
    def get(self, room_id):
        room = models.Room.get(id=room_id)
        self.set_response(response={'status': room.status})


class RoomTypeHandler(BaseHandler):
    def get(self, room_id):
        room = models.Room.get(id=room_id)
        self.set_response(response={'type': room.type})


class RoomsStatusesHandler(BaseHandler):
    def get(self):
        self.set_response(response={'statuses': dict(models.Room.STATUSES)})


class RoomsTypesHandler(BaseHandler):
    def get(self):
        self.set_response(response={'types': dict(models.Room.TYPES)})


class GuestsHandler(BaseHandler):
    post_schema = {
        'name': {
            'type': 'string',
            'required': True},
        'room': {
            'type': 'integer'}}

    put_schema = {
        'name': {
            'type': 'string'},
        'room': {
            'type': 'integer'}}

    def get(self, guest_id=None):
        if guest_id:
            try:
                guest = models.Guest.get(id=guest_id)
                formatted_guest = self.formate_guest(guest, recurse=False, exclude=[models.Guest.room])
                room_id = guest.room.id
                formatted_guest.update(dict(
                    room_url=self.get_room_url(room_id),
                    room=room_id))
                self.set_response(response={'guest': formatted_guest})
                return
            except models.Guest.DoesNotExist:
                self.set_response(
                    response={'message': 'The guest with id #{} not found'.format(guest_id)},
                    status=404)
                return
        page = int(self.get_argument('page', 1))
        count_per_page = int(self.get_argument('count', 10))
        guests = map(self.formate_guest, models.Guest.select().paginate(page, count_per_page))
        paginator = Paginator(models.Guest, self.get_current_url(), page, count_per_page)
        self.set_response(response=dict(
            guests=guests,
            **paginator.get_pagination()
        ))

    def post(self):
        data = json_decode(self.request.body)
        if not self.valid_data(self.post_schema, data):
            return
        try:
            models.Room.exists(id=data.get('room'))
        except models.Room.DoesNotExist:
            self.set_response(
                response={
                    'message': "incorrect params: {'room': ['room with id #{} not found']}".format(data.get('room'))},
                status=400)
            return
        guest = models.Guest.create(**data)
        self.set_response(
            response={'guest': self.formate_guest(guest)},
            status=201,
            headers={'Location': self.get_guest_url(guest.id)})

    def put(self, guest_id):
        try:
            data = json_decode(self.request.body)
            if not self.valid_data(self.put_schema, data):
                return
            ############################
            # TODO 4
            ############################
            # check count guests in room.
            # Cannot to settle in the room more guests than in the room space
            if 'room' in data:
                try:
                    room = models.Room.get(id=data.get('room'))
                    if room.type > len(room.guests.select()):
                        data['room'] = room
                    else:
                        # Code of 409 conflict
                        self.set_response(status=409)
                        return
                except models.Room.DoesNotExist:
                    self.set_response(
                        response={'message': "incorrect params: {'room': ['room with id #{} not found']}".format(
                            data.get('room'))},
                        status=400)
                    return
            models.Guest.update(**data).where(models.Guest.id == guest_id).execute()
            guest = models.Guest.get(id=guest_id)
            self.set_response(
                response={'guest': self.formate_guest(guest)},
                status=200,
                headers={'Location': self.get_guest_url(guest_id)})
        except models.Guest.DoesNotExist:
            self.set_response(
                response={'message': 'The guest with id #{} not found'.format(guest_id)},
                status=404)

    def delete(self, guest_id):
        try:
            guest = models.Guest.get(id=guest_id)
            guest.delete_instance()
            self.set_response(status=204)
        except models.Guest.DoesNotExist:
            self.set_response(
                response={'message': 'The guest with id #{} not found'.format(guest_id)},
                status=404)
