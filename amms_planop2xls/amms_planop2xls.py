# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import xlrd
import secretary
import xlwt
from PyQt5 import QtWidgets, QtCore

from . import __version__
from .mainwindow_ui import Ui_MainWindow
from .storage import get_db, get_model, oddzial_dla_lekarza
from .util import oblicz_dzien_przed
from .util import pobierz_plan, datadir, open_file

QFileDialog_platform_kwargs = {}
if sys.platform == 'darwin':
    QFileDialog_platform_kwargs = dict(
        options=QtWidgets.QFileDialog.DontUseNativeDialog)

class AMMSPlanOp2XLS(Ui_MainWindow):
    def __init__(self, win):
        Ui_MainWindow.__init__(self)
        self.window = win
        self.setupUi(win)
        self.data = ""
        self.importujPDFButton.clicked.connect(self.importujPDFDialog)
        self.zapiszXLSButton.clicked.connect(
            self.zapiszXLSWybierzPlikDocelowy)

        #
        # # Connect "add" button with a custom function (addInputTextToListbox)
        # self.addBtn.clicked.connect(self.addInputTextToListbox)

        # db
        self.db = get_db()
        if not self.db:
            QtWidgets.QMessageBox.critical(
                None,
                "Błąd bazy danych",
                "Nie można otworzyć bazy danych.",
                QtWidgets.QMessageBox.Close)
            QtCore.QCoreApplication.exit(-1)
            return

        self.model = get_model(self.window, self.db)
        self.daneLekarzyTable.setModel(self.model)
        self.daneLekarzyTable.hideColumn(0)
        self.daneLekarzyTable.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)

        self.model.dataChanged.connect(self.uzupelnijLekarzy)

        self.dodajPrzypisanieButton.clicked.connect(self.dodajLekarza)
        self.usunPrzypisanieButton.clicked.connect(self.usunLekarza)
        self.odswiezPrzypisaniaButton.clicked.connect(self.odswiezPrzypisania)

        # templatki
        self.templatkiModel = QtWidgets.QFileSystemModel()
        self.templatkiModel.setRootPath(datadir())
        self.templatkiModel.setNameFilters(['*.odt'])
        self.templatkiModel.setNameFilterDisables(False)
        self.templatkiTable.setModel(self.templatkiModel)
        self.templatkiTable.setRootIndex(self.templatkiModel.index(datadir()))
        self.templatkiTable.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.templatkiModel.directoryLoaded.connect(
            self.templatkiTable.resizeColumnsToContents)
        self.templatkiModel.fileRenamed.connect(
            self.templatkiTable.resizeColumnsToContents)

        self.otworzKatalogButton.clicked.connect(self.otworzKatalogTemplatek)
        self.otworzTemplatkeButton.clicked.connect(self.otworzTemplatke)
        self.generujWydrukiButton.clicked.connect(self.generujWydruki)

        # browser
        self.witajBrowser.setOpenLinks(False)
        self.witajBrowser.anchorClicked.connect(self.browserClicked)

        #

        self.wczytajXLSButton.clicked.connect(
            self.wczytajXLSWybierzPlikZrodlowy)

        #

        self.dodajPacjentaButton.clicked.connect(
            self.dodajPacjenta
        )

        self.usunPacjentaButton.clicked.connect(
            self.usunPacjenta
        )

        #

        self.wyczyscPacjentowButton.clicked.connect(self.wyczyscPacjentow)

    def wyczyscPacjentow(self):
        res = QtWidgets.QMessageBox.question(
            None, "Potwierdź", "Czy na pewno wyczyścić dane planu "
                               "operacyjnego?")

        if res == QtWidgets.QMessageBox.Yes:
            self.wyczyscDanePacjentowZTabeli()

    def wyczyscDanePacjentowZTabeli(self):
        self.danePacjentowTable.clearContents()
        for elem in range(self.danePacjentowTable.rowCount()):
            self.danePacjentowTable.removeRow(0)

    def dodajPacjenta(self):
        self.danePacjentowTable.insertRow(
            self.danePacjentowTable.rowCount())

    def usunPacjenta(self):
        rows = set(
            [x.row() for x in self.danePacjentowTable.selectedIndexes()])

        cnt = 0
        for row in sorted(rows):
            self.danePacjentowTable.removeRow(row - cnt)
            cnt += 1

    def browserClicked(self, url):
        s = url.scheme()
        u = url.url()
        if s == "tab":
            self.tabWidget.setCurrentIndex(int(u[-1]))
        else:
            import webbrowser
            webbrowser.open(u)

    def otworzKatalogTemplatek(self):
        open_file(datadir())

    def otworzTemplatke(self):
        fns = set()
        for idx in self.templatkiTable.selectedIndexes():
            fp = self.templatkiModel.filePath(idx)
            fns.add(fp)

        for fp in fns:
            open_file(fp)

    def generujWydruki(self):
        fns = set()
        for idx in self.templatkiTable.selectedIndexes():
            fp = self.templatkiModel.filePath(idx)
            fns.add(fp)

        header = []
        for col_no in range(11):
            value = self.danePacjentowTable.horizontalHeaderItem(
                col_no).text()
            value = value.replace(" ", "_")
            value = value.replace("ł", "l")
            value = value.replace("ę", "e")
            value = value.replace("ó", "o").lower()
            header.append(value)

        pacjenci = []
        for row_no in range(self.danePacjentowTable.rowCount()):
            dct = {}
            for col_no in range(11):
                value = self.danePacjentowTable.item(row_no, col_no)
                text = ''
                if hasattr(value, "text"):
                    text = value.text()
                dct[header[col_no]] = text
            pacjenci.append(dct)


        engine = secretary.Renderer()

        for fp in fns:
            try:
                result = engine.render(
                    fp,
                    pacjenci=pacjenci,
                    data=self.data,
                    dzien_przed=oblicz_dzien_przed(self.data),
                    wersja=__version__)

            except Exception as e:
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = "".join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback, limit=3))

                QtWidgets.QMessageBox.critical(
                    None,
                    "Błąd renderowania pliku",
                    "Błąd renderowania pliku.\n\n"
                    "Skopiuj poniższą informację i wyślij autorowi "
                    "oprogramowania na adres e-mail wraz z plikiem ODT "
                    "(templatki) który wywołał błąd.\n\n"
                    "%s" % exception)
                continue

            handle, pathname = \
                tempfile.mkstemp(".odt", "amms-planop2xls-")
            os.write(handle, result)
            os.close(handle)
            open_file(pathname)

    def odswiezPrzypisania(self):
        self.daneLekarzyTable.resizeColumnsToContents()
        self.daneLekarzyTable.repaint()

    def dodajLekarza(self):
        self.model.insertRows(self.model.rowCount(), 1)

    def usunLekarza(self):
        rows = set([x.row() for x in self.daneLekarzyTable.selectedIndexes()])
        for unique_row in rows:
            self.model.removeRow(unique_row)
        self.model.select()

    def importujPDFDialog(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Wybierz plik", QtCore.QDir.homePath(),
            "Pliki PDF (*.pdf);;Wszystkie pliki (*)",
            **QFileDialog_platform_kwargs)
        if fn[0]:
            try:
                self.importujPDF(fn[0])
            except Exception as e:
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = "".join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback, limit=3))

                QtWidgets.QMessageBox.critical(
                    None,
                    "Błąd wczytywania pliku",
                    "Błąd wczytywania pliku.\n\n"
                    "Skopiuj poniższą informację i wyślij autorowi "
                    "oprogramowania na adres e-mail wraz z plikiem PDF, "
                    "który wywołał błąd.\n\n"
                    "%s" % exception)

    def importujPDF(self, fn):
        data, tabela = pobierz_plan(fn)
        self.data = data
        self.danePacjentowTable.clearContents()
        for row_no, row in enumerate(tabela):
            self.danePacjentowTable.insertRow(row_no)
            for col_no, col in enumerate(row):
                if col_no == 10:
                    col = col[:80]
                self.danePacjentowTable.setItem(
                    row_no, col_no, QtWidgets.QTableWidgetItem(col)
                )
        self.uzupelnijLekarzy()
        self.danePacjentowTable.resizeColumnsToContents()

    def uzupelnijLekarzy(self):
        for row_no in range(self.danePacjentowTable.rowCount()):
            item = self.danePacjentowTable.item(row_no, 9)
            text = item.text()
            if not text:
                continue
            try:
                lekarz = text.split(", ")[0].strip()
            except IndexError:
                continue
            oddzial = oddzial_dla_lekarza(self.db, lekarz)
            if oddzial:
                self.danePacjentowTable.setItem(
                    row_no, 1, QtWidgets.QTableWidgetItem(oddzial))

        self.odswiezPrzypisania()

    def zapiszXLSWybierzPlikDocelowy(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(
            self.window, "Wybierz plik docelowy", QtCore.QDir.homePath(),
            "Pliki XLS (*.xls)",
            **QFileDialog_platform_kwargs)
        if fn[0]:
            try:
                self.zapiszXLS(fn[0])
            except Exception as e:
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = "".join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback, limit=3))

                QtWidgets.QMessageBox.critical(
                    None,
                    "Błąd zapisywania pliku",
                    "Błąd zapisywania pliku.\n\n"
                    "Skopiuj poniższą informację i wyślij autorowi "
                    "oprogramowania na adres e-mail wraz z plikiem PDF, "
                    "który wywołał błąd.\n\n"
                    "%s" % exception)
            else:
                QtWidgets.QMessageBox.information(
                    None,
                    "Plik zapisano",
                    "Dane w formacie XLS zostały zapisane.\n\n"
                    "Pełna ścieżka do pliku: \n%s" % Path(fn[0]).resolve())

    def wczytajXLSWybierzPlikZrodlowy(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Wybierz plik wejściowy", QtCore.QDir.homePath(),
            "Pliki XLS (*.xls)",
            **QFileDialog_platform_kwargs)
        if fn[0]:
            try:
                self.wczytajXLS(fn[0])
            except Exception as e:
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = "".join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback, limit=3))

                QtWidgets.QMessageBox.critical(
                    None,
                    "Błąd wczytywania pliku",
                    "Błąd wczytywania pliku.\n\n"
                    "Skopiuj poniższą informację i wyślij autorowi "
                    "oprogramowania na adres e-mail wraz z plikiem PDF, "
                    "który wywołał błąd.\n\n"
                    "%s" % exception)

    def wczytajXLS(self, fn):
        xl_workbook = xlrd.open_workbook(fn)
        sheet_names = xl_workbook.sheet_names()
        self.data = sheet_names[0].split("Zabiegi dnia ")[1]

        xl_sheet = xl_workbook.sheet_by_index(0)

        self.wyczyscDanePacjentowZTabeli()

        num_cols = xl_sheet.ncols
        for row_idx in range(0, xl_sheet.nrows):
            self.danePacjentowTable.insertRow(
                self.danePacjentowTable.rowCount())

            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx, col_idx)
                self.danePacjentowTable.setItem(
                    row_idx, col_idx,
                    QtWidgets.QTableWidgetItem(cell_obj.value)
                )

    def zapiszXLS(self, fn):
        book = xlwt.Workbook(encoding="utf-8")

        sheet = book.add_sheet("Zabiegi dnia %s" % self.data)
        for row_no in range(self.danePacjentowTable.rowCount()):
            for col_no in range(11):
                value = self.danePacjentowTable.item(row_no, col_no)
                text = ''
                if hasattr(value, "text"):
                    text = value.text()
                sheet.write(row_no, col_no, text)

        output = open(fn, "wb")
        book.save(output)
        output.close()


def entry_point():
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    prog = AMMSPlanOp2XLS(win)
    win.show()

    if len(sys.argv) > 1 and sys.argv[1]:
        prog.importujPDF(sys.argv[1])

    sys.exit(app.exec_())


if __name__ == '__main__':
    entry_point()
