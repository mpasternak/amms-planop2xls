# -*- coding: utf-8 -*-

import re
import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from .mainwindow import Ui_MainWindow
from .util import pobierz_plan
from .storage import get_db, get_model

class AMMSPlanOp2XLS(Ui_MainWindow):
    def __init__(self, win):
        Ui_MainWindow.__init__(self)
        self.window = win
        self.setupUi(win)

        self.wczytajPDFButton.clicked.connect(self.wczytajPDFDialog)
        #
        # # Connect "add" button with a custom function (addInputTextToListbox)
        # self.addBtn.clicked.connect(self.addInputTextToListbox)

    def wczytajPDFDialog(self):
        qfd = QtWidgets.QFileDialog(
            self.window, "Wybierz pliki", QtCore.QDir.homePath(),
            "Pliki PDF(*.pdf);;Wszystkie pliki(*)")
        qfd.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        qfd.fileSelected.connect(self.wczytajPDF)
        qfd.show()

    def wczytajPDF(self, fn):
        data, tabela = pobierz_plan(fn)

        self.danePacjentowTable.clear()

        for row_no, row in enumerate(tabela):
            self.danePacjentowTable.insertRow(row_no)
            for col_no, col in enumerate(row):
                self.danePacjentowTable.setItem(
                    row_no, col_no, QtWidgets.QTableWidgetItem(col)
                )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    prog = AMMSPlanOp2XLS(win)
    win.show()

    # db
    db = get_db()
    if not db:
        QtWidgets.QMessageBox.critical(
            None,
            "Błąd bazy danych",
            "Nie można otworzyć bazy danych.",
            QtWidgets.QMessageBox.Close)
        sys.exit(-1)

    model = get_model(app, db)
    prog.daneLekarzyTable.setModel(model)
    prog.daneLekarzyTable.hideColumn(0)

    def dodaj():
        model.insertRows(model.rowCount(), 1)
    prog.dodajPrzypisanieButton.clicked.connect(dodaj)

    def usun():
        for elem in prog.daneLekarzyTable.selectedIndexes():
            model.removeRows(elem.row(), 1)
        model.select()
    prog.usunPrzypisanieButton.clicked.connect(usun)

    if len(sys.argv) > 1 and sys.argv[1]:
        prog.wczytajPDF(sys.argv[1])

    sys.exit(app.exec_())
