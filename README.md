# Flask-Sieve
[![Build Status](https://travis-ci.org/codingedward/flask-sieve.svg?branch=master)](https://travis-ci.org/codingedward/flask-sieve)
[![Coverage Status](https://coveralls.io/repos/github/codingedward/flask-sieve/badge.svg?branch=master)](https://coveralls.io/github/codingedward/flask-sieve?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/041c02c078b649a98b5c8c58bd8fd015)](https://www.codacy.com/app/codingedward/flask-sieve?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codingedward/flask-sieve&amp;utm_campaign=Badge_Grade)

A Laravel inspired requests validator for Flask.

## Installing
To install and update using [pip](https://pip.pypa.io/en/stable/quickstart/).
```shell
pip install flask-sieve
```

## Introduction

This package provides an approach to validating your Flask app's incoming data using powerful and composable rules.

## Validation Quickstart

To learn about these powerful validation features, let's look at a complete example of validating a form and displaying the error messages back to the user.

### Example App

Suppose you had a simple application with an endpoint to register a user. We are going to create validations for this endpoint.

```python
# app.py

from flask import Flask

app = Flask(__name__)

@app.route('/', methods=('POST'))
def register():
    return 'Registered!'

app.run()
```

### The Validation Logic

To validate incoming requests to this endpoint, we create a class with validation rules of registering a user as follows:

```python
# requests.py

from flask_sieve import FormRequest

class RegisterRequest(FormRequest):
    def rules(self):
        return {
            'email': 'required|email',
            'username': 'required|string|min:6',
            'password': 'required|min:6|confirmed',
        }

```

Now, using this class, we can guard our endpoint using a `validate` decorator.


```python
# app.py

from flask import Flask
from flask_sieve import Sieve, validate
from .requests import RegisterRequest

app = Flask(__name__)
Sieve(app)

@app.route('/', methods=('POST'))
@validate(RegisterRequest)
def register():
    return 'Registered!'

app.run()
```

If the validation fails, the proper response is automatically generated.

#### Stopping On First Validation Failure

Sometimes you may wish to stop running validation rules on an attribute after the first validation failure. To do so, assign the `bail` rule to the attribute:

```python
# requests.py

# ...
def rules(self):
    return {
        'title': 'bail|string|required|max:255',
        'body': 'required',
    }
# ...
```

In this example, if the `string` rule on the `title` attribute fails, the `max` rule will not be checked. Rules will be validated in the order they are assigned.

#### A Note On Nested Attributes

If your HTTP request contains "nested" parameters, you may specify them in your validation rules using "dot" syntax:


```python
# requests.py

# ...
def rules(self):
    return {
        'author.name': 'required',
        'author.description': 'required',
    }
# ...
```

### Customizing The Error Messages

You may customize the error messages used by the form request by overriding the `messages` method. This method should return an array of attribute / rule pairs and their corresponding error messages:
```python
# requests.py

from flask_sieve import FormRequest

class RegisterRequest(FormRequest):
    def messages(self):
        return {
            'email.required': 'The email is required',
            'password.confirmed': 'Password must be at least 6 characters'
        }

    def rules(self):
        return {
            'email': 'required|email',
            'username': 'required|string|min:6',
            'password': 'required|min:6|confirmed',
        }

```

### Available Validations

#### accepted

The field under validation must be _yes_, _on_, _1_, or _true_. This is useful for validating "Terms of Service" acceptance.

#### active_url

The field under validation must be active and responds to a request from `requests` Python package.

#### after:_date_

The field under validation must be a value after a given date. The dates will be passed into the `parse` function from `python-dateutil` Python
```python
'start_date': 'required|date|after:2018-02-10'
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

The field under validation must be a value preceding the given date. The dates will be passed into the Python `python-dateutil` package.

#### before\_or\_equal:_date_

The field under validation must be a value preceding or equal to the given date. The dates will be passed into the `parse` function from `python-dateutil` Python package.

#### between:_min_,_max_

The field under validation must have a size between the given _min_ and _max_. Strings, numerics, arrays, and files are evaluated in the same fashion as the `size` rule.

#### boolean

The field under validation must be able to be cast as a boolean. Accepted input are `true`, `false`, `1`, `0`, `"1"`, and `"0"`.

#### confirmed

The field under validation must have a matching field of `foo_confirmation`. For example, if the field under validation is `password`, a matching `password_confirmation` field must be present in the input.

#### date

The field under validation must be a valid, non-relative date according to the `parse` function of `python-dateutil`.

#### date_equals:_date_

The field under validation must be equal to the given date. The dates will be passed into the `parse` function of `python-dateutil`.

#### different:_field_

The field under validation must have a different value than _field_.

#### digits:_value_

The field under validation must be _numeric_ and must have an exact length of _value_.

#### digits_between:_min_,_max_

The field under validation must have a length between the given _min_ and _max_.

#### dimensions

The file under validation must be an image meeting the dimension constraints specified as `WidthxHeight`

```python
'avatar': 'dimensions:200x200'
```

#### distinct

When working with arrays, the field under validation must not have any duplicate values.

```python
'foo': 'distinct'
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

#### in_array:_anotherfield_.*

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
'video': 'mime_types:video/avi,video/mpeg,video/quicktime'
```

To determine the MIME type of the uploaded file, the file's contents will be read and the framework will attempt to guess the MIME type, which may be different from the client provided MIME type.

#### min:_value_

The field under validation must have a minimum _value_. Strings, numerics, arrays, and files are evaluated in the same fashion as the `size` rule.

#### not_in:_foo_,_bar_,...

The field under validation must not be included in the given list of values.

#### not_regex:_pattern_

The field under validation must not match the given regular expression.

**Note:** When using the `regex` / `not_regex` patterns, it is necessary to to use python raw strings marked by `r` as shown: `'email': r'not_regex:^.+@.+$/i'`.

#### nullable

The field under validation may be `None`. This is particularly useful when validating primitive such as strings and integers that can contain `None` values.

#### numeric

The field under validation must be numeric.

#### present

The field under validation must be present in the input data but can be empty.

#### regex:_pattern_

The field under validation must match the given regular expression.

**Note:** When using the `regex` / `not_regex` patterns, it is necessary to to use python raw strings marked by `r` as shown: `'email': r'regex:^.+@.+$/i'`.

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

The field under validation must be a valid timezone identifier according to the `pytz` Python package.

#### url

The field under validation must be a valid URL.

#### uuid

The field under validation must be a valid RFC 4122 (version 1, 3, 4, or 5) universally unique identifier (UUID).

## License (BSD-2)

A Flask package for validating requests (Inspired by Laravel).
Copyright © 2019 Edward Njoroge
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Edward Njoroge ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Edward Njoroge BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation
are those of the authors and should not be interpreted as representing
official policies, either expressed or implied, of Edward Njoroge.

