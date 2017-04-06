#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.1.4'

setup(
    name='giftplayer',
    version=version,
    install_requires=requirements,
    author='Toshihiro Kamiya',
    author_email='kamiya@mgj.nifty.com',
    scripts=['giftplayer_run'],
    packages=find_packages(),
    package_data={'giftplayer': ['jquery-3.1.1.min.js', 'match_question.js', 'sample.gift']},
    include_package_data=True,
    url='https://github.com/tos-kamiya/giftplayer/',
    license='License :: OSI Approved :: BSD License',
    description='a handy GIFT quiz player',
)
