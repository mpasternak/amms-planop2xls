# -*- encoding: utf-8 -*-

import os

from PyQt5 import QtSql, QtCore

from .util import datadir


def get_db():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(os.path.join(datadir(), 'lekarze.db'))
    if not db.open():
        return False

    query = QtSql.QSqlQuery()

    query.exec_("""
    CREATE TABLE IF NOT EXISTS lekarze_v0(
        pk INTEGER PRIMARY KEY,
        lekarz VARCHAR UNIQUE,
        oddzial VARCHAR)
    """)

    return db


def get_model(parent, db):
    model = QtSql.QSqlTableModel(parent, db)
    model.setTable("lekarze_v0")
    model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
    model.select()
    model.setHeaderData(0, QtCore.Qt.Horizontal, "ID")
    model.setHeaderData(1, QtCore.Qt.Horizontal, "Lekarz")
    model.setHeaderData(2, QtCore.Qt.Horizontal, "Oddział")
    return model


def db_error(query):
    import sys
    from PyQt5 import QtWidgets
    QtWidgets.QMessageBox.critical(
        None,
        "Błąd bazy danych",
        "Błąd bazy danych: " + query.lastError().text(),
        QtWidgets.QMessageBox.Close)
    sys.exit(-1)


def oddzial_dla_lekarza(db, lekarz, insert_if_not_exists=True):
    query = QtSql.QSqlQuery(db)
    query.prepare("SELECT oddzial FROM lekarze_v0 WHERE lekarz=:val")
    query.bindValue(":val", lekarz)
    res = query.exec_()
    if not res:
        db_error(query)

    if query.next():
        return query.value(0)

    oddzial = "Ustaw oddział dla %s" % lekarz
    query.prepare("INSERT INTO lekarze_v0(lekarz, oddzial) VALUES(:lekarz, "
                  ":oddzial)")
    query.bindValue(":lekarz", lekarz)
    query.bindValue(":oddzial", oddzial)
    res = query.exec_()
    if not res:
        db_error(query)
    return oddzial
