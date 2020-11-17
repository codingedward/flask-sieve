from functools import wraps

from flask import request as flask_request

from flask_sieve.parser import Parser
from flask_sieve.translator import Translator
from flask_sieve.rules_processor import RulesProcessor


class Validator:
    def __init__(self, rules=None, request=None, custom_handlers=None,
            messages=None, **kwargs):
        self._parser = Parser()
        self._translator = Translator(custom_messages=messages)
        self._processor = RulesProcessor()
        self._rules = rules or {}
        self._custom_handlers = custom_handlers or {}
        self._request = self._parse_request(request or {})

    def set_rules(self, rules):
        self._rules = rules

    def set_request(self, request):
        self._request = self._parse_request(request or {})

    def set_custom_messages(self, messages):
        self._translator.set_custom_messages(messages)

    def set_custom_handlers(self, handlers):
        for handler in handlers:
            self.register_rule_handler(**handler)

    def register_rule_handler(self, handler, message, params_count=0):
        if not handler.__name__.startswith('validate_'):
            raise ValueError(
                'Rule handlers must start with "validate_" name, %s provided'
                % (handler.__name__)
            )
        self._processor.register_rule_handler(
            handler=handler,
            message=message,
            params_count=params_count
        )
        handler_messages = {}
        for handler_name, handler_dict in self._processor.custom_handlers().items():
            handler_messages[handler_name[len('validate_'):]] = handler_dict['message']
        self._translator.set_handler_messages(handler_messages)

    def fails(self):
        return not self.passes()

    def passes(self):
        self._parser.set_rules(self._rules)
        self._processor.set_rules(self._parser.parsed_rules())
        self._processor.set_request(self._request)
        return self._processor.passes()

    def messages(self):
        self._translator.set_validations(self._processor.validations())
        return self._translator.translated_errors()

    @staticmethod
    def _parse_request(request):
        if isinstance(request, dict):
            return request
        # instance of flask.request ...
        if request.is_json:
            return request.json
        dict_request = {}
        dict_request.update(request.form.to_dict(flat=True))
        dict_request.update(request.files.to_dict(flat=True))
        return dict_request


def validate(Request):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            req = Request()
            req.validate()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
