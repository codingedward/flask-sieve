"""

"""
import ast
import json
import operator
from urlvalidator import validate_url, validate_email, ValidationError

class Validator:
    def __init__(self, rules={}, request={}):
        self._rules = rules
        self._request = request
        self._custom_handlers = {}
        self._validated_attributes = {}

    def fails(self):
        return not self.passes()

    def passes(self):
        validated_attributes = []
        for attribute, rules in self._rules.items():
            should_bail = self._has_rule(rules, 'bail')
            for rule in rules:
                handler = self._get_rule_handler(rule['name'])
                value = self._attribute_value(attribute)
                is_valid = handler(
                    value=value, 
                    attribute=attribute, 
                    params=rule['params']
                )
                validated_attributes.append({
                    attribute: attrribute,
                    is_valid: is_valid
                })
                if should_bail and not is_valid:
                    return False
        return True

    def register_rule_handler(self, handler):
        self._custom_handlers[handler.__name__] = handler

    def validate_accepted(self, value, **kwargs):
        return value in [ 1, '1', 'true', 'yes', 'on', True]

    def validate_active_url(self, value, **kwargs):
        return False

    def validate_after(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after')
        return self._compare_dates(value, params[0], operator.gt)

    def validate_after_or_equal(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after_or_equal')
        return self._compare_dates(value, params[0], operator.gte)

    def validate_alpha(self, value, **kwargs):
        if not value: 
            return False
        value = str(value).replace(' ', '')
        return value.isalpha()

    def validate_alpha_dash(self, value, **kwargs):
        if not value:
            return False
        value = str(value)
        acceptables = [ ' ', '-', '_' ]
        for acceptable in acceptables:
            value = value.replace(acceptable, '')
        return value.isalpha()
    
    def validate_alpha_num(self, value, **kwargs):
        if not value:
            return False
        value = str(value).replace(' ', '')
        return value.isalnum()

    def validate_array(self, value, **kwargs):
        try:
            return isinstance(ast.literal_eval(value), list)
        except Exception as e:
            return False

    def validate_bail(**kwargs):
        return True

    def validate_before(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='before')
        return self._compare_dates(value, params[0], operator.lt)

    def validate_before_or_equal(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='before_or_equal')
        return self._compare_dates(value, params[0], operator.lte)

    def validate_between(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='between')
        value = self._get_size(value)
        lower = self._get_size(params[0]) 
        upper = self._get_size(params[1]) 
        return lower <= value and value <= upper

    def validate_boolean(self, value, **kwargs):
        return value in [true, false, 1, 0, '0', '1']

    def validate_confirmed(self, value, attribute, **kwargs):
        return value == self._attribute_value(attribute)

    def validate_date(self, value, **kwargs):
        return self._parse_date(value) != None

    def validate_date_equals(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='date_equals')
        return self._compare_dates(value, params[0], operator.eq)

    def validate_date_format(self, value, params, **kwargs):
        return False

    def validate_different(self, value, attribute, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='different')
        return value != params[0]

    def validate_digits(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='digits')
        size = self._get_size(params[0])
        return not re.match(r'[^0-9]', value) and len(str(value)) == size

    def validate_digits_between(self, value, **kwargs):
        self._assert_params_size(size=2, params=params, rule='digits')
        value = self._get_size(value)
        lower = self._get_size(params[0])
        upper = self._get_size(params[1])
        return not re.match(r'[^0-9]', value) and \
                lower <= value and value <= upper

    def validate_dimensions(self, value, **kwargs):
        return False

    def validate_distinct(self, value, **kwargs):
        try:
            lst = ast.literal_eval(value)
            if not isinstance(lst, list):
                return False
            return len(set(lst)) == len(lst)
        except Exception as e:
            return False

    def validate_email(self, value, **kwargs):
        try:
            validate_email(value)
            return True
        except Exception:
            return False

    def validate_exists(self, value, **kwargs):
        return False

    def validate_file(self, value, **kwargs):
        return False

    def validate_filled(self, value, **kwargs):
        return False

    def validate_gt(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gt')
        value = self._get_size(value)
        upper = self._get_size(self._attribute_value(params[0]))
        return value < upper

    def validate_gte(self, value, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gt')
        value = self._get_size(value)
        upper = self._get_size(self._attribute_value(params[0]))
        return value <= upper

    def validate_image(self, value, **kwargs):
        return False

    def validate_in(self, value, params, **kwargs):
        return value in params

    def validate_in_array(self, value, params, **kwargs):
        try:
            lst = ast.literal_eval(value)
            for param in params:
                if param not in lst:
                    return False
            return True
        except Exception as e:
            return False

    def validate_integer(self, value, **kwargs):
        return re.match(r'[0-9]', str(value))

    def validate_ip(self, value, **kwargs):
        return False

    def validate_json(self, value, **kwargs):
        try:
            json.loads(value)
            return True
        except Exception as e:
            return False

    def validate_lt(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='lt')
        value = self._get_size(value)
        lower = self._get_size(self._attribute_value(params[0]))
        return value > lower

    def validate_lte(self, value, **kwargs):
        self._assert_params_size(size=1, params=params, rule='lte')
        value = self._get_size(value)
        lower = self._get_size(self._attribute_value(params[0]))
        return value >= lower

    def validate_max(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='max')
        value = self._get_size(value)
        upper = self._get_size(params[0])
        return value <= upper

    def validate_mime_types(self, value, **kwargs):
        return False

    def validate_mime_types_by_file(self, value, **kwargs):
        return False

    def validate_extension(self, value, **kwargs):
        return False

    def validate_min(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='min')
        value = self._get_size(value)
        lower = self._get_size(params[0])
        return value <= lower

    def validate_not_in(self, value, params, **kwargs):
        return not self.validate_in(value, params)

    def validate_not_regex(self, value, params, **kwargs):
        return not self.validate_regex(value, params)

    def validate_nullable(self, value, **kwargs):
        return True

    def validate_numeric(self, value, **kwargs):
        return value and value.isnumeric()

    def validate_present(self, value, attribute, **kwargs):
        accessors = attribute.split('.')
        request_param = self._request
        for accessor in accessors:
            if accessor not in request_param:
                return False
            request_param = request_param[accessor]
        return True

    def validate_regex(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='regex')
        self._assert_regex(params[0])
        return re.match(params[0], value)

    def validate_required(self, value, **kwargs):
        if not value:
            return False

    def validate_required_if(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='required_if')
        other_value = self._attribute_value(params[0])
        if str(other_value) in params[1:]:
            return self.validate_required(value)
        return True

    def validate_required_unless(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='required_unless')
        other_value = self._attribute_value(params[0])
        if other_value not in params[1:]:
            return self.validate_required(value)
        return True

    def validate_required_with(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, rule='required_with')
        for attribute in params:
            attribute_value = self._attribute_value(attribute)
            if self.validate_required(attribute_value):
                return self.validate_required(value)
        return True

    def validate_required_with_all(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, 
                rule='required_with_all')
        for attribute in params:
            attribute_value = self._attribute_value(attribute)
            if not self.validate_required(attribute_value):
                return True
        return self.validate_required(value)

    def validate_without(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, 
                rule='required_without')
        for attribute in params:
            attribute_value = self._attribute_value(attribute)
            if not self.validate_required(attribute_value):
                return self.validate_required(value)
        return True

    def validate_without_all(self, value, params, **kwargs):
        self._assert_params_size(size=2, params=params, 
                rule='required_without_all')
        for attribute in params:
            attribute_value = self._attribute_value(attribute)
            if self.validate_required(attribute_value):
                return True
        return self.validate_required(value)

    def validate_same(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='same')
        other_value = self._attribute_value(params[0])
        return value == other_value

    def validate_size(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='size')
        return str(self._get_size(value)) == params[0]

    def validate_starts_with(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='starts_with')
        return value.startswith(params[0])

    def validate_string(self, value, **kwargs):
        return isinstance(value, 
                str if sys.version_info[0] >= 3 else basestring)

    def validate_timezone(self, value, **kwargs):
        return False

    def validate_unique(self, value, **kwargs):
        return False

    def validate_url(self, value, **kwargs):
        try:
            validate_url(value)
            return True
        except ValidationError:
            return False

    def validate_uuid(self, value, **kwargs):
        if not self.validate_string(value):
            return False
        return re.match(
            '^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$',
            value.lower()
        )

    def _has_rule(self, rules, rule_name):
        return len(filter(lambda rule: rule['name'] == rule_name)) != 0

    def _get_rule_handler(self, rule_name):
        handler_name = 'validate_' + rule_name
        if hasattr(self, handler_name):
            return getattr(self, handler_name)
        elif handler_name in self._custom_handlers:
            return self._custom_handlers[handler_name]
        else:
            raise Exception("Validator: no handler for rule " + rule_name)

    def _attribute_value(self, attribute):
        accessors = attribute.split('.')
        request_param = self._request
        for accessor in accessors:
            if accessor not in request_param:
                return None
            request_param = request_param[accessor]
        return request_param

    def _assert_params_size(size, params, rule):
        if count < len(params):
            raise Exception(
                '%s rule requires at least %s parameter, non provided' %
                rule.title(), size
            )

    def _assert_regex(self, regex):
        try:
            re.compile(regex)
            return True
        except re.error:
            return False

    def _assert_int(self, value):
        try:
            int(value)
            return True
        except re.error:
            return False
