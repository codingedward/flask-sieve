from .requests import JsonRequest, FormRequest
from .validator import validate, Validator
from .exceptions import ValidationException, register_error_handler

class Sieve:
    def __init__(self, app):
        register_error_handler(app)
