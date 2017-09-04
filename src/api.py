import re
import tornado.httpserver
import tornado.ioloop
import tornado.web


from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler, URLSpec as URL

import handlers as hndlrs
define('port', default=8080, type=int)


class App(Application):
    def __init__(self):
        handlers = [
            URL(r'/', hndlrs.RoomGuestsHandler, name='room_guests'),
            URL(r'/api/v1/rooms/(?P<room_id>\d+)/status/', hndlrs.RoomStatusHandler, name='room_status'),
            URL(r'/api/v1/rooms/(?P<room_id>\d+)/type/', hndlrs.RoomTypeHandler, name='room_type'),
            URL(r'/api/v1/rooms/(?P<room_id>\d+)/', hndlrs.RoomsHandler, name='room'),
            URL(r'/api/v1/rooms/statuses/', hndlrs.RoomsStatusesHandler, name='room_statuses'),
            URL(r'/api/v1/rooms/types/', hndlrs.RoomsTypesHandler, name='room_types'),
            URL(r'/api/v1/rooms/', hndlrs.RoomsHandler, name='rooms'),
            URL(r'/api/v1/guests/(?P<guest_id>\d+)/', hndlrs.GuestsHandler, name='guest'),
            URL(r'/api/v1/guests/', hndlrs.GuestsHandler, name='guests'),
        ]
        settings = dict(
            debug=True
        )
        Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(App())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()        
    