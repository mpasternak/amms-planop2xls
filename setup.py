#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pyqt_distutils.build_ui import build_ui
cmdclass = {'build_ui': build_ui}

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

reqs = lambda fn: list([x.strip() for x in open(fn).readlines() if x.strip()])      

requirements = reqs("requirements.txt")

test_requirements = reqs("requirements_dev.txt")

setup(
    name='amms_planop2xls',
    version='0.7.0',
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
    tests_require=test_requirements,
    cmdclass=cmdclass
)
