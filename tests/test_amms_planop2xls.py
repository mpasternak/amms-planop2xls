# -*- encoding: utf-8 -*-

from pathlib import Path

import xlrd
from PyQt5 import QtWidgets, QtCore

from amms_planop2xls.amms_planop2xls import AMMSPlanOp2XLS


def test_wczytaj_pdf_dialog(program, qtbot, mock):
    qfd = mock.patch("PyQt5.QtWidgets.QFileDialog")
    importujPDF = mock.patch.object(program, "importujPDF", raises=Exception)
    program.importujPDFDialog()
    qfd.getOpenFileName.assert_called_once()
    importujPDF.assert_called_once()


def test_wczytaj_pdf(program, test_pdf_filename):
    program.importujPDF(test_pdf_filename)


def test_dodaj_lekarza_test_usun_lekarza(program, qtbot, mock):
    qtbot.mouseClick(program.dodajPrzypisanieButton, QtCore.Qt.LeftButton)
    qtbot.mouseClick(program.usunPrzypisanieButton, QtCore.Qt.LeftButton)


def test_storage(program):
    from amms_planop2xls.storage import get_db, get_model

    db = get_db()
    assert db is not False
    model = get_model(program.window, db)
    model.select()


def test_pobierz_plan(test_pdf_filename):
    from amms_planop2xls.util import pobierz_plan

    data, dane = pobierz_plan(test_pdf_filename)
    assert data == "28.04.2017"
    assert dane[0][0] == "A"
    assert dane[0][2] == "28.04.2017"
    assert dane[0][4] == "Jan Nowak"


def test_main_window_getdb_failure(mock, qtbot):
    critical = mock.patch("PyQt5.QtWidgets.QMessageBox.critical")
    get_db = mock.patch("amms_planop2xls.amms_planop2xls.get_db",
                        return_value=False)

    AMMSPlanOp2XLS(QtWidgets.QMainWindow())
    get_db.assert_called_once()
    critical.assert_called_once()


def test_wczytaj_pdf_dialog_failure(mock, qtbot, program):
    mock.patch.object(program, "importujPDF", side_effect=Exception("omg"))
    mock.patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName", return_value=(
        "foo", True))
    box = mock.patch("PyQt5.QtWidgets.QMessageBox.critical")
    program.importujPDFDialog()
    box.assert_called_once()


def test_zapisz_xls_wybierz_plik_docelowy(mock, qtbot, program):
    zapiszXLS = mock.patch.object(program, "zapiszXLS",
                                  side_effect=Exception("lol"))
    mock.patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName",
               return_value=("fn", True))
    critical = mock.patch("PyQt5.QtWidgets.QMessageBox.critical")
    information = mock.patch("PyQt5.QtWidgets.QMessageBox.information")

    program.zapiszXLSWybierzPlikDocelowy()
    critical.assert_called_once()

    zapiszXLS.side_effect = None
    program.zapiszXLSWybierzPlikDocelowy()
    information.assert_called_once()


def test_zapisz_xls(mock, qtbot, program, tmpdir):
    fn = Path(tmpdir) / "test.xls"
    program.zapiszXLS(fn.resolve())
    t = xlrd.open_workbook(fn.resolve())
    sheets = t.sheet_names()
    assert (len(list(sheets)) == 1)
