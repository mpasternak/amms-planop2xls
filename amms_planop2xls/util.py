# -*- encoding: utf-8 -*-

import re
from pathlib import Path

from PyQt5 import QtCore
from drunken_child_in_the_fog.core import DrunkenChildInTheFog
from pdf_table_extractor.pdf_table_extractor import extract_table_data

pacjent_regex = re.compile(
    r"(?P<imienazwisko>.*)\(PESEL: (?P<pesel>\d+), Nr KG: \d\d\d\d\/"
    r"(?P<nrkg>\d+)\)")

data_zabiegu_regex = re.compile(
    "Plan operacyjny: na dzień (?P<data>\d+\.\d+\.\d+) .*")


def datadir():
    add = ""
    cnt = 0
    while True:
        ret = Path(QtCore.QDir.homePath()) / (".amms-planop2xls%s" % add)
        if not ret.exists():
            ret.mkdir()

        if ret.exists():
            if not ret.is_dir():
                cnt += 1
                add = "-%i" % cnt
                continue
            return str(ret)


def pobierz_plan(fn):
    doc1 = DrunkenChildInTheFog(open(fn, "rb")).get_document()
    label = doc1.everything().text().all()[0].text
    data_zabiegu = data_zabiegu_regex.match(label).group("data")
    del doc1, label

    tabela = []
    aktualna_sala = ""
    for table in extract_table_data(open(fn, "rb")):
        for row in table:
            if row[6].startswith("Sala"):
                aktualna_sala = row[6][11:]
                continue

            if row[1] == "Lp.":
                continue

            if not row[1]:
                continue

            m = pacjent_regex.match(row[4])

            personel = row[-3].replace(" (OG)", ""). \
                replace(" (AS)", ""). \
                replace(" (A2)", "").split(",")

            tabela.append([
                aktualna_sala,
                "",
                data_zabiegu,
                row[1],
                m.group("imienazwisko").strip(),
                m.group("pesel").strip(),
                m.group("nrkg").strip(),
                row[5],
                row[6],
                ", ".join(personel),
                row[10]
            ])
    return data_zabiegu, tabela
