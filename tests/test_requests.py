import unittest

from werkzeug.datastructures import MultiDict

from flask_sieve.requests import FormRequest, JsonRequest
from flask_sieve.exceptions import ValidationException

class FormMockRequest:
    def __init__(self, data=None):
        data = data or {}
        self.form = MultiDict([(k, v) for k, v in data.items()])
        self.files = MultiDict([])
        self.is_json = False


class JsonMockRequest:
    def __init__(self, data=None):
        self.json = data or {}
        self.is_json = True

class TestFormRequest(FormRequest):
    @staticmethod
    def rules():
        return {
            'name': ['required', 'string', 'min:6'],
            'email':['required', 'email'],
            'password': ['required', 'min:8', 'confirmed']
        }


class TestJsonRequest(JsonRequest):
    @staticmethod
    def rules():
        return {
            'name': ['required', 'string', 'min:6'],
            'email': ['required', 'email'],
            'password': ['required', 'min:8', 'confirmed']
        }


class TestRequests(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'John Doe',
            'email': 'john@doe.com',
            'password': 'john_doe',
            'password_confirmation': 'john_doe',
        }
        self.invalid_data = {
            'name': 'John',
            'email': 'johndoe.com',
            'password': 'johh_doe',
        }

    def test_form_request_fails(self):
        request = FormMockRequest(self.invalid_data)
        form_request = TestFormRequest(request)
        with self.assertRaises(ValidationException):
            form_request.validate()

    def test_form_request_passes(self):
        request = FormMockRequest(self.valid_data)
        form_request = TestFormRequest(request)
        self.assertTrue(form_request.validate())

    def test_json_request_fails(self):
        request = JsonMockRequest(self.invalid_data)
        json_request = TestJsonRequest(request=request)
        with self.assertRaises(ValidationException):
            json_request.validate()

    def test_json_request_passes(self):
        request = JsonMockRequest(self.valid_data)
        json_request = TestJsonRequest(request=request)
        self.assertTrue(json_request.validate())

    def test_json_request_checks_is_json(self):
        request = FormMockRequest(self.invalid_data)
        with self.assertRaises(ValidationException):
            TestJsonRequest(request=request)
