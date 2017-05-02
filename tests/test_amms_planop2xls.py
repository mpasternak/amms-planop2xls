#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_amms_planop2xls
----------------------------------

Tests for `amms_planop2xls` module.
"""

import pytest


from amms_planop2xls import amms_planop2xls


@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

