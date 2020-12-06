#!/bin/bash

watchman-make -p "**/*.py" --run "nosetests --with-coverage --cover-package flask_sieve"
