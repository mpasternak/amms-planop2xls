#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "PyQt5==5.8.2",
    "pdf-table-extractor==0.1.1",
    "xlwt==1.2.0",
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='amms_planop2xls',
    version='0.1.0',
    description="Konwerter plików PDF z planem operacyjnym z systemu Asseco Medical Management Solutions",
    long_description=readme + '\n\n' + history,
    author="Michał Pasternak",
    author_email='michal.dtz@gmail.com',
    url='https://github.com/mpasternak/amms-planop2xls',
    packages=[
        'amms_planop2xls',
    ],
    package_dir={'amms_planop2xls':
                 'amms_planop2xls'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='amms_planop2xls',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
