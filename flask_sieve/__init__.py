from .requests import JsonRequest, FormRequest
from .validator import validate, Validator
from .exceptions import ValidationException, register_error_handler


class Sieve:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        register_error_handler(app)
