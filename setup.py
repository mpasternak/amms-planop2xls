#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.sdist import sdist

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}


class PreSdistCommand(sdist):
    def run(self):
        if build_ui:
            self.run_command("build_ui")
        sdist.run(self)

cmdclass['sdist'] = PreSdistCommand

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

setup_requirements = [
    "pyqt-distutils==0.7.2"
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
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass=cmdclass
)
