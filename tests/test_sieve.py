import unittest

from flask import Flask

from flask_sieve import Sieve
from flask_sieve.exceptions import ValidationException


class TestSieve(unittest.TestCase):
    def test_registers_error_handler(self):
        app = Flask(__name__)
        Sieve(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertIn('Test error', str(response.get_json()))

    def test_deferring_registration_of_error_handler(self):
        app = Flask(__name__)
        s = Sieve()

        s.init_app(app)

        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertIn('Test error', str(response.get_json()))
