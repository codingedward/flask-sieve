#!/bin/bash

pipenv install twine wheel
python setup.py sdist && python setup.py bdist_wheel && twine upload dist/*
git reset hard HEAD
