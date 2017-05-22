#!/usr/bin/env python3

from setuptools import setup, find_packages

from giftplayer import __version__

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='giftplayer',
    version=__version__,
    install_requires=requirements,
    author='Toshihiro Kamiya',
    author_email='kamiya@mbj.nifty.com',
    entry_points="""
      [console_scripts]
      giftplayer = giftplayer:main
      """,
    packages=find_packages(),
    package_data={'giftplayer': ['jquery-3.1.1.min.js', 'match_question.js']},
    include_package_data=True,
    url='https://github.com/tos-kamiya/giftplayer/',
    license='License :: OSI Approved :: BSD License',
    description='a handy GIFT quiz player',
)
