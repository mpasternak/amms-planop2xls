# -*- encoding: utf-8 -*-

from amms_planop2xls.storage import get_db, get_model


def test_get_db(qtbot):
    db = get_db()
    assert db is not False


def test_get_model(program, qtbot):
    db = get_db()
    model = get_model(program.window, db)
    assert model is not False
