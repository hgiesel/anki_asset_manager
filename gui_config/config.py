import os
import json

from pathlib import Path
from itertools import groupby
from jsonschema import validate, RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QDialog, QWidget, QAction
from aqt.utils import (
    getText,
    showWarning,
    showInfo,
    askUser,
    openLink,
    restoreGeom,
    saveGeom,
)

from .forms.config_ui import Ui_Config


def sort_negative_first(v):
    return abs(int(v.name)) * 2 if int(v.name) < 0 else abs(int(v.name)) * 2 + 1


class ConfigDialog(QDialog):
    geom_name = "assetManagerConfigDialog"

    def __init__(self, parent, save_callback, write_back_callback):
        super().__init__(parent=parent)

        self.save_callback = save_callback
        self.write_back_callback = write_back_callback

        self.ui = Ui_Config()
        self.ui.setupUi(self)

        self.accepted.connect(self.save_geom)
        self.rejected.connect(self.save_geom)

        restoreGeom(self, self.geom_name)

    def setupUi(self, modelId, modelName, htmlSetting, scriptSetting):
        self.modelId = modelId

        self.setWindowTitle(f"Assets for {modelName}")

        self.ui.helpButton.clicked.connect(self.showHelp)
        self.ui.wbButton.clicked.connect(self.writeBackCurrentSetting)
        self.ui.saveButton.clicked.connect(self.saveCurrentSetting)
        self.ui.cancelButton.clicked.connect(self.cancel)

        self.ui.configWidgetHtml.setupUi(self.modelId, htmlSetting)
        self.ui.configWidget.setupUi(self.modelId, scriptSetting)

    def writeBackCurrentSetting(self, isClicked):
        self.write_back_callback(*self.export_data())
        self.accept()

    def saveCurrentSetting(self, isClicked):
        self.save_callback(*self.export_data())
        self.accept()

    def showHelp(self):
        openLink("https://ankiweb.net/shared/info/656021484")

    def cancel(self, isClicked):
        if askUser("Discard changes?"):
            self.reject()

    def export_data(self):
        html_data = self.ui.configWidgetHtml.exportData()
        script_data = self.ui.configWidget.exportData()

        return self.modelId, html_data, script_data

    def save_geom(self):
        saveGeom(self, self.geom_name)
