import os
import json

from pathlib import Path
from itertools import groupby
from jsonschema import validate, RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QDialog, QWidget, QAction
from aqt.utils import getText, showWarning, showInfo

from ...lib.config import deserialize_setting, serialize_setting, write_settings
from ...lib.model_editor import setup_models

from ..sm_config_ui import Ui_SMConfig

from .sm_setting_update import SMSettingUpdate
from .sm_script_tab import SMScriptTab

def sort_negative_first(v):
    return abs(int(v.name)) * 2 if int(v.name) < 0 else abs(int(v.name)) * 2 + 1

def save_settings(settings):
    serializedSettings = [serialize_setting(setting) for setting in settings]
    write_settings(serializedSettings)

class SMConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.ui = Ui_SMConfig()
        self.ui.setupUi(self)

        self.ui.cancelButton.clicked.connect(self.reject)

    def setupUi(self, settings, startId=0):
        self.settings = settings

        def saveCurrentSetting(isClicked):
            nonlocal self
            nonlocal settings

            setting_data = self.ui.configWidget.exportData()
            oldSid = self.ui.modelChooser.findText(setting_data.model_name)
            settings[oldSid] = setting_data

            save_settings(settings)
            self.accept()

        def wbCurrentSetting(isClicked):
            nonlocal self
            nonlocal settings

            setting_data = self.ui.configWidget.exportData()
            oldSid = self.ui.modelChooser.findText(setting_data.model_name)
            settings[oldSid] = setting_data

            save_settings(settings)
            setup_models(settings)
            self.accept()

        self.ui.saveButton.clicked.connect(saveCurrentSetting)
        self.ui.wbButton.clicked.connect(wbCurrentSetting)

        self.ui.helpButton.clicked.connect(self.showHelp)
        self.ui.aboutButton.clicked.connect(self.showAbout)
        self.ui.importButton.clicked.connect(self.importDialog)

        def updateConfigWidgetFromModelchooser(newSid):
            nonlocal self
            nonlocal settings

            setting_data = self.ui.configWidget.exportData()
            oldSid = self.ui.modelChooser.findText(setting_data.model_name)
            settings[oldSid] = setting_data

            self.updateConfigWidget(settings[newSid])

        self.ui.modelChooser.setupUi(
            map(lambda v: v.model_name, settings),
            updateConfigWidgetFromModelchooser,
        )

        self.updateConfigWidget(settings[startId])

    def updateConfigWidget(self, setting):
        self.ui.configWidget.setupUi(setting)

    def importDialog(self):
        setting_data = self.ui.configWidget.exportData()
        old_sid = self.ui.modelChooser.findText(setting_data.model_name)

        def updateAfterImport(new_data):
            nonlocal old_sid
            # name of new_data is not actually used
            self.settings[old_sid] = deserialize_setting(setting_data.model_name, new_data)
            self.updateConfigWidget(self.settings[old_sid])

        dirpath = Path(f'{os.path.dirname(os.path.realpath(__file__))}', '../../json_schemas/setting.json')
        schema_path = dirpath.absolute().as_uri()

        with dirpath.open('r') as jsonfile:
            schema = json.load(jsonfile)
            resolver = RefResolver(
                schema_path,
                schema,
            )

            validator = Draft7Validator(schema, resolver=resolver, format_checker=None)

            dial = SMSettingUpdate(mw)
            dial.setupUi(
                json.dumps(serialize_setting(self.settings[old_sid]), sort_keys=True, indent=4),
                validator,
                updateAfterImport,
            )
            dial.exec_()

    def showHelp(self):
        pass
    def showAbout(self):
        pass
