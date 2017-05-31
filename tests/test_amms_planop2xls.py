# -*- encoding: utf-8 -*-

from pathlib import Path

import xlrd
from PyQt5 import QtWidgets, QtCore


def test_wczytaj_pdf_dialog(program, qtbot, mock):
    qfd = mock.patch("PyQt5.QtWidgets.QFileDialog")
    importujPDF = mock.patch.object(program, "importujPDF", raises=Exception)
    program.importujPDFDialog()
    qfd.getOpenFileName.assert_called_once()
    importujPDF.assert_called_once()


def test_wczytaj_pdf(program, pdf_filename):
    program.importujPDF(pdf_filename)


def test_pobierz_plan(pdf_filename):
    from amms_planop2xls.util import pobierz_plan

    data, dane = pobierz_plan(pdf_filename)
    assert data == "28.04.2017"
    assert dane[0][0] == "A"
    assert dane[0][2] == "28.04.2017"
    assert dane[0][4] == "Jan Nowak"


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


def test_zapisz_xls(mock, qtbot, z_pacjentem, tmpdir):
    fn = Path(tmpdir) / "test.xls"
    z_pacjentem.zapiszXLS(fn.resolve())
    t = xlrd.open_workbook(fn.resolve())
    sheets = t.sheet_names()
    assert (len(list(sheets)) == 1)


def test_wczytaj_xls_wybierz_plik_docelowy(mock, program):
    mock.patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName",
               return_value=("fn", True))
    wczytaj = mock.patch.object(program, "wczytajXLS")
    program.wczytajXLSWybierzPlikZrodlowy()
    wczytaj.assert_called_once()

    critical = mock.patch("PyQt5.QtWidgets.QMessageBox.critical")
    wczytaj = mock.patch.object(program, "wczytajXLS",
                                side_effect=Exception("lol"))
    program.wczytajXLSWybierzPlikZrodlowy()
    critical.assert_called_once()


def test_wczytaj_xls(z_pacjentem, tmpdir):
    fn = Path(tmpdir) / "test.xls"
    path = fn.resolve()
    z_pacjentem.zapiszXLS(path)
    z_pacjentem.wczytajXLS(path)


def test_dodaj_pacjenta_generuj_wydruki(qtbot, z_pacjentem, mock,
                                        template_filename):
    """
    :type program: :class:`amms_planop2xls.amms_planop2xls.AMMSPlanOp2XLS`
    """
    mock.patch.object(
        z_pacjentem.templatkiTable, "selectedIndexes", return_value=[1, ])
    mock.patch.object(
        z_pacjentem.templatkiModel, "filePath", return_value=template_filename)
    mock.patch("os.write")
    from amms_planop2xls import amms_planop2xls
    secretary = mock.patch.object(amms_planop2xls, "secretary")
    Renderer = secretary.Renderer
    open_file = mock.patch("amms_planop2xls.amms_planop2xls.open_file")
    qtbot.mouseClick(z_pacjentem.generujWydrukiButton, QtCore.Qt.LeftButton)
    open_file.assert_called_once()
    Renderer.assert_called_once()


def test_dodaj_pacjenta_brak_plikow(qtbot, program, mock,
                                    template_filename):
    mock.patch.object(
        program.templatkiTable, "selectedIndexes", return_value=[1, ])
    mock.patch.object(
        program.templatkiModel, "filePath", return_value=template_filename)
    warning = mock.patch("PyQt5.QtWidgets.QMessageBox.warning")
    qtbot.mouseClick(program.generujWydrukiButton, QtCore.Qt.LeftButton)
    warning.assert_called_once()


def test_dodaj_pacjenta_brak_pacjentow(qtbot, z_pacjentem, mock):
    warning = mock.patch("PyQt5.QtWidgets.QMessageBox.warning")
    qtbot.mouseClick(z_pacjentem.generujWydrukiButton, QtCore.Qt.LeftButton)
    warning.assert_called_once()


def test_wyczysc_pacjentow(qtbot, z_pacjentem, mock):
    """
    :type program: :class:`amms_planop2xls.amms_planop2xls.AMMSPlanOp2XLS`
    """

    question = mock.patch("PyQt5.QtWidgets.QMessageBox.question",
                          return_value=QtWidgets.QMessageBox.Yes)

    qtbot.mouseClick(z_pacjentem.wyczyscPacjentowButton, QtCore.Qt.LeftButton)
    question.assert_called_once()
    assert z_pacjentem.danePacjentowTable.rowCount() == 0


def test_dodaj_usun_pacjenta(qtbot, program, mock):
    """
    :type qtbot: :class:`pytestqt.qtbot.QtBot`
    :type program: :class:`amms_planop2xls.amms_planop2xls.AMMSPlanOp2XLS`
    """
    qtbot.mouseClick(program.dodajPacjentaButton, QtCore.Qt.LeftButton)
    qtbot.mouseDClick(program.danePacjentowTable.viewport(),
                      QtCore.Qt.LeftButton,
                      pos=QtCore.QPoint(10, 10))
    assert program.danePacjentowTable.rowCount() == 1
    qtbot.keyClicks(program.danePacjentowTable.viewport(), "f")
    qtbot.mouseClick(program.usunPacjentaButton, QtCore.Qt.LeftButton)
    assert program.danePacjentowTable.rowCount() == 0


def test_browser_clicked(qtbot, program, mock):
    assert program.tabWidget.currentIndex() == 0
    program.browserClicked(QtCore.QUrl("tab://1"))
    assert program.tabWidget.currentIndex() == 1

    open = mock.patch("webbrowser.open")
    program.browserClicked(QtCore.QUrl("http://openoffice.org"))
    open.assert_called_once()


def test_otworz_katalog_templatek(qtbot, program, mock):
    open_file = mock.patch("amms_planop2xls.amms_planop2xls.open_file")
    program.otworzKatalogTemplatek()
    open_file.assert_called_once()


def test_otworz_templatke(qtbot, program, mock):
    mock.patch.object(
        program.templatkiTable, "selectedIndexes", return_value=[1, ])
    mock.patch.object(
        program.templatkiModel, "filePath", return_value="foo")
    open_file = mock.patch("amms_planop2xls.amms_planop2xls.open_file")

    program.otworzTemplatke()
    open_file.assert_called_once()


def test_entry_point(mock):
    from amms_planop2xls import amms_planop2xls
    exit = mock.patch("sys.exit")
    mock.patch("PyQt5.QtWidgets.QMainWindow")
    mock.patch("PyQt5.QtWidgets.QApplication")
    a = mock.patch.object(amms_planop2xls, "AMMSPlanOp2XLS")
    amms_planop2xls.entry_point()
    exit.assert_called_once()
    a.assert_called_once()
