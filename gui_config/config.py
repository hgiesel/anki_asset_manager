import os
import json

from pathlib import Path
from itertools import groupby
from jsonschema import validate, RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QDialog, QWidget, QAction
from aqt.utils import getText, showWarning, showInfo, askUser, openLink

from ..src.config import deserialize_setting, serialize_setting, write_setting
from ..src.lib.model_editor import setup_model

from .forms.config_ui import Ui_Config
from .script_tab import ScriptTab


def sort_negative_first(v):
    return abs(int(v.name)) * 2 if int(v.name) < 0 else abs(int(v.name)) * 2 + 1

class ConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.ui = Ui_Config()
        self.ui.setupUi(self)

    def setupUi(self, modelId, modelName, setting):
        self.modelId = modelId

        self.setWindowTitle(f'Assets for {modelName}')

        self.ui.wbButton.clicked.connect(self.writeBackCurrentSetting)
        self.ui.saveButton.clicked.connect(self.saveCurrentSetting)
        self.ui.cancelButton.clicked.connect(self.cancel)

        self.ui.helpButton.clicked.connect(self.showHelp)

        self.ui.configWidget.setupUi(self.modelId, setting)

    def writeBackCurrentSetting(self, isClicked):
        setting_data = self.ui.configWidget.exportData()

        write_setting(self.modelId, setting_data)
        setup_model(self.modelId)

        self.accept()

    def saveCurrentSetting(self, isClicked):
        setting_data = self.ui.configWidget.exportData()

        write_setting(self.modelId, setting_data)

        self.accept()

    def cancel(self, isClicked):
        if askUser('Discard changes?'):
            self.reject()

    def showHelp(self):
        openLink('https://ankiweb.net/shared/info/656021484')
