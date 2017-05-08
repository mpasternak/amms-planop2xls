# -*- encoding: utf-8 -*-
import os

import PyQt5
import pytest


@pytest.fixture
def test_pdf_filename():
    return os.path.join(os.path.dirname(__file__), "test.pdf")


@pytest.fixture
def program(qtbot):
    """Pass the application to the test functions via a pytest fixture.
    """
    from amms_planop2xls.amms_planop2xls import AMMSPlanOp2XLS

    window = PyQt5.QtWidgets.QMainWindow()
    program = AMMSPlanOp2XLS(window)
    qtbot.add_widget(window)
    window.show()
    return program
