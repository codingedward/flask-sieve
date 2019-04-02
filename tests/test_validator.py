import json
import unittest
from flask_sieve.parser import Parser
from flask_sieve.validator import Validator

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.validator = Validator()

    def test_validates_active_url(self):
        self.assert_passes(
            rules={'field': 'active_url'},
            request={'field': 'https://google.com'},
        )
        self.assert_fails(
            rules={'field': 'active_url'},
            request={'field': 'https://gxxgle.cxm'},
        )
        
    def test_validates_after(self):
        self.assert_passes(
            rules={'field': 'after:2018-08-02'},
            request={'field': '2nd Sept 2018'}
        )
        self.assert_fails(
            rules={'field': 'after:2018-08-03'},
            request={'field': '3rd Aug 2018'}
        )
        self.assert_fails(
            rules={'field': 'after:2018-09-02'},
            request={'field': '2nd Sept 2017'}
        )

    def test_validates_after_or_equal(self):
        self.assert_passes(
            rules={'field': 'after_or_equal:3/8/2018'},
            request={'field': '3rd Sept 2018'}
        )
        self.assert_passes(
            rules={'field': 'after_or_equal:3/8/2018'},
            request={'field': '3rd Aug 2018'}
        )
        self.assert_fails(
            rules={'field': 'after_or_equal:5/8/2018'},
            request={'field': '5th Sept 2017'}
        )

    def test_validates_alpha(self):
        self.assert_passes(
            rules={'field': 'alpha'},
            request={'field': 'hi there'}
        )
        self.assert_fails(
            rules={'field': 'alpha'},
            request={'field': 'abcd1234'}
        )

    def test_validates_alpha_dash(self):
        self.assert_passes(
            rules={'field': 'alpha_dash'},
            request={'field': 'hi-there__ friend'}
        )
        self.assert_fails(
            rules={'field': 'alpha_dash'},
            request={'field': 'abcd1234'}
        )

    def test_validates_alpha_num(self):
        self.assert_passes(
            rules={'field': 'alpha_num'},
            request={'field': 'abcd1234'}
        )
        self.assert_fails(
            rules={'field': 'alpha_num'},
            request={'field': 'hi-there__ friend'}
        )

    def test_validates_array(self):
        self.assert_passes(
            rules={'field': 'array'},
            request={'field': '[1, 2, 3]'}
        )
        self.assert_fails(
            rules={'field': 'array'},
            request={'field': '[1, 2, 3}'}
        )

    def test_validates_before(self):
        self.assert_passes(
            rules={'field': 'before:2018-09-02'},
            request={'field': '2nd Nov 2017'}
        )
        self.assert_fails(
            rules={'field': 'before:2018-09-02'},
            request={'field': '2nd Oct 2018'}
        )
        self.assert_fails(
            rules={'field': 'before:2018-08-02'},
            request={'field': '2nd Sept 2018'}
        )

    def test_validates_before_or_equal(self):
        self.assert_passes(
            rules={'field': 'before_or_equal:2018-09-03'},
            request={'field': '3rd Nov 2017'}
        )
        self.assert_passes(
            rules={'field': 'before_or_equal:2018-09-03'},
            request={'field': '3rd Sept 2018'}
        )
        self.assert_fails(
            rules={'field': 'before_or_equal:2018-08-02'},
            request={'field': '2nd Sept 2018'}
        )

    def test_validates_between(self):
        self.assert_passes(
            rules={'field': 'between:2.0,50'},
            request={'field': '3'}
        )
        self.assert_passes(
            rules={'field': 'between:0.002,5'},
            request={'field': '5'}
        )
        self.assert_fails(
            rules={'field': 'between:2.0,5'},
            request={'field': '30'}
        )

    def test_validates_boolean(self):
        for value in [True, False, 1, 0, '1', '0']:
            self.assert_passes(
                rules={'field': 'boolean'},
                request={'field': value}
            )

        self.assert_fails(
            rules={'field': 'boolean'},
            request={'field': 'hi'}
        )


    def test_validates_confirmed(self):
        self.assert_passes(
            rules={'field': 'confirmed'},
            request={'field': 1, 'field_confirmation': 1}
        )
        self.assert_fails(
            rules={'field': 'confirmed'},
            request={'field': 2, 'field_confirmation': 1}
        )
        self.assert_fails(
            rules={'field': 'confirmed'},
            request={'field': 2}
        )

    def test_validates_date(self):
        self.assert_passes(
            rules={'field': 'date'},
            request={'field': '2018-01-10'}
        )
        self.assert_passes(
            rules={'field': 'date'},
            request={'field': '3rd August 2018'}
        )
        self.assert_fails(
            rules={'field': 'date'},
            request={'field': 'now'}
        )
        self.assert_fails(
            rules={'field': 'date'},
            request={'field': True}
        )

    def test_validates_date_equals(self):
        self.assert_passes(
            rules={'field': 'date_equals:2018-08-02'},
            request={'field': '2nd August 2018'}
        )
        self.assert_fails(
            rules={'field': 'date_equals:2018-08-03'},
            request={'field': '3rd March 2019'}
        )
        self.assert_fails(
            rules={'field': 'date_equals:2018-09-02'},
            request={'field': '2nd Sept 2017'}
        )

    def test_validates_date_equals(self):
        self.assert_passes(
            rules={'field': 'date_equals:2018-08-02'},
            request={'field': '2nd August 2018'}
        )
        self.assert_fails(
            rules={'field': 'date_equals:2018-08-03'},
            request={'field': '3rd March 2019'}
        )
        self.assert_fails(
            rules={'field': 'date_equals:2018-09-02'},
            request={'field': '2nd Sept 2017'}
        )

    def test_validates_different(self):
        self.assert_passes(
            rules={'field': 'different:field_2'},
            request={'field': 1, 'field_2': 2}
        )
        self.assert_fails(
            rules={'field': 'different:field_2'},
            request={'field': 1, 'field_2': 1}
        )

    def test_validates_digits(self):
        self.assert_passes(
            rules={'field': 'digits:1'},
            request={'field': 1}
        )
        self.assert_passes(
            rules={'field': 'digits:4'},
            request={'field': '1.243'}
        )
        self.assert_passes(
            rules={'field': 'digits:4'},
            request={'field': 0.243}
        )
        self.assert_fails(
            rules={'field': 'digits:1'},
            request={'field': '123ab'}
        )

    def test_validates_digits_between(self):
        self.assert_passes(
            rules={'field': 'digits_between:1,3'},
            request={'field': 1}
        )
        self.assert_passes(
            rules={'field': 'digits_between:1,3'},
            request={'field': '1.24'}
        )
        self.assert_passes(
            rules={'field': 'digits_between:0,4'},
            request={'field': 0.243}
        )
        self.assert_fails(
            rules={'field': 'digits_between:0,3'},
            request={'field': '3.142'}
        )

    def test_validates_distinct(self):
        self.assert_passes(
            rules={'field': 'distinct'},
            request={'field': [1, 2, 3]}
        )
        self.assert_passes(
            rules={'field': 'distinct'},
            request={'field': ['hi', 'there', 'friend']}
        )
        self.assert_passes(
            rules={'field': 'distinct'},
            request={'field': '[1, 2, 4]'}
        )
        self.assert_fails(
            rules={'field': 'distinct'},
            request={'field': [1, 1]}
        )

    def test_validates_email(self):
        self.assert_passes(
            rules={'field': 'email'},
            request={'field': 'john@doe.com'}
        )
        self.assert_passes(
            rules={'field': 'email'},
            request={'field': 'jane@doe.com'}
        )
        self.assert_fails(
            rules={'field': 'email'},
            request={'field': 'hi there'}
        )

    def test_validates_gt(self):
        self.assert_passes(
            rules={'field': 'gt:field_2'},
            request={'field': -1, 'field_2': -10}
        )
        self.assert_fails(
            rules={'field': 'gt:field_2'},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': 'gt:field_2'},
            request={'field': 1, 'field_2': 10}
        )

    def test_validates_gte(self):
        self.assert_passes(
            rules={'field': 'gte:field_2'},
            request={'field': -1, 'field_2': -10}
        )
        self.assert_passes(
            rules={'field': 'gte:field_2'},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': 'gte:field_2'},
            request={'field': 1, 'field_2': 10}
        )

    def test_validates_in(self):
        self.assert_passes(
            rules={'field': 'in:male,female'},
            request={'field': 'male'}
        )
        self.assert_fails(
            rules={'field': 'in:male,female'},
            request={'field': 'person'}
        )

    def test_validates_not_in(self):
        self.assert_passes(
            rules={'field': 'not_in:male,female'},
            request={'field': 'person'}
        )
        self.assert_fails(
            rules={'field': 'not_in:male,female'},
            request={'field': 'female'}
        )

    def test_validates_in_array(self):
        self.assert_passes(
            rules={'field': 'in_array:field_2'},
            request={'field': 'male', 'field_2': ['male', 'female']}
        )
        self.assert_fails(
            rules={'field': 'in_array:field_2'},
            request={'field': 'female', 'field_2': []}
        )

    def test_validates_integer(self):
        self.assert_passes(
            rules={'field': 'integer'},
            request={'field': 100}
        )
        self.assert_passes(
            rules={'field': 'integer'},
            request={'field': '100'}
        )
        self.assert_fails(
            rules={'field': 'integer'},
            request={'field': '1.200'}
        )
        self.assert_fails(
            rules={'field': 'integer'},
            request={'field': 1.204}
        )

    def test_validates_ip(self):
        self.assert_passes(
            rules={'field': 'ip'},
            request={'field': '0.0.0.0'}
        )
        self.assert_passes(
            rules={'field': 'ip'},
            request={'field': '127.0.0.1'}
        )
        self.assert_passes(
            rules={'field': 'ip'},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )
        self.assert_fails(
            rules={'field': 'ip'},
            request={'field': '127.d.0.1'}
        )
        self.assert_fails(
            rules={'field': 'ip'},
            request={'field': '20:0db8:0000:0000:0000:xx:0042:8329'}
        )

    def test_validates_ipv4(self):
        self.assert_passes(
            rules={'field': 'ipv4'},
            request={'field': '0.0.0.0'}
        )
        self.assert_passes(
            rules={'field': 'ipv4'},
            request={'field': '127.0.0.1'}
        )
        self.assert_fails(
            rules={'field': 'ipv4'},
            request={'field': '127.d.0.1'}
        )
        self.assert_fails(
            rules={'field': 'ipv4'},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )

    def test_validates_ipv6(self):
        self.assert_passes(
            rules={'field': 'ipv6'},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )
        self.assert_fails(
            rules={'field': 'ipv6'},
            request={'field': '127.0.0.1'}
        )
        self.assert_fails(
            rules={'field': 'ipv6'},
            request={'field': '20:0db8:0000:0000:0000:xx:0042:8329'}
        )

    def test_validates_json(self):
        self.assert_passes(
            rules={'field': 'json'},
            request={'field': json.dumps({'hi': 'there'})}
        )
        self.assert_fails(
            rules={'field': 'json'},
            request={'field': 'hello'}
        )
        self.assert_fails(
            rules={'field': 'json'},
            request={'field': 1}
        )

    def test_validates_lt(self):
        self.assert_passes(
            rules={'field': 'lt:field_2'},
            request={'field': -10, 'field_2': -1}
        )
        self.assert_fails(
            rules={'field': 'lt:field_2'},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': 'lt:field_2'},
            request={'field': 10, 'field_2': 1}
        )

    def test_validates_lte(self):
        self.assert_passes(
            rules={'field': 'lte:field_2'},
            request={'field': -10, 'field_2': -1}
        )
        self.assert_passes(
            rules={'field': 'lte:field_2'},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': 'lte:field_2'},
            request={'field': 10, 'field_2': 1}
        )

    def test_validates_max(self):
        self.assert_passes(
            rules={'field': 'max:20'},
            request={'field': 10}
        )
        self.assert_fails(
            rules={'field': 'max:10'},
            request={'field': 30}
        )

    def test_validates_min(self):
        self.assert_passes(
            rules={'field': 'min:0'},
            request={'field': 10}
        )
        self.assert_fails(
            rules={'field': 'min:10'},
            request={'field': 0}
        )

    def test_validates_mime_types(self):
        pass

    def assert_fails(self, rules, request):
        self._assert(rules, request, False)

    def assert_passes(self, rules, request):
        self._assert(rules, request, True)

    def _assert(self, rules, request, passes):
        p = self.parser
        v = self.validator
        v.set_request(request)
        p.set_rules(rules)
        v.set_rules(p.parsed_rules())
        self.assertTrue(v.passes() if passes else v.fails())


if __name__ == '__main__':
    unittest.main()
