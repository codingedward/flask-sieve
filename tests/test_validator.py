import unittest

from flask_sieve.validator import Validator


class TestValidator(unittest.TestCase):
    def setUp(self):
        self._validator = Validator()

    def test_translates_validations(self):
        self.set_validator_params(
            rules={'email': 'required|email'},
            request={'email': 'invalid_email'},
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('valid email', str(self._validator.messages()))

    def test_translates_validations_with_param(self):
        self.set_validator_params(
            rules={'name': 'required|string|min:6'},
            request={'name': 'joe'},
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('6 characters', str(self._validator.messages()))

    def test_translates_validations_with_rest_params(self):
        self.set_validator_params(
            rules={'name': 'required_unless:email,a@b.com,c@d.com'},
            request={'email': 'e@f.com'}
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('required unless', str(self._validator.messages()))

    def test_translates_validations_with_all_params(self):
        self.set_validator_params(
            rules={'name': 'required_with:email,age'},
            request={'email': 'a@b.com', 'age': 2}
        )
        self.assertTrue(self._validator.fails())
        self.assertIn('required when', str(self._validator.messages()))

    def set_validator_params(self, rules=None, request=None):
        rules = rules or {}
        request = request or {}
        self._validator.set_rules(rules)
        self._validator.set_request(request)
