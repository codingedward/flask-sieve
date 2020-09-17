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
        app.config['SIEVE_INVALID_STATUS_CODE'] = 422
        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(422, status)
        self.assertIn('Test error', str(response.get_json()))

    def test_configuring_response_message(self):
        app = Flask(__name__)
        msg = "Only Chuck Norris can submit invalid data!"
        app.config['SIEVE_RESPONSE_MESSAGE'] = msg
        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertIn(msg, str(response.get_json()))

    def test_keeping_success_message(self):
        app = Flask(__name__)
        app.config['SIEVE_INCLUDE_SUCCESS_KEY'] = True

        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertTrue('success' in response.get_json())

    def test_keeping_removing_message(self):
        app = Flask(__name__)
        app.config['SIEVE_INCLUDE_SUCCESS_KEY'] = False

        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertFalse('success' in response.get_json())

    def test_wrapping_response_with_data(self):
        app = Flask(__name__)
        app.config['SIEVE_RESPONSE_WRAPPER'] = 'data'

        register_error_handler(app)
        self.assertIn(ValidationException, app.error_handler_spec[None][None])
        errors = {'field': 'Test error'}

        with app.app_context():
            response, status = app.error_handler_spec[None][None][ValidationException](
                ValidationException(errors)
            )
        self.assertEqual(400, status)
        self.assertIn('Test error', str(response.get_json()))
        self.assertTrue('data' in response.get_json())

    def test_wrapping_response_without_data(self):
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
        self.assertFalse('data' in response.get_json())
        self.assertTrue('errors' in response.get_json())
