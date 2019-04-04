"""
"""

class Parser:
    def __init__(self, rules=None):
        self._rules = rules or {}

    def set_rules(self, rules):
        self._rules = rules

    def parsed_rules(self):
        parsed_rules = {}
        for attribute, rules in self._rules.items():
            attribute_rules = []
            for rule in rules.split('|'):
                rule_name = rule_params = None
                if ':' in rule:
                    rule_name, rule_params = rule.split(':')
                    rule_params = rule_params.split(',')
                else:
                    rule_name = rule
                    rule_params = []

                attribute_rules.append({
                    'name': rule_name,
                    'params': rule_params,
                })

            parsed_rules[attribute] = attribute_rules
        return parsed_rules
