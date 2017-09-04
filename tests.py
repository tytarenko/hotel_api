import unittest

from tornado.escape import json_encode
from tornado.testing import AsyncHTTPTestCase

from api import HotelAPIApp


class ApiTestCase(AsyncHTTPTestCase):
    def get_app(self):
        self.app = HotelAPIApp()
        return self.app


class RoomsTestCase(ApiTestCase):
    def test_get_rooms_should_return_200(self):
        response = self.fetch('/api/v1/rooms/')
        self.assertEqual(response.code, 200)

    def test_room_with_id_1_it_should_return_200(self):
        response = self.fetch('/api/v1/rooms/1/')
        self.assertEqual(response.code, 200)

    def test_room_with_id_1_and_customers_it_should_return_200(self):
        response = self.fetch('/api/v1/rooms/1/customers/')
        self.assertEqual(response.code, 200)

    def test_room_with_id_1_and_booking_it_should_return_200(self):
        response = self.fetch('/api/v1/rooms/1/booking/')
        self.assertEqual(response.code, 200)

    def test_room_with_id_100_it_should_return_404(self):
        response = self.fetch('/api/v1/rooms/100/')
        self.assertEqual(response.code, 404)

    def test_create_new_room_should_return_201(self):
        body = json_encode({'type': 1, 'price': 123.12, 'options': 'test options'})
        response = self.fetch('/api/v1/rooms/', method="POST", body=body)
        self.assertEqual(response.code, 201)

    def test_update_exists_room_should_return_405(self):
        body = json_encode({'type': 1, 'price': 123.12, 'options': 'test options'})
        response = self.fetch('/api/v1/rooms/1/', method="POST", body=body)
        self.assertEqual(response.code, 405)

    def test_create_new_room_with_incorrect_params_it_should_return_400(self):
        body = json_encode({'type': 1})
        response = self.fetch('/api/v1/rooms/', method="POST", body=body)
        self.assertEqual(response.code, 400)

    def test_delete_room_with_id_1_it_should_return_405(self):
        response = self.fetch('/api/v1/rooms/1/', method="DELETE")
        self.assertEqual(response.code, 405)


class CustomersTestCase(ApiTestCase):
    def test_get_customers_it_should_return_200(self):
        response = self.fetch('/api/v1/customers/')
        self.assertEqual(response.code, 200)

    def test_get_customer_with_id_1_it_should_return_200(self):
        response = self.fetch('/api/v1/customers/1/')
        self.assertEqual(response.code, 200)

    def test_get_customer_with_id_1_and_rooms_it_should_return_200(self):
        response = self.fetch('/api/v1/customers/1/rooms/')
        self.assertEqual(response.code, 200)

    def test_get_customer_with_id_1_and_booking_it_should_return_200(self):
        response = self.fetch('/api/v1/customers/1/rooms/')
        self.assertEqual(response.code, 200)

    def test_create_new_customer_it_should_return_201(self):
        body = json_encode({'name': 'John Dou', 'passport': '1Q2W3E4R5T6Y'})
        response = self.fetch('/api/v1/customers/', method="POST", body=body)
        self.assertEqual(response.code, 201)

    def test_create_new_customer_with_exists_passport_number_it_should_return_409(self):
        body = json_encode({'name': 'John Dou', 'passport': '1Q2W3E4R5T6Y'})
        response = self.fetch('/api/v1/customers/', method="POST", body=body)
        self.assertEqual(response.code, 409)

    def test_create_new_customer_with_incorrect_params_it_should_return_400(self):
        body = json_encode({'name': 'John Dou'})
        response = self.fetch('/api/v1/customers/', method="POST", body=body)
        self.assertEqual(response.code, 400)

    def test_update_exists_customer_should_return_405(self):
        body = json_encode({'name': 'John Dou', 'passport': '1Q2W3E4R5T6Y'})
        response = self.fetch('/api/v1/customers/1/', method="POST", body=body)
        self.assertEqual(response.code, 405)

    def test_delete_exists_customer_with_id_1_it_should_return_405(self):
        response = self.fetch('/api/v1/customers/1/', method="DELETE")
        self.assertEqual(response.code, 405)


if __name__ == '__main__':
    unittest.main()
