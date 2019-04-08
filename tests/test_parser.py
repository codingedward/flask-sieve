import unittest

from flask_sieve.parser import Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self._parser = Parser()

    def test_parses_rules_correctly(self):
        rules = {
            'name': ['required', 'string', 'min:6'],
            'email': ['required', 'email', 'in:a@b.com,b@c.com'],
            'password': ['required', 'min:8', 'confirmed']
        }
        self._parser.set_rules(rules)
        parsed_rules = self._parser.parsed_rules()
        self.assertDictEqual(
            parsed_rules,
            {
                'name': [
                    {'name': 'required', 'params': []},
                    {'name': 'string', 'params': []},
                    {'name': 'min', 'params': ['6']}
                ],
                'email': [
                    {'name': 'required', 'params': []},
                    {'name': 'email', 'params': []},
                    {'name': 'in', 'params': ['a@b.com', 'b@c.com']},
                ],
                'password': [
                    {'name': 'required', 'params': []},
                    {'name': 'min', 'params': ['8']},
                    {'name': 'confirmed', 'params': []},
                ]

            }
        )
