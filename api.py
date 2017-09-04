from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, URLSpec as url

from handlers import (BookingHandler, BookingOrderHandler, RoomsHandler,
                      RoomHandler, RoomCustomersHandler, RoomBookingHandler,
                      CustomerHandler, CustomersHandler, CustomerBookingHandler,
                      CustomerRoomsHandler, StatusesHandler, TypesHandler)

define('port', default=8080, type=int)


class HotelAPIApp(Application):
    def __init__(self):
        handlers = [
            # TODO should implementing func that add prefix like /api/v1/ to all subroutes in one place
            url(r'/api/v1/rooms/(?P<room_id>\d+)/', RoomHandler, name='room'),
            url(r'/api/v1/rooms/(?P<room_id>\d+)/customers/', RoomCustomersHandler, name='room_customers'),
            url(r'/api/v1/rooms/(?P<room_id>\d+)/booking/', RoomBookingHandler, name='room_booking'),
            url(r'/api/v1/rooms/', RoomsHandler, name='rooms'),
            url(r'/api/v1/booking/', BookingHandler, name='booking'),
            url(r'/api/v1/booking/(?P<booking_id>\d+)/', BookingOrderHandler, name='booking_order'),
            url(r'/api/v1/customers/(?P<customer_id>\d+)/', CustomerHandler, name='customer'),
            url(r'/api/v1/customers/(?P<customer_id>\d+)/booking/', CustomerBookingHandler, name='customer_booking'),
            url(r'/api/v1/customers/(?P<customer_id>\d+)/rooms/', CustomerRoomsHandler, name='customer_rooms'),
            url(r'/api/v1/customers/', CustomersHandler, name='customers'),
            url(r'/api/v1/statuses/', StatusesHandler, name='statuses'),
            url(r'/api/v1/types/', TypesHandler, name='types')
        ]
        settings = dict(
            debug=True,
        )
        Application.__init__(self, handlers, **settings)


def main():
    http_server = HTTPServer(HotelAPIApp())
    http_server.listen(options.port)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
