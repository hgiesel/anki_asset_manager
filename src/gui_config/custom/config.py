import os
import json

from pathlib import Path
from itertools import groupby
from jsonschema import validate, RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QDialog, QWidget, QAction
from aqt.utils import getText, showWarning, showInfo

from ...config import deserialize_setting, serialize_setting, write_setting
from ...lib.model_editor import setup_model

from ..config_ui import Ui_Config

from .setting_update import SettingUpdate
from .script_tab import ScriptTab

def sort_negative_first(v):
    return abs(int(v.name)) * 2 if int(v.name) < 0 else abs(int(v.name)) * 2 + 1

class ConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.ui = Ui_Config()
        self.ui.setupUi(self)

        self.ui.cancelButton.clicked.connect(self.reject)

    def saveCurrentSetting(self, isClicked):
        setting_data = self.ui.configWidget.exportData()

        write_setting(self.modelId, setting_data)

        self.accept()

    def wbCurrentSetting(self, isClicked):
        setting_data = self.ui.configWidget.exportData()

        write_setting(self.modelId, setting_data)
        setup_model(setting_data)

        self.accept()

    def setupUi(self, modelId, setting):
        self.modelId = modelId

        self.ui.saveButton.clicked.connect(self.saveCurrentSetting)
        self.ui.wbButton.clicked.connect(self.wbCurrentSetting)

        self.ui.helpButton.clicked.connect(self.showHelp)
        self.ui.aboutButton.clicked.connect(self.showAbout)

        self.ui.configWidget.setupUi(self.modelId, setting)

    def showHelp(self):
        pass
    def showAbout(self):
        pass
