# -*- encoding: utf-8 -*-

from PyQt5 import QtSql, QtCore


def get_db():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('lekarze.db')

    query = QtSql.QSqlQuery()
    return False
    if not db.open():
        return False

    query.exec_("""
    CREATE TABLE IF NOT EXISTS lekarze_v0(
        pk INTEGER PRIMARY KEY,
        lekarz VARCHAR,
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

