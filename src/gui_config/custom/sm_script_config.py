import os
import json

import jsonschema
from jsonschema import validate, RefResolver, Draft7Validator
from pathlib import Path

from aqt import mw
from aqt.qt import QDialog, QWidget, QFont, Qt
from aqt.utils import showInfo # actually needed!

from .js_highlighter import JSHighlighter
from .sm_setting_update import SMSettingUpdate

from ..sm_script_config_ui import Ui_SMScriptConfig

from ...lib.config import deserialize_script, serialize_script

class SMScriptConfig(QDialog):
    def __init__(self, parent, callback):
        super().__init__(parent=parent)

        self.callback = callback

        self.ui = Ui_SMScriptConfig()
        self.ui.setupUi(self)

        self.accepted.connect(self.onAccept)
        self.rejected.connect(self.onReject)

        self.ui.saveButton.clicked.connect(self.tryAccept)
        self.ui.saveButton.setDefault(True)

        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.validateButton.clicked.connect(self.validateConditions)
        self.ui.importButton.clicked.connect(self.importDialog)

        self.ui.enableScriptCheckBox.stateChanged.connect(self.enableChangeGui)
        self.initEditor(self.ui.codeTextEdit)

    def initEditor(self, editor):
        font = editor.document().defaultFont()
        font.setFamily('Courier New')
        font.setStyleHint(QFont.Monospace)
        font.setWeight(QFont.Medium)
        font.setFixedPitch(True)
        font.setPointSize(14)

        editor.setFont(font)

        self.highlighter = JSHighlighter(editor.document())

    def setupUi(self, script):
        self.ui.nameLineEdit.setText(script.name)
        self.ui.versionLineEdit.setText(script.version)
        self.ui.descriptionTextEdit.setPlainText(script.description)

        self.ui.enableScriptCheckBox.setChecked(script.enabled)

        self.ui.conditionsTextEdit.setPlainText(json.dumps(script.conditions))
        self.ui.codeTextEdit.setPlainText(script.code)

        self.enableChangeGui()

    def tryAccept(self):
        try:
            self.validateConditionsRaw()
        except:
            showInfo('Invalid Conditions. Please correct the conditions or just set it to `[]`.')
        else:
            self.accept()

    def onAccept(self):
        self.callback(self.exportData())

    def onReject(self):
        pass

    def enableChangeGui(self):
        self.enableChange(self.ui.enableScriptCheckBox.isChecked())

    def enableChange(self, state=True):
        self.ui.conditionsTextEdit.setReadOnly(not state)
        self.ui.codeTextEdit.setReadOnly(not state)
        self.ui.descriptionTextEdit.setReadOnly(not state)

        self.ui.nameLineEdit.setReadOnly(not state)
        self.ui.versionLineEdit.setReadOnly(not state)

    def getConditions(self): # can throw
        return json.loads(self.ui.conditionsTextEdit.toPlainText())

    def validateConditionsRaw(self):
        dirpath  = Path(f'{os.path.dirname(os.path.realpath(__file__))}', '../../json_schemas/script_cond.json')
        schema_path = dirpath.absolute().as_uri()

        with dirpath.open('r') as jsonfile:

            schema = json.load(jsonfile)
            resolver = RefResolver(
                schema_path,
                schema,
            )

            validator = Draft7Validator(schema, resolver=resolver, format_checker=None)
            instance = self.getConditions()

            validator.validate(instance)

    def validateConditions(self):
        try:
            self.validateConditionsRaw()
        except json.decoder.JSONDecodeError as e:
            showInfo(str(e))
        except jsonschema.exceptions.ValidationError as e:
            showInfo(str(e))
        else:
            showInfo('Valid Conditions.')

    def exportData(self):
        from aqt.utils import showInfo

        result = deserialize_script({
            'name': self.ui.nameLineEdit.text(),
            'version': self.ui.versionLineEdit.text(),

            'description': self.ui.descriptionTextEdit.toPlainText(),
            'enabled': self.ui.enableScriptCheckBox.isChecked(),
            'conditions': self.getConditions(),
            'code': self.ui.codeTextEdit.toPlainText(),
        })
        return result

    def importDialog(self):
        def updateAfterImport(new_script):
            self.setupUi(deserialize_script(new_script))

        dirpath = Path(f'{os.path.dirname(os.path.realpath(__file__))}', '../../json_schemas/scr.json')
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
                json.dumps(serialize_script(self.exportData()), sort_keys=True, indent=4),
                validator,
                updateAfterImport,
            )
            dial.exec_()
