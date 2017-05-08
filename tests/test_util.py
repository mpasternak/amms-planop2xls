# -*- encoding: utf-8 -*-

from amms_planop2xls import util


def test_datadir():
    d = util.datadir()
    assert d is not None


def test_pobierz_plan(test_pdf_filename):
    p = util.pobierz_plan(test_pdf_filename)
    assert len(p) == 2
