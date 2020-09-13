import json
import unittest

from werkzeug.datastructures import FileStorage

from flask_sieve.parser import Parser
from flask_sieve.rules_processor import RulesProcessor

class FakeFileStream:
    def __init__(self, buf):
       self.buf = buf

    def read(self, buf_size):
        return self.buf[:buf_size]

    def seek(self, value):
        pass


class TestRulesProcessor(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.processor = RulesProcessor()
        self.stream = open('tests/files/image.png', 'rb')
        self.image_file = FileStorage(
            stream=self.stream,
            filename='image.png',
            content_type='image/png',
            name='image'
        )
        self.invalid_file = FileStorage(
            stream=FakeFileStream(bytearray([0xFE, 0x58, 0x8F, 0x00, 0x08])),
            filename='invalid.png'
        )

    def test_validates_accepted(self):
        acceptables = [ 1, '1', 'true', 'yes', 'on', True]
        for acceptable in acceptables:
            self.assert_passes(
                rules={'field': ['accepted']},
                request={'field': acceptable},
            )
        self.assert_fails(
            rules={'field': ['accepted']},
            request={'field': 'hi'},
        )

    def test_validates_active_url(self):
        self.assert_passes(
            rules={'field': ['active_url']},
            request={'field': 'https://google.com'},
        )
        self.assert_fails(
            rules={'field': ['bail', 'active_url']},
            request={'field': 'https://gxxgle.cxm'},
        )

    def test_validates_after(self):
        self.assert_passes(
            rules={'field': ['after:2018-08-02']},
            request={'field': '2nd Sept 2018'}
        )
        self.assert_fails(
            rules={'field': ['after:2018-08-03']},
            request={'field': '3rd Aug 2018'}
        )
        self.assert_fails(
            rules={'field': ['after:2018-09-02']},
            request={'field': '2nd Sept 2017'}
        )

    def test_validates_after_or_equal(self):
        self.assert_passes(
            rules={'field': ['after_or_equal:3/8/2018']},
            request={'field': '3rd Sept 2018'}
        )
        self.assert_passes(
            rules={'field': ['after_or_equal:3/8/2018']},
            request={'field': '3rd Aug 2018'}
        )
        self.assert_fails(
            rules={'field': ['after_or_equal:5/8/2018']},
            request={'field': '5th Sept 2017'}
        )

    def test_validates_alpha(self):
        self.assert_passes(
            rules={'field': ['alpha']},
            request={'field': 'hi there'}
        )
        self.assert_fails(
            rules={'field': ['alpha']},
            request={}
        )
        self.assert_fails(
            rules={'field': ['alpha']},
            request={'field': 'abcd1234'}
        )

    def test_validates_alpha_dash(self):
        self.assert_passes(
            rules={'field': ['alpha_dash']},
            request={'field': 'hi-there__ friend'}
        )
        self.assert_fails(
            rules={'field': ['alpha_dash']},
            request={}
        )
        self.assert_fails(
            rules={'field': ['alpha_dash']},
            request={'field': 'abcd1234'}
        )

    def test_validates_alpha_num(self):
        self.assert_passes(
            rules={'field': ['alpha_num']},
            request={'field': 'abcd1234'}
        )
        self.assert_fails(
            rules={'field': ['alpha_num']},
            request={}
        )
        self.assert_fails(
            rules={'field': ['alpha_num']},
            request={'field': 'hi-there__ friend'}
        )

    def test_validates_array(self):
        self.assert_passes(
            rules={'field': ['array']},
            request={'field': '[1, 2, 3]'}
        )
        self.assert_fails(
            rules={'field': ['array']},
            request={'field': '[1, 2, 3}'}
        )

    def test_validates_before(self):
        self.assert_passes(
            rules={'field': ['before:2018-09-02']},
            request={'field': '2nd Nov 2017'}
        )
        self.assert_fails(
            rules={'field': ['before:2018-09-02']},
            request={'field': '2nd Oct 2018'}
        )
        self.assert_fails(
            rules={'field': ['before:2018-08-02']},
            request={'field': '2nd Sept 2018'}
        )

    def test_validates_before_or_equal(self):
        self.assert_passes(
            rules={'field': ['before_or_equal:2018-09-03']},
            request={'field': '3rd Nov 2017'}
        )
        self.assert_passes(
            rules={'field': ['before_or_equal:2018-09-03']},
            request={'field': '3rd Sept 2018'}
        )
        self.assert_fails(
            rules={'field': ['before_or_equal:2018-08-02']},
            request={'field': '2nd Sept 2018'}
        )

    def test_validates_between(self):
        self.assert_passes(
            rules={'field': ['between:2.0,50']},
            request={'field': '3'}
        )
        self.assert_passes(
            rules={'field': ['between:0.002,5']},
            request={'field': '5'}
        )
        self.assert_fails(
            rules={'field': ['between:2.0,5']},
            request={'field': '30'}
        )

    def test_validates_boolean(self):
        for value in [True, False, 1, 0, '1', '0']:
            self.assert_passes(
                rules={'field': ['boolean']},
                request={'field': value}
            )

        self.assert_fails(
            rules={'field': ['boolean']},
            request={'field': 'hi'}
        )


    def test_validates_confirmed(self):
        self.assert_passes(
            rules={'field': ['confirmed']},
            request={'field': 1, 'field_confirmation': 1}
        )
        self.assert_fails(
            rules={'field': ['confirmed']},
            request={'field': 2, 'field_confirmation': 1}
        )
        self.assert_fails(
            rules={'field': ['confirmed']},
            request={'field': 2}
        )

    def test_validates_date(self):
        self.assert_passes(
            rules={'field': ['date']},
            request={'field': '2018-01-10'}
        )
        self.assert_passes(
            rules={'field': ['date']},
            request={'field': '3rd August 2018'}
        )
        self.assert_fails(
            rules={'field': ['date']},
            request={'field': 'now'}
        )
        self.assert_fails(
            rules={'field': ['date']},
            request={'field': True}
        )

    def test_validates_date_equals(self):
        self.assert_passes(
            rules={'field': ['date_equals:2018-08-02']},
            request={'field': '2nd August 2018'}
        )
        self.assert_fails(
            rules={'field': ['date_equals:2018-08-03']},
            request={'field': '3rd March 2019'}
        )
        self.assert_fails(
            rules={'field': ['date_equals:2018-09-02']},
            request={'field': '2nd Sept 2017'}
        )

    def test_validates_different(self):
        self.assert_passes(
            rules={'field': ['different:field_2']},
            request={'field': 1, 'field_2': 2}
        )
        self.assert_fails(
            rules={'field': ['different:field_2']},
            request={'field': 1, 'field_2': 1}
        )

    def test_validates_digits(self):
        self.assert_passes(
            rules={'field': ['digits:1']},
            request={'field': 1}
        )
        self.assert_passes(
            rules={'field': ['digits:4']},
            request={'field': '1.243'}
        )
        self.assert_passes(
            rules={'field': ['digits:4']},
            request={'field': 0.243}
        )
        self.assert_fails(
            rules={'field': ['digits:1']},
            request={'field': '123ab'}
        )

    def test_validates_digits_between(self):
        self.assert_passes(
            rules={'field': ['digits_between:1,3']},
            request={'field': 1}
        )
        self.assert_passes(
            rules={'field': ['digits_between:1,3']},
            request={'field': '1.24'}
        )
        self.assert_passes(
            rules={'field': ['digits_between:0,4']},
            request={'field': 0.243}
        )
        self.assert_fails(
            rules={'field': ['digits_between:0,3']},
            request={'field': '3.142'}
        )

    def test_validates_dimensions(self):
        self.assert_passes(
            rules={'field': ['dimensions:1x1']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['dimensions:2x1']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['dimensions:2x1']},
            request={'field': 'not a file'}
        )
        self.assert_fails(
            rules={'field': ['dimensions:1x1']},
            request={'field': self.invalid_file}
        )

    def test_validates_distinct(self):
        self.assert_passes(
            rules={'field': ['distinct']},
            request={'field': [1, 2, 3]}
        )
        self.assert_passes(
            rules={'field': ['distinct']},
            request={'field': ['hi', 'there', 'friend']}
        )
        self.assert_passes(
            rules={'field': ['distinct']},
            request={'field': '[1, 2, 4]'}
        )
        self.assert_fails(
            rules={'field': ['distinct']},
            request={'field': '["a":1, "b":2, "c":4}'}
        )
        self.assert_fails(
            rules={'field': ['distinct']},
            request={'field': '{"a":1, "b":2, "c":4}'}
        )
        self.assert_fails(
            rules={'field': ['distinct']},
            request={'field': [1, 1]}
        )

    def test_validates_exists(self):
        self.assert_fails(
            rules={'field': ['exists']},
            request={}
        )

    def test_validates_extension(self):
        self.assert_passes(
            rules={'field': ['extension:png']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['extension:png']},
            request={'field': 1}
        )
        self.assert_fails(
            rules={'field': ['extension:tnp']},
            request={'field': self.invalid_file}
        )

    def test_validates_email(self):
        self.assert_passes(
            rules={'field': ['email', 'nullable']},
            request={'field': 'john@doe.com'}
        )
        self.assert_passes(
            rules={'field': ['email']},
            request={'field': 'jane@doe.com'}
        )
        self.assert_fails(
            rules={'field': ['email']},
            request={'field': 'hi there'}
        )

    def test_validates_file(self):
        self.assert_passes(
            rules={'field': ['file']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['file']},
            request={'field': 'hi'}
        )

    def test_validates_filled(self):
        self.assert_passes(
            rules={'field': ['filled']},
            request={'field': 'hi'}
        )
        self.assert_passes(
            rules={'field': ['filled']},
            request={}
        )
        self.assert_fails(
            rules={'field': ['filled']},
            request={'field': None}
        )

    def test_validates_gt(self):
        self.assert_passes(
            rules={'field': ['gt:field_2']},
            request={'field': -1, 'field_2': -10}
        )
        self.assert_fails(
            rules={'field': ['gt:field_2']},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': ['gt:field_2']},
            request={'field': 1, 'field_2': 10}
        )

    def test_validates_gte(self):
        self.assert_passes(
            rules={'field': ['gte:field_2']},
            request={'field': -1, 'field_2': -10}
        )
        self.assert_passes(
            rules={'field': ['gte:field_2']},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': ['gte:field_2']},
            request={'field': 1, 'field_2': 10}
        )

    def test_validates_image(self):
        self.assert_passes(
            rules={'field': ['image']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['image']},
            request={'field': 1}
        )
        self.assert_fails(
            rules={'field': ['image']},
            request={}
        )

    def test_validates_in(self):
        self.assert_passes(
            rules={'field': ['in:male,female']},
            request={'field': 'male'}
        )
        self.assert_fails(
            rules={'field': ['in:male,female']},
            request={'field': 'person'}
        )

    def test_validates_in_array(self):
        self.assert_passes(
            rules={'field': ['in_array:field_2']},
            request={'field': 'male', 'field_2': ['male', 'female']}
        )
        self.assert_fails(
            rules={'field': ['in_array:field_2']},
            request={'field': '{"a":1, "b":2, "c":4}', 'field_2':'hi'}
        )
        self.assert_fails(
            rules={'field': ['in_array:field_2']},
            request={'field': 'female', 'field_2': []}
        )

    def test_validates_integer(self):
        self.assert_passes(
            rules={'field': ['integer']},
            request={'field': 100}
        )
        self.assert_passes(
            rules={'field': ['integer']},
            request={'field': '100'}
        )
        self.assert_fails(
            rules={'field': ['integer']},
            request={'field': '1.200'}
        )
        self.assert_fails(
            rules={'field': ['integer']},
            request={'field': 1.204}
        )

    def test_validates_ip(self):
        self.assert_passes(
            rules={'field': ['ip']},
            request={'field': '0.1.0.0'}
        )
        self.assert_passes(
            rules={'field': ['ip']},
            request={'field': '127.0.0.1'}
        )
        self.assert_passes(
            rules={'field': ['ip']},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )
        self.assert_fails(
            rules={'field': ['ip']},
            request={'field': '127.d.0.1'}
        )
        self.assert_fails(
            rules={'field': ['ip']},
            request={'field': '20:0db8:0000:0000:0000:xx:0042:8329'}
        )

    def test_validates_ipv4(self):
        self.assert_passes(
            rules={'field': ['ipv4']},
            request={'field': '0.1.0.0'}
        )
        self.assert_passes(
            rules={'field': ['ipv4']},
            request={'field': '127.0.0.1'}
        )
        self.assert_fails(
            rules={'field': ['ipv4']},
            request={'field': '127.d.0.1'}
        )
        self.assert_fails(
            rules={'field': ['ipv4']},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )

    def test_validates_ipv6(self):
        self.assert_passes(
            rules={'field': ['ipv6']},
            request={'field': '2001:0db8:0000:0000:0000:ff00:0042:8329'}
        )
        self.assert_fails(
            rules={'field': ['ipv6']},
            request={'field': '127.0.0.1'}
        )
        self.assert_fails(
            rules={'field': ['ipv6']},
            request={'field': '20:0db8:0000:0000:0000:xx:0042:8329'}
        )

    def test_validates_json(self):
        self.assert_passes(
            rules={'field': ['json']},
            request={'field': json.dumps({'hi': 'there'})}
        )
        self.assert_fails(
            rules={'field': ['json']},
            request={'field': 'hello'}
        )
        self.assert_fails(
            rules={'field': ['json']},
            request={'field': 1}
        )

    def test_validates_lt(self):
        self.assert_passes(
            rules={'field': ['lt:field_2']},
            request={'field': -10, 'field_2': -1}
        )
        self.assert_fails(
            rules={'field': ['lt:field_2']},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': ['lt:field_2']},
            request={'field': 10, 'field_2': 1}
        )

    def test_validates_lte(self):
        self.assert_passes(
            rules={'field': ['lte:field_2']},
            request={'field': -10, 'field_2': -1}
        )
        self.assert_passes(
            rules={'field': ['lte:field_2']},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': ['lte:field_2']},
            request={'field': 10, 'field_2': 1}
        )

    def test_validates_max(self):
        self.assert_passes(
            rules={'field': ['max:20']},
            request={'field': 10}
        )
        self.assert_fails(
            rules={'field': ['max:10']},
            request={'field': 30}
        )

    def test_validates_mime_types(self):
        self.assert_passes(
            rules={'field': ['mime_types:image/png']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['mime_types:image/png']},
            request={'field': 1}
        )
        self.assert_fails(
            rules={'field': ['mime_types:image/xpng']},
            request={'field': self.invalid_file}
        )

    def test_validates_min(self):
        self.assert_passes(
            rules={'field': ['min:0']},
            request={'field': 10}
        )
        self.assert_fails(
            rules={'field': ['min:10']},
            request={'field': 0}
        )

    def test_validates_not_in(self):
        self.assert_passes(
            rules={'field': ['not_in:male,female']},
            request={'field': 'person'}
        )
        self.assert_fails(
            rules={'field': ['not_in:male,female']},
            request={'field': 'female'}
        )

    def test_validates_not_regex(self):
        self.assert_passes(
            rules={'field': ['not_regex:[0-9]\|']},
            request={'field': 'person\|'}
        )
        self.assert_passes(
            rules={'field': ['not_regex:\d']},
            request={'field': 'person'}
        )
        self.assert_fails(
            rules={'field': ['not_regex:\d']},
            request={'field': '10'}
        )

    def test_validates_numeric(self):
        self.assert_passes(
            rules={'field': ['numeric']},
            request={'field': '1.2004'}
        )
        self.assert_passes(
            rules={'field': ['numeric']},
            request={'field': 2000.04}
        )
        self.assert_fails(
            rules={'field': ['numeric']},
            request={'field': 'x10'}
        )

    def test_validates_present(self):
        self.assert_passes(
            rules={'field': ['present']},
            request={'field': '1.2004'}
        )
        self.assert_passes(
            rules={'field': ['present']},
            request={'field': 2000.04}
        )
        self.assert_passes(
            rules={'field': ['present']},
            request={'field': None}
        )
        self.assert_fails(
            rules={'field': ['present']},
            request={'field_2': 'x10'}
        )

    def test_validates_regex(self):
        self.assert_passes(
            rules={'field': ['regex:[0-9]']},
            request={'field': '01234567'}
        )
        self.assert_passes(
            rules={'field': ['regex:^\w']},
            request={'field': 'person'}
        )
        self.assert_fails(
            rules={'field': ['regex:\d']},
            request={'field': 'hi there'}
        )

    def test_validates_required(self):
        self.assert_passes(
            rules={'field': ['required']},
            request={'field': 'hi'}
        )
        self.assert_fails(
            rules={'field': ['required']},
            request={'field': []}
        )
        self.assert_fails(
            rules={'field': ['required']},
            request={'field': ''}
        )
        self.assert_fails(
            rules={'field': ['required']},
            request={'field': None}
        )

    def test_validates_required_if(self):
        self.assert_passes(
            rules={'field': ['required_if:field_2,one,two']},
            request={'field': 'three', 'field_2': 'one'}
        )
        self.assert_passes(
            rules={'field': ['required_if:field_2,one,two']},
            request={'field': '', 'field_2': 'three'}
        )
        self.assert_passes(
            rules={'field': ['size:0']},
            request={'field': self.image_file}
        )
        self.assert_fails(
            rules={'field': ['required_if:field_2,one,two']},
            request={'field': '', 'field_2': 'one'}
        )

    def test_validates_required_unless(self):
        self.assert_passes(
            rules={'field': ['required_unless:field_2,one,two']},
            request={'field': 'three', 'field_2': 'four'}
        )
        self.assert_passes(
            rules={'field': ['required_unless:field_2,one,two']},
            request={'field': '', 'field_2': 'one'}
        )
        self.assert_fails(
            rules={'field': ['required_unless:field_2,one,two']},
            request={'field': '', 'field_2': 'three'}
        )

    def test_validates_required_with(self):
        self.assert_passes(
            rules={'field': ['required_with:field_2']},
            request={'field': 'three', 'field_2': 'four'}
        )
        self.assert_passes(
            rules={'field': ['required_with:field_2']},
            request={'field': ''}
        )
        self.assert_passes(
            rules={'field': ['required_with:field_2']},
            request={'field': 'hi', 'field_2': ''}
        )
        self.assert_fails(
            rules={'field': ['required_with:field_2']},
            request={'field': '', 'field_2': ''}
        )

    def test_validates_required_with_all(self):
        self.assert_passes(
            rules={'field': ['required_with_all:field_2,field_3']},
            request={'field': 'three', 'field_2': 'four', 'field_3': 'five'}
        )
        self.assert_passes(
            rules={'field': ['required_with_all:field_2,field_3']},
            request={'field': '', 'field_2': 'hi'}
        )
        self.assert_fails(
            rules={'field': ['required_with_all:field_2']},
            request={'field': '', 'field_2': ''}
        )

    def test_validates_required_without(self):
        self.assert_passes(
            rules={'field': ['required_without:field_2,field_3']},
            request={'field': '', 'field_2': 'four', 'field_3': 'five'}
        )
        self.assert_passes(
            rules={'field': ['required_without:field_2,field_3']},
            request={'field': 'hello', 'field_2': 'hi'}
        )
        self.assert_fails(
            rules={'field': ['required_without:field_2,field_3']},
            request={'field': '', 'field_2': ''}
        )

    def test_validates_required_without_all(self):
        self.assert_passes(
            rules={'field': ['required_without_all:field_2,field_3']},
            request={'field': '', 'field_2': 'four'}
        )
        self.assert_passes(
            rules={'field': ['required_without_all:field_2,field_3']},
            request={'field': '', 'field_2': 'hi', 'field_3': 'there'}
        )
        self.assert_passes(
            rules={'field': ['required_without_all:field_2,field_3']},
            request={'field': 'hi' }
        )
        self.assert_fails(
            rules={'field': ['required_without_all:field_2,field_3']},
            request={'field': '' }
        )

    def test_validates_same(self):
        self.assert_passes(
            rules={'field': ['same:field_2']},
            request={'field': 1, 'field_2': 1}
        )
        self.assert_fails(
            rules={'field': ['same:field_2']},
            request={'field': 1, 'field_2': 2}
        )

    def test_validates_size(self):
        self.assert_passes(
            rules={'field': ['size:2']},
            request={'field': 'hi'}
        )
        self.assert_passes(
            rules={'field': ['size:20']},
            request={'field': 20}
        )
        self.assert_passes(
            rules={'field': ['size:20.5']},
            request={'field': '20.5'}
        )
        self.assert_passes(
            rules={'field': ['array', 'size:2']},
            request={'field': '[1, 2]'}
        )
        self.assert_fails(
            rules={'field': ['size:1']},
            request={'field': 'hi'}
        )

    def test_validates_starts_with(self):
        self.assert_passes(
            rules={'field': ['starts_with:hi']},
            request={'field': 'hi there'}
        )
        self.assert_passes(
            rules={'field': ['starts_with:2']},
            request={'field': 20}
        )
        self.assert_fails(
            rules={'field': ['starts_with:hi']},
            request={'field': '20.5'}
        )

    def test_validates_string(self):
        self.assert_passes(
            rules={'field': ['string']},
            request={'field': 'hi there'}
        )
        self.assert_passes(
            rules={'field': ['string']},
            request={'field': '20.5'}
        )
        self.assert_fails(
            rules={'field': ['string']},
            request={'field': 20}
        )

    def test_validates_timezone(self):
        self.assert_passes(
            rules={'field': ['timezone']},
            request={'field': 'Africa/Nairobi'}
        )
        self.assert_passes(
            rules={'field': ['timezone']},
            request={'field': 'Atlantic/Cape_Verde'}
        )
        self.assert_passes(
            rules={'field': ['timezone']},
            request={'field': 'Etc/Universal'}
        )
        self.assert_fails(
            rules={'field': ['timezone']},
            request={'field': 'hi'}
        )

    def test_validates_unique(self):
        self.assert_fails(
            rules={'field': ['unique']},
            request={}
        )

    def test_validates_url(self):
        self.assert_passes(
            rules={'field': ['url']},
            request={'field': 'https://google.com'}
        )
        self.assert_passes(
            rules={'field': ['url']},
            request={'field': 'http://127.0.0.1:8080'}
        )
        self.assert_passes(
            rules={'field': ['url']},
            request={'field': 'ftp://127.0.0.1:8080'}
        )
        self.assert_fails(
            rules={'field': ['url']},
            request={'field': 'hi'}
        )

    def test_allows_nullable_fields(self):
        self.assert_passes(
            rules={'field': ['integer', 'nullable']},
            request={}
        )
        self.assert_passes(
            rules={'field': ['string', 'email', 'nullable']},
            request={}
        )


    def test_validates_uuid(self):
        self.assert_passes(
            rules={'field': ['uuid']},
            request={'field': '06d007b0-5608-11e9-8647-d663bd873d93'}
        )
        self.assert_fails(
            rules={'field': ['uuid']},
            request={'field': '06d007b0-560647-d663bd873d93'}
        )

    def test_custom_handlers(self):
        def validate_odd(value, **kwargs):
            return value % 2
        self.processor.register_rule_handler(
            handler=validate_odd,
            message='Not odd'
        )
        self.assert_passes(
            rules={'field': ['odd']},
            request={'field': 3}
        )
        self.assert_fails(
            rules={'field': ['odd']},
            request={'field': 2}
        )

    def test_get_rule_handler(self):
        handler = self.processor._get_rule_handler('ip')
        self.assertEqual(handler.__name__, 'validate_ip')

        with self.assertRaises(ValueError):
            self.processor._get_rule_handler('wow')

    def test_assert_params_size(self):
        handler = self.processor._get_rule_handler('ip')
        self.assertEqual(handler.__name__, 'validate_ip')

        with self.assertRaises(ValueError):
            self.processor._assert_params_size(size=1, params=[], rule='hi')

    def test_compare_dates(self):
        import operator
        self.assertTrue(
            self.processor._compare_dates(
                '2018-02-10',
                '2019-02-10',
                operator.lt
            )
        )
        self.assertFalse(
            self.processor._compare_dates(
                'S',
                '2019-02-10',
                operator.lt
            )
        )

    def assert_fails(self, rules, request):
        self._assert(rules, request, False)

    def assert_passes(self, rules, request):
        self._assert(rules, request, True)

    def _assert(self, rules, request, passes):
        p = self.parser
        v = self.processor
        v.set_request(request)
        p.set_rules(rules)
        v.set_rules(p.parsed_rules())
        self.assertTrue(v.passes() if passes else v.fails())

    def tearDown(self):
        self.stream.close()

if __name__ == '__main__':
    unittest.main()
