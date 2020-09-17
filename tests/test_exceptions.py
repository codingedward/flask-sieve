import unittest

from flask import Flask

from flask_sieve.exceptions import ValidationException, register_error_handler


class TestErrorHandler(unittest.TestCase):
    def test_error_handler(self):
        app = Flask(__name__)
        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertIn('Test error', str(response.get_json()))

    def test_configurable_status_code(self):
        app = Flask(__name__)
        app.config['SIEVE_INVALID_STATUS_CODE'] = 422;
        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(422, status)
        self.assertIn('Test error', str(response.get_json()))
