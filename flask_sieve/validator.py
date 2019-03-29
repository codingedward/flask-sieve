"""

"""
import ast
import json
import operator

class Validator:
    def __init__(self, rules={}, request={}):
        self._errors = {}
        self._rules = rules
        self._request = request
        self._custom_handlers = {}

    def register_rule_handler(self, handler):
        self._custom_handlers[handler.__name__] = handler

    def passes(self):
        validated_attributes = []
        for attribute, rules in self._rules.items():
            should_bail = self._has_bail_rule(rules)
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

    def validate_accepted(self, value, **kwargs):
        acceptable = [ 1, '1', 'true', 'yes', 'on', True]
        return acceptable.contains(value)

    def validate_active_url(self, value, **kwargs):
        return False

    def validate_after(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after')
        return self._compare_dates(value, params[0], operator.gt)

    def validate_after_or_equal(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='after_or_equal')
        return self._compare_dates(value, params[0], operator.gte)

    def validate_alpha(self, value, **kwargs):
        value = str(value).replace(' ', '')
        return value.isalpha()

    def validate_alpha_dash(self, value, **kwargs):
        value = str(value)
        acceptables = [ ' ', '-', '_' ]
        for acceptable in acceptables:
            value = value.replace(acceptable)
        return value.isalpha()
    
    def validate_alpha_num(self, value, **kwargs):
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
        acceptable = [true, false, 1, 0, '0', '1']
        return acceptable.contains(value)

    def validate_confirmed(self, value, attribute, **kwargs):
        return value == self._request.get(attribute)

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
            if not isinstance(value, list):
                return False

            unique_elements = set(lst)
            return len(unique_elements) == len(lst)
        except Exception as e:
            return False

    def validate_email(self, value, **kwargs):
        return re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", 
                value)

    def validate_exists(self, value, **kwargs):
        return False

    def validate_file(self, value, **kwargs):
        return False

    def validate_filled(self, value, **kwargs):
        return False

    def validate_gt(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gt')
        value = self._get_size(value)
        upper = self._get_size(params[0])
        return value < upper

    def validate_gte(self, value, **kwargs):
        self._assert_params_size(size=1, params=params, rule='gt')
        value = self._get_size(value)
        upper = self._get_size(params[0])
        return value <= upper

    def validate_image(self, value, **kwargs):
        return False

    def validate_in(self, value, params, **kwargs):
        return params.contains(value)

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
        lower = self._get_size(params[0])
        return value > lower

    def validate_lte(self, value, **kwargs):
        self._assert_params_size(size=1, params=params, rule='lte')
        value = self._get_size(value)
        lower = self._get_size(params[0])
        return value >= lower

    def validate_max(self, value, **kwargs):
        return False

    def validate_mime_types(self, value, **kwargs):
        return False

    def validate_mime_types_by_file(self, value, **kwargs):
        return False

    def validate_extension(self, value, **kwargs):
        return False

    def validate_min(self, value, **kwargs):
        return False

    def validate_not_in(self, value, **kwargs):
        return False

    def validate_not_regex(self, value, **kwargs):
        return False

    def validate_nullable(self, value, **kwargs):
        return False

    def validate_numeric(self, value, **kwargs):
        return False

    def validate_numeric(self, attribute, **kwargs):
        pass

    def validate_present(self, value, **kwargs):
        return False

    def validate_regex(self, value, **kwargs):
        return False

    def validate_requied(self, value, **kwargs):
        return False

    def validate_required_if(self, value, **kwargs):
        return False

    def validate_required_unless(self, value, **kwargs):
        return False

    def validate_required_with(self, value, **kwargs):
        return False

    def validate_required_with_all(self, value, **kwargs):
        return False

    def validate_without(self, value, **kwargs):
        return False

    def validate_without_all(self, value, **kwargs):
        return False

    def validate_same(self, value, **kwargs):
        return False

    def validate_size(self, value, **kwargs):
        return False

    def validate_starts_with(self, value, **kwargs):
        return False

    def validate_string(self, value, **kwargs):
        return False

    def validate_timezone(self, value, **kwargs):
        return False

    def validate_unique(self, value, **kwargs):
        return False

    def validate_url(self, value, **kwargs):
        return False

    def validate_uuid(self, value, **kwargs):
        return False

    def validate_before(self, attribute, **kwargs):
        pass

    def _has_bail_rule(self, rules):
        return len(filter(lambda rule: rule['name'] == 'bail')) != 0
    
    def _get_rule_handler(self, rule_name):
        handler_name = 'validate_' + rule_name
        if hasattr(self, handler_name):
            return getattr(self, handler_name)
        elif handler_name in self._custom_handlers:
            return self._custom_handlers[handler_name]
        else:
            raise Exception("Validator: no handler for rule " + rule_name)

    def _attribute_value(self, attribute):
        accessors = attributes.split('.')
        request_param = self._request
        for accessor in accessors:
            if accessor not in request_param:
                return None
            request_param = request_param[accessor]
        return request_param

    def _assert_params_size(size, params, rule):
        if count < len(params):
            raise Exception(rule.title() + 
                    'rule requires a parameter, non provided')
