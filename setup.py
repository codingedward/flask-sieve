"""
"""

from setuptools import setup

setup(
    name='flask-sieve',
    description='A Laravel inspired requests validator',
    version='0.0.1',
    url='https://github.com/codingedward/flask-sieve',
    license='MIT',
    author='Edward Njoroge',
    author_email='codingedward@gmail.com',
    maintainer='Edward Njoroge',
    maintainer_email='codingedward@gmail.com',
    install_requires=[
        'Flask',
    ],
    classifiers=[
        'Programming Language :: Python 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['flask_sieve']
)
