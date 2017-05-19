# -*- encoding: utf-8 -*-

from amms_planop2xls import util


def test_datadir():
    d = util.datadir()
    assert d is not None


def test_pobierz_plan(test_pdf_filename):
    p = util.pobierz_plan(test_pdf_filename)
    assert len(p) == 2


def test_oblicz_dzien_przed():
    assert util.oblicz_dzien_przed("28.04.2017") == "27.04.2017"
    assert util.oblicz_dzien_przed("1.01.2017") == "31.12.2016"


def test_open_file():
    util.open_file("test.pdf")
