from __future__ import absolute_import
import os
import re
import sys
import ast
import json
import pytz
import operator
import requests
import filetype

from PIL import Image
from dateutil.parser import parse as dateparse
from werkzeug.datastructures import FileStorage


class RulesProcessor:
    def __init__(self, app=None, rules=None, request=None):
        self._app = app
        self._rules = rules or {}
        self._request = request or {}
        self._custom_handlers = {}
        self._attributes_validations = {}

    def validations(self):
        return self._attributes_validations

    def fails(self):
        return not self.passes()

    def custom_handlers(self):
        return self._custom_handlers

    def passes(self):
        passes = True
        self._attributes_validations = {}
        for attribute, rules in self._rules.items():
            should_bail = self._has_rule(rules, 'bail')
            nullable = self._has_rule(rules, 'nullable')
            validations = []
            for rule in rules:
                handler = self._get_rule_handler(rule['name'])
                value = self._attribute_value(attribute)
                attr_type = self._get_type(value, rules)
                is_valid = False
                if value is None and nullable:
                    is_valid = True
                else:
                    is_valid = handler(
                        value=value,
                        attribute=attribute,
                        params=rule['params'],
                        nullable=nullable,
                        rules=rules
                    )

                validations.append({
                    'attribute': attribute,
                    'rule': rule['name'],
                    'is_valid': is_valid,
                    'attribute_type': attr_type,
                    'params': rule['params'],
                })
                if not is_valid:
                    passes = False
                    if should_bail:
                        self._attributes_validations[attribute] = validations
                        return False
            self._attributes_validations[attribute] = validations
        return passes

    def set_rules(self, rules):
        self._rules = rules

    def set_request(self, request):
        self._request = request

    def register_rule_handler(self, handler, message, params_count=0):
        # add a params count check wrapper
        def checked_handler(*args, **kwargs):
            self._assert_params_size(
                size=params_count,
                params=kwargs['params'],
                rule=('custom rule %s' % (handler.__name__,))
            )
            return handler(*args, **kwargs)

        self._custom_handlers[handler.__name__] = {
            'handler': checked_handler,
            'message': message or ('%s check failed' % (handler.__name__,))
        }

    @staticmethod
    def validate_accepted(value, **kwargs):
        return value in [ 1, '1', 'true', 'yes', 'on', True]

    def validate_active_url(self, value, **kwargs):
        return self._can_call_with_method(requests.options, value)

    def validate_after(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after')
        return self._compare_dates(value, params[0], operator.gt)

    def validate_after_or_equal(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after_or_equal')
        return self._compare_dates(value, params[0], operator.ge)

    @staticmethod
    def validate_alpha(value, **kwargs):
        if not value:
            return False
        value = str(value).replace(' ', '')
        return value.isalpha()

    @staticmethod
    def validate_alpha_dash(value, **kwargs):
        if not value:
            return False
        value = str(value)
        acceptables = [ ' ', '-', '_' ]
        for acceptable in acceptables:
            value = value.replace(acceptable, '')
        return value.isalpha()

    @staticmethod
    def validate_alpha_num(value, **kwargs):
        if not value:
            return False
        value = str(value).replace(' ', '')
        return value.isalnum()

    @staticmethod
    def validate_array(value, **kwargs):
        try:
            return isinstance(ast.literal_eval(str(value)), list)
        except (ValueError, SyntaxError):
            return False

    @staticmethod
    def validate_bail(**kwargs):
        return True

    def validate_before(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='before')
        return self._compare_dates(value, params[0], operator.lt)

    def validate_before_or_equal(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='before_or_equal')
        return self._compare_dates(value, params[0], operator.le)

    def validate_between(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='between')
        value = self._get_size(value)
        lower = self._get_size(params[0])
        upper = self._get_size(params[1])
        return lower <= value and value <= upper

    @staticmethod
    def validate_boolean(value, **kwargs):
        return value in [True, False, 1, 0, '0', '1']

    def validate_confirmed(self, value, attribute, **kwargs):
        return value == self._attribute_value(attribute + '_confirmation')

    def validate_date(self, value, **kwargs):
        return self._can_call_with_method(dateparse, value)

    def validate_date_equals(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='date_equals')
        return self._compare_dates(value, params[0], operator.eq)

    def validate_different(self, value, attribute, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='different')
        return value != self._attribute_value(params[0])

    def validate_digits(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='digits')
        self._assert_with_method(int, params[0])
        size = int(params[0])
        is_numeric = self.validate_numeric(value)
        return is_numeric and len(str(value).replace('.', '')) == size

    def validate_digits_between(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='digits_between')
        self._assert_with_method(int, params[0])
        self._assert_with_method(int, params[1])
        lower = int(params[0])
        upper = int(params[1])
        is_numeric = self.validate_numeric(value)
        value_len = len(str(value).replace('.', ''))
        return is_numeric and lower <= value_len and value_len <= upper

    def validate_dimensions(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='dimensions')
        if not self.validate_image(value):
            return False
        try:
            image = Image.open(value)
            w, h = image.size
            value.seek(0)
            return ('%dx%d' % (w, h)) == params[0]
        except Exception:
            return False

    @staticmethod
    def validate_distinct(value, **kwargs):
        try:
            lst = ast.literal_eval(str(value))
            if not isinstance(lst, list):
                return False
            return len(set(lst)) == len(lst)
        except (ValueError, SyntaxError):
            return False

    @staticmethod
    def validate_email(value, **kwargs):
        pattern = re.compile("""
            ^
            [a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]
            +@[a-zA-Z0-9]
            (?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?
            (?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(str(value)) is not None

    @staticmethod
    def validate_exists(value, **kwargs):
        return False

    def validate_extension(self, value, params, **kwargs):
        if not self.validate_file(value):
            return False
        self._assert_params_size(size=1, params=params, rule='extension')
        kind = filetype.guess(value.stream.read(512))
        value.seek(0)
        if kind is None:
            return value.filename.split('.')[-1].lower() == params[0]
        return kind.extension in params

    @staticmethod
    def validate_file(value, **kwargs):
        return isinstance(value, FileStorage)

    def validate_filled(self, value, attribute, nullable, **kwargs):
        if self.validate_present(attribute):
            return self.validate_required(value, attribute, nullable)
        return True

    def validate_gt(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gt')
        value = self._get_size(value)
        upper = self._get_size(self._attribute_value(params[0]))
        return value > upper

    def validate_gte(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gte')
        value = self._get_size(value)
        upper = self._get_size(self._attribute_value(params[0]))
        return value >= upper

    def validate_image(self, value, **kwargs):
        if not self.validate_file(value):
            return False
        ext = value.filename.split('.')[-1]
        return ext in ['jpg', 'jpeg', 'gif', 'png', 'bmp', 'svg', 'tiff', 'tif']

    @staticmethod
    def validate_in(value, params, **kwargs):
        return value in params

    def validate_in_array(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='in_array')
        other_value = self._attribute_value(params[0])
        try:
            lst = ast.literal_eval(str(other_value))
            return value in lst
        except (ValueError, SyntaxError):
            return False

    @staticmethod
    def validate_integer(value, **kwargs):
        return str(value).isdigit()

    def validate_ip(self, value, **kwargs):
        return self.validate_ipv4(value) or self.validate_ipv6(value)

    @staticmethod
    def validate_ipv6(value, **kwargs):
        # S/0: question 319279
        pattern = re.compile(r"""
            ^
            \s*                         # Leading whitespace
            (?!.*::.*::)                # Only a single whildcard allowed
            (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
            (?:                         # Repeat 6 times:
                [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            ){6}                        #
            (?:                         # Either
                [0-9a-f]{0,4}           #   Another group
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                [0-9a-f]{0,4}           #   Last group
                (?: (?<=::)             #   Colon iff preceeded by exacly one colon
                 |  (?<!:)              #
                 |  (?<=:) (?<!::) :    #
                 )                      # OR
             |                          #   A v4 address with NO leading zeros
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                (?: \.
                    (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                ){3}
            )
            \s*                         # Trailing whitespace
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(value) is not None

    @staticmethod
    def validate_ipv4(value, **kwargs):
        # S/0: question 319279
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(value) is not None

    def validate_json(self, value, **kwargs):
        return self._can_call_with_method(json.loads, value)

    def validate_lt(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='lt')
        value = self._get_size(value)
        lower = self._get_size(self._attribute_value(params[0]))
        return value < lower

    def validate_lte(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='lte')
        value = self._get_size(value)
        lower = self._get_size(self._attribute_value(params[0]))
        return value <= lower

    def validate_max(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='max')
        value = self._get_size(value)
        upper = self._get_size(params[0])
        return value <= upper

    def validate_mime_types(self, value, params, **kwargs):
        if not self.validate_file(value):
            return False
        self._assert_params_size(size=1, params=params, rule='mime_types')
        kind = filetype.guess(value.stream.read(512))
        value.seek(0)
        if kind is None:
            return value.mimetype in params
        return kind.mime in params

    def validate_min(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='min')
        value = self._get_size(value)
        lower = self._get_size(params[0])
        return value >= lower

    def validate_not_in(self, value, params, **kwargs):
        return not self.validate_in(value, params)

    def validate_not_regex(self, value, params, **kwargs):
        return not self.validate_regex(value, params)

    @staticmethod
    def validate_nullable(value, **kwargs):
        return True

    def validate_numeric(self, value, **kwargs):
        return self._can_call_with_method(float, value)

    def validate_present(self, attribute, **kwargs):
        accessors = attribute.split('.')
        request_param = self._request
        for accessor in accessors:
            if accessor not in request_param:
                return False
            request_param = request_param[accessor]
        return True

    def validate_regex(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='regex')
        self._assert_with_method(re.compile, params[0])
        return re.match(params[0], value)

    def validate_required(self, value, attribute, nullable, **kwargs):
        if not value and not nullable:
            return False
        return self.validate_present(attribute)

    def validate_required_if(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=2, params=params, rule='required_if')
        other_value = self._attribute_value(params[0])
        if str(other_value) in params[1:]:
            return self.validate_required(value, attribute, nullable)
        return True

    def validate_required_unless(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=2, params=params, rule='required_unless')
        other_value = self._attribute_value(params[0])
        if other_value not in params[1:]:
            return self.validate_required(value, attribute, nullable)
        return True

    def validate_required_with(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=1, params=params, rule='required_with')
        for param in params:
            if self.validate_present(param):
                return self.validate_required(value, attribute, nullable)
        return True

    def validate_required_with_all(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=1, params=params,
                rule='required_with_all')
        for param in params:
            if not self.validate_present(param):
                return True
        return self.validate_required(value, attribute, nullable)

    def validate_required_without(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=1, params=params,
                rule='required_without')
        for param in params:
            if not self.validate_present(param):
                return self.validate_required(value, attribute, nullable)
        return True

    def validate_required_without_all(self, value, attribute, params, nullable, **kwargs):
        self._assert_params_size(size=1, params=params,
                rule='required_without_all')
        for param in params:
            if self.validate_present(param):
                return True
        return self.validate_required(value, attribute, nullable)

    def validate_same(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='same')
        other_value = self._attribute_value(params[0])
        return value == other_value

    def validate_size(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='size')
        self._assert_with_method(float, params[0])
        other_value = params[0]
        if other_value.count('.') > 0:
            other_value = float(other_value)
        else:
            other_value = int(other_value)
        return self._get_size(value) == other_value

    def validate_starts_with(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='starts_with')
        return str(value).startswith(params[0])

    @staticmethod
    def validate_string(value, **kwargs):
        return isinstance(value,
                str if sys.version_info[0] >= 3 else basestring)

    @staticmethod
    def validate_timezone(value, **kwargs):
        return value in pytz.all_timezones

    @staticmethod
    def validate_unique(value, **kwargs):
        return False

    @staticmethod
    def validate_url(value, **kwargs):
        pattern = re.compile(r"""
            ^
            (https?|ftp)://  # http, https or ftp
            (?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.? # domain
                |
            localhost
                |
            \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) # ...or ip
            (?::\d+)?                           # optional port
            (?:/?|[/?]\S+)
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(value) is not None

    @staticmethod
    def validate_uuid(value, **kwargs):
        return re.match(
            r'^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$',
            str(value).lower()
        ) is not None

    @staticmethod
    def _compare_dates(first, second, comparator):
        try:
            return comparator(dateparse(first), dateparse(second))
        except Exception:
            return False

    def _can_call_with_method(self, method, value):
        try:
            self._assert_with_method(method, value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _has_rule(rules, rule_name):
        for rule in rules:
            if rule['name'] == rule_name:
                return True
        return False

    def _get_rule_handler(self, rule_name):
        handler_name = 'validate_' + rule_name
        if handler_name in self._custom_handlers:
            return self._custom_handlers[handler_name]['handler']
        elif hasattr(self, handler_name):
            return getattr(self, handler_name)
        else:
            raise ValueError("Validator: no handler for rule " + rule_name)

    def _get_size(self, value, rules=None):
        rules = rules or {}
        value_type = self._get_type(value, rules)
        if value_type == 'array':
            return len(ast.literal_eval(str(value)))
        elif value_type == 'numeric':
            return float(value)
        elif value_type == 'file':
            value.seek(0, os.SEEK_END)
            return round(value.tell() /  1024.0, 0)
        return len(str(value))

    def _get_type(self, value, rules=None):
        rules = rules or {}
        value_type = self._get_type_from_rules(value, rules)
        if not value_type:
            value_type = self._get_type_from_value(value)
        return value_type

    def _get_type_from_rules(self, value, rules):
        array_rules = ['array']
        numeric_rules = ['integer', 'numeric']
        file_rules = ['file', 'image', 'dimensions']
        string_rules = ['alpha', 'alpha_dash', 'string']
        if self._has_any_of_rules(string_rules, rules):
            return 'string'
        elif self._has_any_of_rules(numeric_rules, rules) and self.validate_numeric(value):
            return 'numeric'
        elif self._has_any_of_rules(array_rules, rules) and self.validate_array(value):
            return 'array'
        elif self._has_any_of_rules(file_rules, rules) and self.validate_file(value):
            return 'file'

    def _get_type_from_value(self, value):
        if self.validate_numeric(value):
            return 'numeric'
        elif self.validate_array(value):
            return 'array'
        elif self.validate_file(value):
            return 'file'
        return 'string'

    def _has_any_of_rules(self, subset, rules):
        for rule in subset:
            if self._has_rule(rules, rule):
                return True
        return False

    def _attribute_value(self, attribute):
        accessors = attribute.split('.')
        request_param = self._request
        for accessor in accessors:
            if accessor not in request_param:
                return None
            request_param = request_param[accessor]
        return request_param

    @staticmethod
    def _assert_params_size(size, params, rule):
        if size > len(params):
            raise ValueError(
                '%s rule requires at least %s parameter(s), non provided.' %
                (rule.title(), size)
            )

    @staticmethod
    def _assert_with_method(method, value):
        try:
            method(value)
        except:
            raise ValueError(
                'Cannot call method %s with value %s' %
                (method.__name__, str(value))
            )

