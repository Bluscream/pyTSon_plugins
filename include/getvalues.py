from enum import Enum, unique

import sys, os, traceback, re, ts3lib, ts3defines, pytson, ts3client, devtools, io, json, pytsonui
from PythonQt.QtGui import *
from PythonQt.QtCore import Qt, QFile, QIODevice, QUrl
from PythonQt.QtUiTools import QUiLoader
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PythonQt import BoolResult
from rlcompleter import Completer
from itertools import takewhile
from tempfile import gettempdir
from zipfile import ZipFile


@unique
class ValueType(Enum):
    """
    enum to define the types of value shown and received with getValues.
    """
    boolean = 1
    integer = 2
    double = 3
    string = 4
    listitem = 5


def _createReturnDict(widgets):
    ret = {}

    for key, w in widgets.items():
        if not key in ["dialog", "buttonbox"]:
            if type(w) is QCheckBox:
                ret[key] = w.checked
            elif type(w) is QSpinBox or type(w) is QDoubleSpinBox:
                ret[key] = w.value
            elif type(w) is QLineEdit:
                ret[key] = w.text
            elif type(w) is QPlainTextEdit:
                ret[key] = w.plainText
            elif type(w) is QGroupBox:
                counter = 0
                for c in w.children():
                    if type(c) is QRadioButton:
                        if c.checked:
                            ret[key] = counter

                        counter += 1
            elif type(w) is QComboBox:
                ret[key] = w.currentIndex
            elif type(w) is QListWidget:
                ret[key] = [w.row(item) for item in w.selectedItems()]

    return ret


def getValues(parent, title, params, doneclb):
    """
    Convenience function to open a dialog to get multiple input values from the user.
    @param parent: the dialog's parent, pass None to ignore
    @type parent: QWidget (or derived type)
    @param title: the dialog's title
    @type title: str
    @param params: a dict definining the user input type {'key': (ValueType, label, startingValue, minimum, maximum)}. Potential types are defined in the enum ValueType. The label will be displayed right next to the input widget. All other elements in this tuple are dependent on the ValueType. startingValue defines a predefined value of input. Minimum and maximum define input limits.
    boolean: startingValue is bool, minimum and maximum are not used; the widget used is a QCheckBox without an extra QLabel
    integer: startingValue, minimum and maximum are int; the widget used is a QSpinBox with an extra QLabel
    double: startingValue, minimum; the widget used is a QDoubleSpinBox with an extra QLabel
    string: startingValue is str, minimum is not used, if maximum == 1 the widget used is a QLineEdit, otherwise a QPlainTextEdit with a maximumBlockCount of maximum, each with an extra QLabel
    listitem: startingValue is a tuple([str], [int]) defining the listitems in the first element, the second element is a list with prechecked item indexes, minimum is an int defining how much items the user at least has to choose, maximum is an int defining if the user can choose more than one item (maximum != 1), depending on minimum and maximum the used widget is a QGroupBox and multiple QRadioButtons, a QComboBox with an extra QLabel or a QListWidget with an extra QLabel
    @type params: dict{str: tuple(ValueType, str, int/double/str/tuple(list[str], list[int]), int/double, int/double)}
    @param doneclb: a callable which gets the dialogs return code (see QDialog.DialogCode) and on success, a dict with the resulting values, referenced by the key.
    @type doneclb: callable(int, dict{str: int/str/bool/[str]})
    @return: Returns a dict containing the used input widgets plus the dialog and the QDialogButtonBox
    @rtype: dict{str: QWidget}

    """
    ret = {}

    dlg = ret['dialog'] = QDialog(parent)
    dlg.setWindowTitle(title)

    dlg.connect("finished(int)", lambda r: (
    doneclb(r, _createReturnDict(ret)) if r == QDialog.Accepted else doneclb(r, {}), dlg.delete()))

    form = QFormLayout()
    box = ret['buttonbox'] = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok, Qt.Horizontal, dlg)
    box.connect("accepted()", dlg.accept)
    box.connect("rejected()", dlg.reject)

    vlayout = QVBoxLayout(dlg)
    vlayout.addLayout(form)
    vlayout.addWidget(box)

    dlg.setLayout(vlayout)

    for key, (t, label, start, minimum, maximum) in params.items():
        if key in ["dialog", "buttonbox"]:
            dlg.delete()
            raise Exception("Keys dialog and buttonbox are forbidden")

        if t is ValueType.boolean:
            w = ret[key] = QCheckBox(label, dlg)
            w.setChecked(start)

            form.addRow(w)
        elif t is ValueType.integer:
            l = QLabel(label, dlg)
            w = ret[key] = QSpinBox(dlg)
            w.setMinimum(minimum)
            w.setMaximum(maximum)
            w.setValue(start)

            form.addRow(l, w)
        elif t is ValueType.double:
            l = QLabel(label, dlg)
            w = ret[key] = QDoubleSpinBox(dlg)
            w.setMinimum(minimum)
            w.setMaximum(maximum)
            w.setValue(start)

            form.addRow(l, w)
        elif t is ValueType.string:
            l = QLabel(label, dlg)
            if maximum == 1:
                w = ret[key] = QLineEdit(start, dlg)
            else:
                w = ret[key] = QPlainTextEdit(start, dlg)
                w.setMaximumBlockCount(maximum)

            form.addRow(l, w)
        elif t is ValueType.listitem:
            if minimum == maximum == 1:
                grp = ret[key] = QGroupBox(label, dlg)
                layout = QVBoxLayout(grp)
                for i, s in enumerate(start[0]):
                    b = QRadioButton(s, grp)
                    b.setChecked(i in start[1])

                    layout.addWidget(b)

                form.addRow(grp)
            elif maximum == 1:
                l = QLabel(label, dlg)
                w = QComboBox(dlg)
                w.addItems(start[0])
                if len(start[1]) > 0:
                    w.setCurrentIndex(start[1][0])

                form.addRow(l, w)
            else:
                l = QLabel(label, dlg)
                w = QListWidget(dlg)
                for i, s in enumerate(start[0]):
                    item = QListWidgetItem(s, w)

                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Checked if i in start[1] else Qt.Unchecked)

                form.addRow(l, w)
        else:
            dlg.delete()
            raise Exception("Unrecognized ValueType")

    dlg.show()

    return ret
