# Flask-Sieve
[![](https://travis-ci.org/codingedward/flask-sieve.svg?branch=master)](https://travis-ci.org/codingedward/flask-sieve)
[![](https://readthedocs.org/projects/flask-sieve/badge/?version=latest)](https://flask-sieve.readthedocs.io/en/latest/?badge=latest)
[![](https://coveralls.io/repos/github/codingedward/flask-sieve/badge.svg?branch=master)](https://coveralls.io/github/codingedward/flask-sieve?branch=master)
[![](https://api.codacy.com/project/badge/Grade/041c02c078b649a98b5c8c58bd8fd015)](https://www.codacy.com/app/codingedward/flask-sieve?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codingedward/flask-sieve&amp;utm_campaign=Badge_Grade)
[![](https://pepy.tech/badge/flask-sieve)](https://pepy.tech/project/flask-sieve)
[![](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://pypi.org/project/flask-sieve/)


A requests validator for Flask inspired by Laravel.

This package provides an approach to validating incoming requests using powerful and composable rules. 

## Installing
To install and update using [pip](https://pip.pypa.io/en/stable/quickstart/).
```shell
pip install -U flask-sieve
```

## Quickstart

To learn about these powerful validation features, let's look at a complete example of validating a form and displaying the error messages back to the user.

### Example App

Suppose you had a simple application with an endpoint to register a user. We are going to create validations for this endpoint.

```python
# app.py

from flask import Flask

app = Flask(__name__)

@app.route('/', methods=('POST',))
def register():
    return 'Registered!'

app.run()
```

### The Validation Logic

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

@app.route('/', methods=('POST'))
@validate(RegisterRequest)
def register():
    return 'Registered!'

app.run()
```

If the validation fails, the proper response is automatically generated. 


## Documentation

Find the documentation [here](https://flask-sieve.readthedocs.io/en/latest/).


## License (BSD-2)

A Flask package for validating requests (Inspired by Laravel).

Copyright © 2019 Edward Njoroge

All rights reserved.

Find a copy of the License [here](https://github.com/codingedward/flask-sieve/blob/master/LICENSE.txt).
