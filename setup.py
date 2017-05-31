# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='xbee-bridge',
    version='0.1.0',
    description='DigiMesh to MQTT Bridge',
    long_description=readme,
    author='Echo1 COnsulting',
    author_email='=',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

