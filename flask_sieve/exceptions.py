from flask import jsonify

class ValidationException(Exception):
    def __init__(self, errors):
        self.errors = errors


def register_error_handler(app):
    def validations_error_handler(ex):
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': ex.errors
        }), 400
    app.register_error_handler(
        ValidationException,
        validations_error_handler
    )

