#!/bin/bash

watchman-make -p "**/*.py" --run "rm .coverage; nosetests --nocapture --with-coverage --cover-package flask_sieve"
