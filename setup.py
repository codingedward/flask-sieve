"""
"""

from setuptools import setup

setup(
    name='flask-sieve',
    description='A Laravel inspired requests validator for Flask',
    version='0.0.1.dev0',
    url='https://github.com/codingedward/flask-sieve',
    license='Apache 2.0',
    author='Edward Njoroge',
    author_email='codingedward@gmail.com',
    maintainer='Edward Njoroge',
    maintainer_email='codingedward@gmail.com',
    install_requires=[
        'Flask',
        'Pillow',
        'python-dateutil',
        'pytz',
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['flask_sieve'],
    project_urls={
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/codingedward/flask-sieve/',
        'Tracker': 'https://github.com/codingedward/flask-sieve/issues',
    },
    python_requires='>= 2.7'
)
