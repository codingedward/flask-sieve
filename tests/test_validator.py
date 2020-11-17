import json
import unittest

from flask import Flask

from flask_sieve.validator import Validator, validate

class TestValidator(unittest.TestCase):
    def setUp(self):
        self._validator = Validator()

    def test_translates_validations(self):
        self.set_validator_params(
            rules={'email_address': ['required', 'email']},
            request={'email_address': 'invalid_email'},
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('valid email address', str(self._validator.messages()))

    def test_translates_validations_with_param(self):
        self.set_validator_params(
            rules={'first_name': ['required', 'string', 'min:6']},
            request={'first_name': 'joe'},
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('6 characters', str(self._validator.messages()))
        self.assertIn('first name', str(self._validator.messages()))

    def test_translates_validations_with_rest_params(self):
        self.set_validator_params(
            rules={'name': ['required_unless:email,a@b.com,c@d.com']},
            request={'email': 'e@f.com'}
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('required unless', str(self._validator.messages()))

    def test_translates_validations_with_all_params(self):
        self.set_validator_params(
            rules={'name': ['required_with:email,age']},
            request={'email': 'a@b.com', 'age': 2}
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('required when', str(self._validator.messages()))

    def test_handles_different_types_of_requests(self):
        class MockMultiDict:
            def to_dict(self, flat=None):
                return {'field': 1}

        class MockRequest:
            def __init__(self):
                self.is_json = True
                self.form = self.files = MockMultiDict()
                self.json = self.form.to_dict()


        request = MockRequest()
        validator = Validator(request=request, rules={'field': ['numeric']})
        self.assertTrue(validator.passes())
        request.is_json = False
        validator.set_request(request)
        self.assertTrue(validator.passes())

    def test_validate_decorator(self):
        class FailingRequest:
            def validate(self):
                raise ValueError()
        @validate(FailingRequest)
        def failing_request_endpoint():
            pass
        with self.assertRaises(ValueError):
            failing_request_endpoint()

        class PassingRequest:
            def validate(self):
                pass
        @validate(PassingRequest)
        def passing_request_endpoint():
            return True
        self.assertTrue(passing_request_endpoint())

    def test_translates_validations_with_custom_messages(self):
        self.set_validator_params(
            rules={'email': ['required', 'email']},
            request={'email': ''}
        )
        self._validator.set_custom_messages({
            'email.required': 'Kindly provide the email',
            'email.email': 'Whoa! That is not valid',
        })
        self.assertTrue(self._validator.fails())
        self.assertDictEqual({
            'email': [
                'Kindly provide the email',
                'Whoa! That is not valid'
            ]
        }, self._validator.messages())

    def test_translates_validations_with_custom_messages_on_constructor(self):
        validator = Validator(
            rules={'email': ['required', 'email']},
            request={'email': ''},
            messages={
                'email.required': 'Kindly provide the email',
                'email.email': 'Whoa! That is not valid',
            }
        )
        self.assertTrue(validator.fails())
        self.assertDictEqual({
            'email': [
                'Kindly provide the email',
                'Whoa! That is not valid'
            ]
        }, validator.messages())

    def test_translates_validations_with_custom_handler(self):
        def validate_odd(value, **kwargs):
            return int(value) % 2
        self._validator.register_rule_handler(
            handler=validate_odd,
            message='This number must be odd.',
            params_count=0
        )
        self.set_validator_params(
            rules={'number': ['odd']},
            request={'number': 4}
        )
        self.assertTrue(self._validator.fails())
        self.assertDictEqual({
            'number': [
                'This number must be odd.'
            ]
        }, self._validator.messages())
        self.set_validator_params(
            rules={'number': ['odd']},
            request={'number': 3}
        )
        self.assertTrue(self._validator.passes())

    def test_translates_validations_set_through_custom_handlers(self):
        def validate_odd(value, **kwargs):
            return int(value) % 2
        self._validator.set_custom_handlers([
            {
                'handler': validate_odd,
                'message':'This number must be odd.',
                'params_count':0
            }
        ])
        self.set_validator_params(
            rules={'number': ['odd']},
            request={'number': 4}
        )
        self.assertTrue(self._validator.fails())
        self.assertDictEqual({
            'number': [
                'This number must be odd.'
            ]
        }, self._validator.messages())
        self.set_validator_params(
            rules={'number': ['odd']},
            request={'number': 3}
        )
        self.assertTrue(self._validator.passes())

    def test_cannot_set_custom_handler_without_validate_keyword(self):
        def method_odd(value, **kwargs):
            return int(value) % 2
        with self.assertRaises(ValueError):
            self._validator.register_rule_handler(
                handler=method_odd,
                message='This number must be odd.',
                params_count=0
            )

    def set_validator_params(self, rules=None, request=None):
        rules = rules or {}
        request = request or {}
        self._validator.set_rules(rules)
        self._validator.set_request(request)

