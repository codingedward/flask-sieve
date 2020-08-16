# Flask-Sieve
[![](https://travis-ci.org/codingedward/flask-sieve.svg?branch=master)](https://travis-ci.org/codingedward/flask-sieve)
[![](https://readthedocs.org/projects/flask-sieve/badge/?version=latest)](https://flask-sieve.readthedocs.io/en/latest/?badge=latest)
[![](https://coveralls.io/repos/github/codingedward/flask-sieve/badge.svg?branch=master)](https://coveralls.io/github/codingedward/flask-sieve?branch=master)
[![](https://api.codacy.com/project/badge/Grade/041c02c078b649a98b5c8c58bd8fd015)](https://www.codacy.com/app/codingedward/flask-sieve?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codingedward/flask-sieve&amp;utm_campaign=Badge_Grade)
[![](https://pepy.tech/badge/flask-sieve)](https://pepy.tech/project/flask-sieve)
[![](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://pypi.org/project/flask-sieve/)


<img src="https://raw.githubusercontent.com/codingedward/flask-sieve/master/docs/source/_static/sieve.png" style="width: 40%; float: right; transform: rotate(-15deg)" />
A requests validator for Flask inspired by Laravel.

This package provides an approach to validating incoming requests using powerful and composable rules.

## Installation
To install and update using [pip](https://pip.pypa.io/en/stable/quickstart/).
```shell
pip install -U flask-sieve
```

## Quickstart

To learn about these powerful validation features, let's look at a complete example of validating a form and displaying the error messages back to the user.

### Auto-validation of Requests

Suppose you had a simple application with an endpoint to register a user.

```shell
flask-app/
  __init__.py
  app.py
  app_requests.py
```

We are going to create validations for this endpoint.

```python
# app.py

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=('POST',))
def register():
    return jsonify({'message': 'Registered!'}), 200

app.run()
```

To validate incoming requests to this endpoint, we create a class with validation rules of registering a user as follows:

```python
# app_requests.py

from flask_sieve import FormRequest

class RegisterRequest(FormRequest):
    def rules(self):
        return {
            'email': ['required', 'email'],
            'username': ['required', 'string', 'min:6'],
            'password': ['required', 'min:6', 'confirmed']
        }
```

Now, using this class, we can guard our endpoint using a `validate` decorator.


```python
# app.py

from flask import Flask
from flask_sieve import Sieve, validate
from .app_requests import RegisterRequest

app = Flask(__name__)
Sieve(app)

@app.route('/', methods=('POST',))
@validate(RegisterRequest)
def register():
    return jsonify({'message': 'Registered!'}), 200

app.run()
```

Note the initialization of `Sieve` with the application instance. This is required
for setting up the necessary mechanism to autorespond with the error messages.

### Manual Validation of Requests

Sometimes you might not wish to rely on the default auto-response made by Flask-Sieve. In this case,
you can create an instance of `Validator` and set the rules yourself.

Using the same application shown above, this is how you would go about it:

```python
# app.py

from flask import Flask, jsonify, request
from flask_sieve import Sieve, Validator

app = Flask(__name__)
Sieve(app)

@app.route('/', methods=('POST',))
def register():
    rules = {
        'email': ['required', 'email'],
        'avatar': ['image', 'dimensions:200x200'],
        'username': ['required', 'string', 'min:6'],
    }
    validator = Validator(rules=rules, request=request)
    if validator.passes():
        return jsonify({'message': 'Registered!'}), 200
    return jsonify(validator.messages()), 400

app.run()
```

This would allow you to make the correct response in cases where you would not want to rely
on the response format provided by Flask-Sieve.


## Digging Deeper

Flask-Sieve supports various approaches to validating requests. Here we will make an in-depth
tour of the functionalities offered.

#### Form vs JSON Requests
To address the differences in requests with form requests (with `Content-Type: 'multipart/form-data'`)
and JSON requests (with `Content-Type: 'application/json'`) Flask-Sieve supports two kinds of auto-validating
requests:

##### Form Requests
To validate form requests, you have to inherit from `FormRequest` on the validation request. Example:

```python
from flask_sieve import FormRequest

class PostRequest(FormRequest):
    def rules(self):
        return {
            'image': ['file'],
            'username': ['required', 'string', 'min:6'],
        }
```

##### JSON Requests
To validate this format you will have to inherit from `JsonRequest`.
Before validating the request, this checks that the request is indeed a JSON request (with `Content-Type: 'application/json'`).

```python
from flask_sieve import JsonRequest

class PostRequest(JsonRequest):
    def rules(self):
        return {
            'email': ['required', 'email'],
        }
```


### Error Messages Format

In case validation fails to pass, the following is the format of the generated response:
```js
{
    success: False,
    message: 'Validation error',
    errors: {
        'email': [
            'The email is required.',
            'The email must be a valid email address.'
        ],
        'password': [
            'The password confirmation does not match.'
        ]
    }
}
```
All validation error messages will have a HTTP error status code 400.

### Stopping on First Validation Failure

Sometimes you may wish to stop running validation rules on an attribute after the first validation failure. To do so, assign the `bail` rule to the attribute:

```python
# app_requests.py

# ... omitted for brevity ...
def rules(self):
    return {
        'body': ['required'],
        'title': ['bail', 'string', 'required', 'max:255'],
    }
```

In this example, if the `string` rule on the `title` attribute fails, the `max` rule will not be checked. Rules will be validated in the order they are assigned.

### A Note on Nested Attributes

If your HTTP request contains "nested" parameters, you may specify them in your validation rules using "dot" syntax:


```python
# app_requests.py

# ... omitted for brevity ...

def rules(self):
    return {
        'author.name': ['required'],
        'author.description': ['required'],
    }
```

### Customizing the Error Messages

You may customize the error messages used by the form request by overriding the `messages` method. This method should return an array of attribute / rule pairs and their corresponding error messages:

```python
# app_requests.py

from flask_sieve import FormRequest

class RegisterRequest(FormRequest):
    def messages(self):
        return {
            'email.required': 'The email is required',
            'password.confirmed': 'Password must be at least 6 characters'
        }

    def rules(self):
        return {
            'email': ['required', 'email'],
            'username': ['required', 'string', 'min:6'],
            'password': ['required', 'min:6', 'confirmed',]
        }
```

### Adding Custom Rules

Besides the rules offered by default, you can extend the validator with your own custom rules. You can
do this either when defining the Form/JSON Request class or when you instantiate a `Validator`.

#### Custom Rule Handler

A rule handler is a predicate (a method returning either `True` or `False`) that you can use to add
your validations to Flask-Sieve.

This method must satisfy the following conditions:
- It must start with the `validate_` keyword.
- It will receive keyword the following keyword parameters:
    - `value` - the value of the request field being validated.
    - `attribute` - the field name being validated.
    - `params` - a list of parameters passed to the rule. For instance, for the inbuilt rule `between:min,max`, the list will be `[min, max]`.
    - `nullable` - a boolean marking whether this field has been specified as `nullable` or not.
    - `rules` - a list containing all the rules passed on the field.

**Tip**: In case your handler does not need all these parameters, you can simply ignore the ones you don't need with `**kwargs`.

For example:
```python
def validate_odd(value, **kwargs):
    return int(value) %  2
```

#### Custom Rules on Form/JSON Requests

To define a custom rule validator on a Form/JSON Rquest, you will have to provide it in a method named
`custom_handlers` as follows:

```python
from flask_sieve import FormRequest

def validate_odd(value, **kwargs):
    return int(value) % 2

class RegisterRequest(FormRequest):

    # ... omitted for brevity ...

    def custom_handlers(self):
        return [{
            'handler': validate_odd,  # the rule handler
            'message': 'Number must be odd', # the message to display when this rule fails
            'params_count': 0 # the number of parameters the rule expects
        }]
```

#### Custom Rules on `Validator` Instance

To add a custom rule handler to a `Validator` instance, you have will have to use
`register_rule_handler` method as shown below:

```python
from flask import Flask, jsonify, request
from flask_sieve import Sieve, Validator

app = Flask(__name__)
Sieve(app)

def validate_odd(value, **kwargs):
    return int(value) % 2

@app.route('/', methods=('POST',))
def register():
    rules = {'avatar': ['image', 'dimensions:200x200']}
    validator = Validator(rules=rules, request=request)
    validator.register_rule_handler(
        handler=validate_odd,
        message='Must be odd',
        params_count=0
    )
    if validator.passes():
        return jsonify({'message': 'Registered!'}), 200
    return jsonify(validator.messages()), 400

```
## Available Validations

#### accepted

The field under validation must be _yes_, _on_, _1_, or _true_. This is useful for validating "Terms of Service" acceptance.

#### active_url

The field under validation must be active and responds to a request from `requests` Python package.

#### after:_date_

The field under validation must be a value after a given date. The dates will be passed into the `parse` function from [`python-dateutil`](https://pypi.org/project/python-dateutil/) Python
```python
'start_date': ['required', 'date', 'after:2018-02-10']
```


#### after\_or\_equal:_date_

The field under validation must be a value after or equal to the given date.

#### alpha

The field under validation must be entirely alphabetic characters.

#### alpha_dash

The field under validation may have alpha-numeric characters, as well as dashes and underscores.

#### alpha_num

The field under validation must be entirely alpha-numeric characters.

#### array

The field under validation must be an `array` string.

#### bail

Stop running validation rules after the first validation failure.

#### before:_date_

The field under validation must be a value preceding the given date. The dates will be passed into the Python [`python-dateutil`](https://pypi.org/project/python-dateutil/) package.

#### before\_or\_equal:_date_

The field under validation must be a value preceding or equal to the given date. The dates will be passed into the `parse` function from [`python-dateutil`](https://pypi.org/project/python-dateutil/) Python package.

#### between:_min_,_max_

The field under validation must have a size between the given _min_ and _max_. Strings, numerics, arrays, and files are evaluated in the same fashion as the `size` rule.

#### boolean

The field under validation must be able to be cast as a boolean. Accepted input are `true`, `false`, `1`, `0`, `"1"`, and `"0"`.

#### confirmed

The field under validation must have a matching field of `foo_confirmation`. For example, if the field under validation is `password`, a matching `password_confirmation` field must be present in the input.

#### date

The field under validation must be a valid, non-relative date according to the `parse` function of [`python-dateutil`](https://pypi.org/project/python-dateutil/).

#### date_equals:_date_

The field under validation must be equal to the given date. The dates will be passed into the `parse` function of [python-dateutil](https://pypi.org/project/python-dateutil/).

#### different:_field_

The field under validation must have a different value than _field_.

#### digits:_value_

The field under validation must be _numeric_ and must have an exact length of _value_.

#### digits_between:_min_,_max_

The field under validation must have a length between the given _min_ and _max_.

#### dimensions

The file under validation must be an image meeting the dimension constraints specified as `WidthxHeight`

```python
'avatar': ['dimensions:200x200']
```

#### distinct

When working with arrays, the field under validation must not have any duplicate values.

```python
'foo': ['distinct']
```

#### email

The field under validation must be formatted as an e-mail address.

#### file

The field under validation must be a successfully uploaded file.

#### filled

The field under validation must not be empty when it is present.

#### gt:_field_

The field under validation must be greater than the given _field_. The two fields must be of the same type. Strings, numerics, arrays, and files are evaluated using the same conventions as the `size` rule.

#### gte:_field_

The field under validation must be greater than or equal to the given _field_. The two fields must be of the same type. Strings, numerics, arrays, and files are evaluated using the same conventions as the `size` rule.

#### image

The file under validation must be an image (jpeg, png, bmp, gif, tif, or svg)

#### in:_foo_,_bar_,...

The field under validation must be included in the given list of values.

#### in_array:_anotherfield_

The field under validation must exist in _anotherfield_'s values.

#### integer

The field under validation must be an integer.

#### ip

The field under validation must be an IP address.

#### ipv4

The field under validation must be an IPv4 address.

#### ipv6

The field under validation must be an IPv6 address.

#### json

The field under validation must be a valid JSON string.

#### lt:_field_

The field under validation must be less than the given _field_. The two fields must be of the same type. Strings, numerics, arrays, and files are evaluated using the same conventions as the `size` rule.

#### lte:_field_

The field under validation must be less than or equal to the given _field_. The two fields must be of the same type. Strings, numerics, arrays, and files are evaluated using the same conventions as the `size` rule.

#### max:_value_

The field under validation must be less than or equal to a maximum _value_. Strings, numerics, arrays, and files are evaluated in the same fashion as the `size` rule.

#### mime_types:_text/plain_,...

The file under validation must match one of the given MIME types:

```python
'video': ['mime_types:video/avi,video/mpeg,video/quicktime']
```

To determine the MIME type of the uploaded file, the file's contents will be read and the framework will attempt to guess the MIME type, which may be different from the client provided MIME type.

#### min:_value_

The field under validation must have a minimum _value_. Strings, numerics, arrays, and files are evaluated in the same fashion as the `size` rule.

#### not_in:_foo_,_bar_,...

The field under validation must not be included in the given list of values.

#### not_regex:_pattern_

The field under validation must not match the given regular expression.

#### nullable

The field under validation may be `None`. This is particularly useful when validating primitive such as strings and integers that can contain `None` values.

#### numeric

The field under validation must be numeric.

#### present

The field under validation must be present in the input data but can be empty.

#### regex:_pattern_

The field under validation must match the given regular expression.

#### required

The field under validation must be present in the input data and not empty. A field is considered "empty" if one of the following conditions are true:

<div class="content-list" markdown="1">

- The value is `None`.
- The value is an empty string.
- The value is an empty array.

</div>

#### required_if:_anotherfield_,_value_,...

The field under validation must be present and not empty if the _anotherfield_ field is equal to any _value_.

#### required_unless:_anotherfield_,_value_,...

The field under validation must be present and not empty unless the _anotherfield_ field is equal to any _value_.

#### required_with:_foo_,_bar_,...

The field under validation must be present and not empty _only if_ any of the other specified fields are present.

#### required_with_all:_foo_,_bar_,...

The field under validation must be present and not empty _only if_ all of the other specified fields are present.

#### required_without:_foo_,_bar_,...

The field under validation must be present and not empty _only when_ any of the other specified fields are not present.

#### required_without_all:_foo_,_bar_,...

The field under validation must be present and not empty _only when_ all of the other specified fields are not present.

#### same:_field_

The given _field_ must match the field under validation.

#### size:_value_

The field under validation must have a size matching the given _value_. For string data, _value_ corresponds to the number of characters. For numeric data, _value_ corresponds to a given integer value. For an array, _size_ corresponds to the `count` of the array. For files, _size_ corresponds to the file size in kilobytes.

#### starts_with:_foo_,_bar_,...

The field under validation must start with one of the given values.

#### string

The field under validation must be a string. If you would like to allow the field to also be `None`, you should assign the `nullable` rule to the field.

#### timezone

The field under validation must be a valid timezone identifier according to the [`pytz`](http://pytz.sourceforge.net/) Python package.

#### url

The field under validation must be a valid URL.

#### uuid

The field under validation must be a valid RFC 4122 (version 1, 3, 4, or 5) universally unique identifier (UUID).

## Contributions

Contributions and bugfixes are welcome!

## License (BSD-2)

A Flask package for validating requests (Inspired by Laravel).

Copyright © 2019 Edward Njoroge

All rights reserved.

Find a copy of the License [here](https://github.com/codingedward/flask-sieve/blob/master/LICENSE.txt).
