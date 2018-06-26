# -*- encoding: utf-8 -*-
import pytest

from amms_planop2xls import util
from amms_planop2xls.util import pacjent_regex


def test_datadir():
    d = util.datadir()
    assert d is not None


def test_pobierz_plan(pdf_filename):
    p = util.pobierz_plan(pdf_filename)
    assert len(p) == 2


def test_pobierz_zly_plan(bad_pdf_filename):
    p = util.pobierz_plan(bad_pdf_filename)
    assert len(p) == 2


def test_oblicz_dzien_przed():
    assert util.oblicz_dzien_przed("28.04.2017") == "27.04.2017"
    assert util.oblicz_dzien_przed("1.01.2017") == "31.12.2016"


def test_open_file(pdf_filename):
    util.open_file(pdf_filename)


@pytest.mark.parametrize(
    "input,should_be",
    [
        (
            "Jolanta Drugieimie Kowalska (PESEL: 99010103234, "
            "Nr KG: 2018/312) Oddział Jako-Taki od 08-01-2018 07:31",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": "99010103234",
             "nrkg": "312",
             "oddzial": "Oddział Jako-Taki"}
        ),
        (
            "Jolanta Drugieimie Kowalska (PESEL: 99010103234, "
            "Nr KG: 2018/312)",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": "99010103234",
             "nrkg": "312",
             "oddzial": None}
        ),
        (
            "Jolanta Drugieimie Kowalska (Nr KG: 2018/312) "
            "Oddział Jako-Taki od 08-01-2018 07:31",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": None,
             "nrkg": "312",
             "oddzial": "Oddział Jako-Taki"}
        ),
        (
            "Jolanta Drugieimie Kowalska (PESEL: 99010103234) "
            "Oddział Jako-Taki od 08-01-2018 07:31",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": "99010103234",
             "nrkg": None,
             "oddzial": "Oddział Jako-Taki"}
        ),
        (
            "Jolanta Drugieimie Kowalska () Oddział Jako-Taki "
            "od 08-01-2018 07:31",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": None,
             "nrkg": None,
             "oddzial": "Oddział Jako-Taki"}
        ),
        (
            "Jolanta Drugieimie Kowalska () Oddział Jako-Taki "
            "od 08-01-2018 07:31",
            {"imienazwisko": "Jolanta Drugieimie Kowalska",
             "pesel": None,
             "nrkg": None,
             "oddzial": "Oddział Jako-Taki"}
        ),
    ]
)
def test_regex(input, should_be):
    res = pacjent_regex.match(input)
    assert res.groupdict() == should_be
