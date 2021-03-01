#!/bin/bash

watchman-make -p "**/*.py" --run "rm .coverage; nosetests --with-coverage --cover-package flask_sieve"
