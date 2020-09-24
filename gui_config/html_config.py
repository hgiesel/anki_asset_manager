import os
import json

from typing import Union
from dataclasses import asdict, replace

import jsonschema
from jsonschema import validate, RefResolver, Draft7Validator
from pathlib import Path

from aqt import mw
from aqt.qt import QDialog, QWidget, QFont, Qt
from aqt.utils import askUser, restoreGeom, saveGeom, showInfo # actually needed!

from ..src.config import serialize_html, deserialize_html
from ..src.config_types import ConcreteHTML

from ..src.lib.interface import make_html_bool
from ..src.lib.registrar import get_interface

from .forms.html_config_ui import Ui_HTMLConfig

from .utils import (
    script_type_to_gui_text, script_position_to_gui_text,
    pos_to_script_type, pos_to_script_position,
)
from .highlighter import HTMLHighlighter


geom_name = 'assetManagerScriptConfig'

class HTMLConfig(QDialog):
    def __init__(self, parent, model_name, callback):
        super().__init__(parent=parent)

        self.callback = callback
        self.modelName = model_name

        self.ui = Ui_HTMLConfig()
        self.ui.setupUi(self)

        self.accepted.connect(self.onAccept)
        self.rejected.connect(self.onReject)

        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.resetButton.hide()

        self.ui.saveButton.clicked.connect(self.tryAccept)
        self.ui.saveButton.setDefault(True)

        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.validateButton.clicked.connect(self.validateConditions)

        self.ui.metaLabel.setText('')
        self.ui.enableScriptCheckBox.stateChanged.connect(self.enableChangeGui)
        self.initEditor(self.ui.codeTextEdit)

        restoreGeom(self, geom_name)

    def initEditor(self, editor):
        font = editor.document().defaultFont()
        font.setFamily('Courier New')
        font.setStyleHint(QFont.Monospace)
        font.setWeight(QFont.Medium)
        font.setFixedPitch(True)
        font.setPointSize(14)

        editor.setFont(font)

        self.highlighter = HTMLHighlighter(editor.document())

    def setupUi(self, concrete_script: ConcreteHTML):
        self.ui.nameLineEdit.setText(concrete_script.name)

        self.ui.enableScriptCheckBox.setChecked(concrete_script.enabled)

        self.ui.versionLineEdit.setText(concrete_script.version)
        self.ui.descriptionTextEdit.setPlainText(concrete_script.description)

        self.ui.labelEdit.setText(concrete_script.label)
        self.ui.conditionsTextEdit.setPlainText(json.dumps(concrete_script.conditions))

        self.ui.codeTextEdit.setPlainText(concrete_script.code)

        self.enableChangeGui()

    def reset(self):
        # only available for meta scripts
        if not askUser('Are you sure you want to reset this script? This will set it back to its default settings.'):
            return

        try:
            self.validateConditionsRaw()
        except:
            showInfo('Invalid Conditions. Please fix the conditions before resetting.')
        else:
            # this is necessary to trigger the meta hooks before resetting
            current_script = self.exportData()
            self.setupUiMeta(current_script)

            # fall back to current script if dev setup the reset hook wrong
            try:
                reset_script = self.iface.reset(self.meta.id, self.meta.storage)
                self.setupUiConcrete(reset_script)
            except:
                showInfo('Ooops, it seems like the developer responsible for this script did not setup the reset function correctly.')
                self.setupUiMeta(current_script)

            self.ui.nameLineEdit.repaint()

            self.ui.enableScriptCheckBox.repaint()

            self.ui.versionLineEdit.repaint()
            self.ui.descriptionTextEdit.repaint()

            self.ui.conditionsTextEdit.repaint()

            self.ui.codeTextEdit.repaint()

    def enableChangeGui(self):
        try:
            self.enableChange(self.ui.enableScriptCheckBox.isChecked(), self.iface.readonly)
        except AttributeError:
            self.enableChange(self.ui.enableScriptCheckBox.isChecked())

    def enableChange(self, state=True, readonly=make_html_bool()):
        self.ui.nameLineEdit.setReadOnly(not state or readonly.name)

        self.ui.versionLineEdit.setReadOnly(not state or readonly.version)
        self.ui.descriptionTextEdit.setReadOnly(not state or readonly.description)

        self.ui.labelEdit.setReadOnly(not state or readonly.label)
        self.ui.conditionsTextEdit.setReadOnly(not state or readonly.conditions)

        self.ui.codeTextEdit.setReadOnly(not state or readonly.code)

    def getConditions(self): # can throw
        return json.loads(self.ui.conditionsTextEdit.toPlainText())

    def validateConditionsRaw(self):
        dirpath  = Path(f'{os.path.dirname(os.path.realpath(__file__))}', '../json_schemas/script_cond.json')
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

    def exportData(self) -> Union[ConcreteHTML]:
        result = deserialize_html({
            'name': self.ui.nameLineEdit.text(),

            'enabled': self.ui.enableScriptCheckBox.isChecked(),

            'version': self.ui.versionLineEdit.text(),
            'description': self.ui.descriptionTextEdit.toPlainText(),

            'label': self.ui.labelEdit.text(),
            'conditions': self.getConditions(),

            'code': self.ui.codeTextEdit.toPlainText(),
        })

        return result

    def cancel(self):
        if askUser('Discard changes?'):
            self.reject()

    def tryAccept(self):
        try:
            self.validateConditionsRaw()
        except:
            showInfo('Invalid Conditions. Please correct the conditions or just set it to `[]`.')
        else:
            self.accept()

    def onAccept(self):
        saveGeom(self, geom_name)
        self.callback(self.exportData())

    def onReject(self):
        saveGeom(self, geom_name)
