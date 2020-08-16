from flask import request as flask_request

from flask_sieve.validator import Validator
from flask_sieve.exceptions import ValidationException


class FormRequest:
    def __init__(self, request=None):
        request = request or flask_request
        self._validator = Validator(rules=self.rules(), request=request)
        self._validator.set_custom_messages(self.messages())
        self._validator.set_custom_handlers(self.custom_handlers())

    def validate(self):
        if self._validator.fails():
            raise ValidationException(self._validator.messages())
        return True

    @staticmethod
    def messages():
        return {}

    @staticmethod
    def custom_handlers():
        return {}


class JsonRequest(FormRequest):
    def __init__(self, request=None):
        request = request or flask_request
        if not request.is_json:
            raise ValidationException({'request': 'Request must be valid JSON'})
        self._validator = Validator(rules=self.rules(), request=request)

