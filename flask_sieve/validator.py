from functools import wraps

from flask_sieve.parser import Parser
from flask_sieve.translator import Translator
from flask_sieve.rules_processor import RulesProcessor


class Validator:
    def __init__(self, request=None, rules=None):
        self._parser = Parser()
        self._translator = Translator()
        self._processor = RulesProcessor()
        self._rules = rules or {}
        self._request = request or {}

    def set_rules(self, rules):
        self._rules = rules

    def set_request(self, request):
        self._request = request

    def set_custom_messages(self, messages):
        self._translator.set_custom_messages(messages)

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


def validate(Request):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            req = Request()
            req.validate()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
