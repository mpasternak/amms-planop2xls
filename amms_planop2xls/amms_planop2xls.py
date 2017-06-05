# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from pathlib import Path

import secretary
import xlrd
import xlwt
from PyQt5 import QtWidgets, QtCore, QtGui

from . import __version__
from .mainwindow_ui import Ui_MainWindow
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

        if not fns:
            QtWidgets.QMessageBox.warning(
                None,
                "Hola, hola",
                "Nie zaznaczyłeś żadnego pliku wzorcowego (templatki).")
            return

        if self.danePacjentowTable.rowCount() < 1:
            QtWidgets.QMessageBox.warning(
                None,
                "Hola, hola",
                "Twój plan operacji nie zawiera żadnych zabiegów.")
            return

        header = []
        for col_no in range(12):
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
            for col_no in range(12):
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

    def importujPDFDialog(self):
        path = QtCore.QStandardPaths.locate(
            QtCore.QStandardPaths.DownloadLocation, "",
            QtCore.QStandardPaths.LocateDirectory)

        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Wybierz plik", path,
            "Pliki PDF (*.pdf);;Wszystkie pliki (*)",
            **QFileDialog_platform_kwargs)
        if fn[0]:
            try:
                self.window.setCursor(QtCore.Qt.WaitCursor)
                self.importujPDF(fn[0])
            except Exception as e:
                self.window.setCursor(QtCore.Qt.ArrowCursor)

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
            finally:
                self.window.setCursor(QtCore.Qt.ArrowCursor)

    def importujPDF(self, fn):
        data, tabela = pobierz_plan(fn)
        self.data = data
        self.wyczyscDanePacjentowZTabeli()
        for row_no, row in enumerate(tabela):
            self.danePacjentowTable.insertRow(row_no)
            for col_no, col in enumerate(row):
                if col_no == 10:
                    col = col[:80]
                self.danePacjentowTable.setItem(
                    row_no, col_no, QtWidgets.QTableWidgetItem(col)
                )
        self.danePacjentowTable.resizeColumnsToContents()

    def documentPath(self):
        path = QtCore.QStandardPaths.locate(
            QtCore.QStandardPaths.DocumentsLocation, "",
            QtCore.QStandardPaths.LocateDirectory)

        return path

    def zapiszXLSWybierzPlikDocelowy(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(
            self.window, "Wybierz plik docelowy", self.documentPath(),
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
            self.window, "Wybierz plik wejściowy",
            self.documentPath(), "Pliki XLS (*.xls)",
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
            for col_no in range(12):
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

    qtranslator = QtCore.QTranslator()
    translations_path = QtCore.QLibraryInfo.location(
        QtCore.QLibraryInfo.TranslationsPath)
    qtranslator.load("qtbase_pl", translations_path)

    app.installTranslator(qtranslator)
    win = QtWidgets.QMainWindow()
    icon_path = (Path(__file__) / ".." / "amms-planop2xls.svg").resolve()
    print(str(icon_path))
    icon = QtGui.QIcon(str(icon_path))
    print(icon)
    win.setWindowIcon(icon)
    app.setWindowIcon(icon)
    prog = AMMSPlanOp2XLS(win)
    win.show()

    if len(sys.argv) > 1 and sys.argv[1]:
        prog.importujPDF(sys.argv[1])

    sys.exit(app.exec_())


if __name__ == '__main__':
    entry_point()
