"""
"""
import sys
import ast
import json
import operator
import requests
from requests import RequestException

if sys.version_info[0] >= 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen
    from urllib.error import URLError

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
        try:
            requests.options(value)
            return True
        except (URLError, IOError):
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
        except Exception:
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
        return self._parse_date(value) is not None

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
        return re.match(
            "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
            value
        ) is not None

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
        self._assert_params_size(size=1, params=params, rule='gte')
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
        return re.match(r'[0-9]', str(value)) is not None

    def validate_ip(self, value, **kwargs):
        return self.validate_ipv4(value) or self.validate_ipv6(value)

    def validate_ipv6(self, value, **kwargs):
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

    def validate_ipv4(self, value, **kwargs):
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

    def validate_mime_types(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='mime_types')
        return value.mimetype in params

    def validate_extension(self, value, params, **kwargs):
        self._assert_params_size(size=1, params=params, rule='mime_types')
        return value.filename.split('.')[-1].lower() == params[0]

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
        """
         This pattern is derived from Symfony\Component\Validator\Constraints\UrlValidator (2.7.4).
         (c) Fabien Potencier <fabien@symfony.com> http://symfony.com
        """
        pattern = re.compile(r"""
            ^
            ((aaa|aaas|about|acap|acct|acr|adiumxtra|afp|afs|aim|apt|attachment|aw|barion|beshare|bitcoin|blob|bolo|callto|cap|chrome|chrome-extension|cid|coap|coaps|com-eventbrite-attendee|content|crid|cvs|data|dav|dict|dlna-playcontainer|dlna-playsingle|dns|dntp|dtn|dvb|ed2k|example|facetime|fax|feed|feedready|file|filesystem|finger|fish|ftp|geo|gg|git|gizmoproject|go|gopher|gtalk|h323|ham|hcp|http|https|iax|icap|icon|im|imap|info|iotdisco|ipn|ipp|ipps|irc|irc6|ircs|iris|iris.beep|iris.lwz|iris.xpc|iris.xpcs|itms|jabber|jar|jms|keyparc|lastfm|ldap|ldaps|magnet|mailserver|mailto|maps|market|message|mid|mms|modem|ms-help|ms-settings|ms-settings-airplanemode|ms-settings-bluetooth|ms-settings-camera|ms-settings-cellular|ms-settings-cloudstorage|ms-settings-emailandaccounts|ms-settings-language|ms-settings-location|ms-settings-lock|ms-settings-nfctransactions|ms-settings-notifications|ms-settings-power|ms-settings-privacy|ms-settings-proximity|ms-settings-screenrotation|ms-settings-wifi|ms-settings-workplace|msnim|msrp|msrps|mtqp|mumble|mupdate|mvn|news|nfs|ni|nih|nntp|notes|oid|opaquelocktoken|pack|palm|paparazzi|pkcs11|platform|pop|pres|prospero|proxy|psyc|query|redis|rediss|reload|res|resource|rmi|rsync|rtmfp|rtmp|rtsp|rtsps|rtspu|secondlife|s3|service|session|sftp|sgn|shttp|sieve|sip|sips|skype|smb|sms|smtp|snews|snmp|soap.beep|soap.beeps|soldat|spotify|ssh|steam|stun|stuns|submit|svn|tag|teamspeak|tel|teliaeid|telnet|tftp|things|thismessage|tip|tn3270|turn|turns|tv|udp|unreal|urn|ut2004|vemmi|ventrilo|videotex|view-source|wais|webcal|ws|wss|wtai|wyciwyg|xcon|xcon-userid|xfire|xmlrpc\.beep|xmlrpc.beeps|xmpp|xri|ymsgr|z39\.50|z39\.50r|z39\.50s)):// # protocol
            (([\pL\pN-]+:)?([\pL\pN-]+)@)?  # basic auth
            (
                ([\pL\pN\pS\-\.])+(\.?([\pL]|xn\-\-[\pL\pN-]+)+\.?) # a domain name
                    |                                              # or
                \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}                 # an IP address
                    |                                              # or
                \[
                    (?:(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){6})(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:::(?:(?:(?:[0-9a-f]{1,4})):){5})(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:[0-9a-f]{1,4})))?::(?:(?:(?:[0-9a-f]{1,4})):){4})(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,1}(?:(?:[0-9a-f]{1,4})))?::(?:(?:(?:[0-9a-f]{1,4})):){3})(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,2}(?:(?:[0-9a-f]{1,4})))?::(?:(?:(?:[0-9a-f]{1,4})):){2})(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,3}(?:(?:[0-9a-f]{1,4})))?::(?:(?:[0-9a-f]{1,4})):)(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,4}(?:(?:[0-9a-f]{1,4})))?::)(?:(?:(?:(?:(?:[0-9a-f]{1,4})):(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,5}(?:(?:[0-9a-f]{1,4})))?::)(?:(?:[0-9a-f]{1,4})))|(?:(?:(?:(?:(?:(?:[0-9a-f]{1,4})):){0,6}(?:(?:[0-9a-f]{1,4})))?::))))
                \]  # an IPv6 address
            )
            (:[0-9]+)?                              # a port (optional)
            (/?|/\S+|\?\S*|\#\S*)                   # a /, nothing, a / with something, a query or a fragment
            $/ixu
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(value) is not None

    def validate_uuid(self, value, **kwargs):
        if not self.validate_string(value):
            return False
        return re.match(
            r'^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$',
            value.lower()
        ) is not None

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
                '%s rule requires at least %s parameter(s), non provided.' %
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
