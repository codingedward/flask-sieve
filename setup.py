from setuptools import setup, find_packages


setup(
    name='flask-sieve',
    description='A Laravel inspired requests validator for Flask',
    long_description='Find the documentation at https://flask-sieve.readthedocs.io/en/latest/',
    version='1.2.1',
    url='https://github.com/codingedward/flask-sieve',
    license='BSD-2',
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
        'filetype',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    project_urls={
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/codingedward/flask-sieve/',
        'Tracker': 'https://github.com/codingedward/flask-sieve/issues',
    },
    python_requires='>=3.5',
    zip_safe=False
)
