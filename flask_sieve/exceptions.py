from flask import jsonify


class ValidationException(Exception):
    def __init__(self, errors):
        self.errors = errors


def register_error_handler(app):
    def validations_error_handler(ex):
        response = {
            'message': app.config.get('SIEVE_RESPONSE_MESSAGE', 'Validation error'),
            'errors': ex.errors
        }

        if app.config.get('SIEVE_INCLUDE_SUCCESS_KEY'):
            response['success'] = False

        if app.config.get('SIEVE_RESPONSE_WRAPPER'):
            response = {app.config.get('SIEVE_RESPONSE_WRAPPER'): response}

        return jsonify(response), app.config.get('SIEVE_INVALID_STATUS_CODE', 400)

    app.register_error_handler(
        ValidationException,
        validations_error_handler
    )
