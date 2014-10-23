import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-migrations-plus',
    version='0.1',
    packages=['migrations_plus'],
    include_package_data=True,
    description='Extra helpers for using django.db.migrations',
)
