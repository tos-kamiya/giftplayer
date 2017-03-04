#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.1'

setup(
    name='giftplayer',
    version=version,
    install_requires=requirements,
    author='Toshihiro Kamiya',
    author_email='kamiya@mgj.nifty.com',
    packages=find_packages(),
    data_files=[('giftplayer', ['giftplayer/jquery-3.1.1.min.js', 'giftplayer/match_question.js', 'giftplayer/sample.gift'])],
    include_package_data=True,
    url='https://github.com/tos-kamiya/giftplayer/',
    license='License :: OSI Approved :: BSD License',
    description='a handy GIFT quiz player',
)
