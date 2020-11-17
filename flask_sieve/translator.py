import re

from flask_sieve.lang.en import rule_messages


class Translator:
    def __init__(self, validations=None, custom_messages=None,
            handler_messages=None):
        self._validations = validations or {}
        self._custom_messages = custom_messages or {}
        self._handler_messages = handler_messages or {}
        self._size_rules = ['between', 'gt', 'gte', 'lt', 'lte', 'max', 'min', 'size']

    def set_custom_messages(self, messages):
        self._custom_messages = messages

    def set_handler_messages(self, messages):
        self._handler_messages = messages

    def set_validations(self, validations):
        self._validations = validations

    def translated_errors(self):
        error_messages = {}
        for attribute, validations in self._validations.items():
            translated = []
            for validation in validations:
                if not validation['is_valid']:
                    validation_key = validation['attribute'] + '.' + validation['rule']
                    if validation_key in self._custom_messages:
                        translated.append(self._custom_messages[validation_key])
                    else:
                        translated.append(self._translate_validation(validation))
            if len(translated):
                error_messages[attribute] = translated
        return error_messages

    def _translate_validation(self, validation):
        messages = self._get_all_messages()
        message = messages.get(validation['rule'])
        if validation['rule'] in self._size_rules:
            message = message[validation['attribute_type']]
        message_fields = self._extract_message_fields(message)
        fields_to_params = \
            self._zip_fields_to_params(fields=message_fields,
                                       params=validation['params'])
        for field in message_fields:
            if field == ':attribute':
                message = message.replace(field, ' '.join([word for word in
                        validation['attribute'].split('_') if word != '']))
            else:
                message = message.replace(field, fields_to_params[field])
        return message

    def _get_all_messages(self):
        messages = {}
        messages.update(rule_messages)
        messages.update(self._handler_messages)
        return messages

    @staticmethod
    def _extract_message_fields(message):
        return re.findall(':\w+', message)

    @staticmethod
    def _zip_fields_to_params(params, fields):
        zipped = {}
        for field in fields:
            if field == ':attribute':
                continue
            _, param_index = field.split('_')
            if param_index == 'all':
                zipped[field] = ', '.join(params)
            elif param_index == 'rest':
                zipped[field] = ', '.join(params[1:])
            else:
                index = int(param_index)
                zipped[field] = params[index]
        return zipped
