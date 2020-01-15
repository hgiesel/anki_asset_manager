import os
import json

from typing import Union
from dataclasses import asdict, replace

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

from ...lib.types import SMConcrScript, SMMetaScript, SMScriptStorage, SMScriptBool
from ...lib.interface import make_script_bool
from ...lib.registrar import get_interface

def fix_storage(store: SMScriptStorage, script: SMConcrScript, to_store: SMScriptBool) -> SMScriptStorage:
    def filter_store(tost):
        return [
            storekey[0]
            for storekey
            in asdict(tost).items() if storekey[1]
        ]

    filtered_store = filter_store(to_store)
    the_dict = dict([
        (key, getattr(script, key))
        for key
        in filtered_store
    ])

    return replace(store, **the_dict)

class SMScriptConfig(QDialog):
    def __init__(self, parent, model_name, callback):
        super().__init__(parent=parent)

        self.callback = callback
        self.modelName = model_name

        self.ui = Ui_SMScriptConfig()
        self.ui.setupUi(self)

        self.accepted.connect(self.onAccept)
        self.rejected.connect(self.onReject)

        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.resetButton.hide()

        self.ui.saveButton.clicked.connect(self.tryAccept)
        self.ui.saveButton.setDefault(True)

        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.validateButton.clicked.connect(self.validateConditions)
        self.ui.importButton.clicked.connect(self.importDialog)

        self.ui.metaLabel.setText('')
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
        if isinstance(script, SMConcrScript):
            self.setupUiConcr(script)
        else:
            self.setupUiMeta(script)

    def setupUiConcr(self, concr_script):
        self.ui.nameLineEdit.setText(concr_script.name)
        self.ui.versionLineEdit.setText(concr_script.version)
        self.ui.descriptionTextEdit.setPlainText(concr_script.description)
        self.ui.enableScriptCheckBox.setChecked(concr_script.enabled)
        self.ui.conditionsTextEdit.setPlainText(json.dumps(concr_script.conditions))
        self.ui.codeTextEdit.setPlainText(concr_script.code)

        self.enableChangeGui()

    def setupUiMeta(self, meta_script):
        self.meta = meta_script
        self.iface = get_interface(meta_script.tag)

        self.setupUiConcr(self.iface.getter(self.meta.id, self.meta.storage))
        self.ui.metaLabel.setText(self.iface.label(self.meta.id, self.meta.storage))

        if self.iface.reset:
            self.ui.resetButton.show()

    def reset(self):
        # only available for meta scripts

        try:
            self.validateConditionsRaw()
        except:
            showInfo('Invalid Conditions. Please fix the conditions before resetting.')
        else:
            self.setupUi(self.exportData())
            self.setupUiConcr(self.iface.reset(self.meta.id, self.meta.storage))

            self.ui.nameLineEdit.repaint()
            self.ui.versionLineEdit.repaint()
            self.ui.descriptionTextEdit.repaint()
            self.ui.enableScriptCheckBox.repaint()
            self.ui.conditionsTextEdit.repaint()
            self.ui.codeTextEdit.repaint()

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
        try:
            self.enableChange(self.ui.enableScriptCheckBox.isChecked(), self.iface.readonly)
        except AttributeError:
            self.enableChange(self.ui.enableScriptCheckBox.isChecked())

    def enableChange(self, state=True, readonly=make_script_bool()):
        def get_state(newstate, readonlystate):
            return newstate or readonlystate

        self.ui.conditionsTextEdit.setReadOnly(get_state(not state, readonly.conditions))
        self.ui.codeTextEdit.setReadOnly(get_state(not state, readonly.code))
        self.ui.descriptionTextEdit.setReadOnly(get_state(not state, readonly.description))
        self.ui.nameLineEdit.setReadOnly(get_state(not state, readonly.name))
        self.ui.versionLineEdit.setReadOnly(get_state(not state, readonly.version))

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

    def exportData(self) -> Union[SMConcrScript, SMMetaScript]:
        result = deserialize_script(self.modelName, {
            'name': self.ui.nameLineEdit.text(),
            'version': self.ui.versionLineEdit.text(),

            'description': self.ui.descriptionTextEdit.toPlainText(),
            'enabled': self.ui.enableScriptCheckBox.isChecked(),
            'conditions': self.getConditions(),
            'code': self.ui.codeTextEdit.toPlainText(),
        })

        try:
            user_result = self.iface.setter(self.meta.id, result)

            if isinstance(user_result, SMConcrScript):
                return replace(
                    self.meta,
                    storage = fix_storage(self.meta.storage, user_result, self.iface.store),
                )

            elif user_result:
                return replace(
                    self.meta,
                    storage = fix_storage(self.meta.storage, result, self.iface.store),
                )

            else:
                return self.meta

        except AttributeError:
            return result

    def importDialog(self):
        def updateAfterImport(new_script):
            self.setupUi(deserialize_script(self.modelName, new_script))

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
