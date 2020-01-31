import json
import os

from typing import Union

from pathlib import Path
from jsonschema import RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QWidget, QLabel, Qt

from ...lib.config import deserialize_script, serialize_script, deserialize_setting, serialize_setting
from ...lib.types import SMConcrScript, SMMetaScript
from ...lib.registrar import get_interface

from ..sm_script_tab_ui import Ui_SMScriptTab

from .sm_setting_add_replace import SMSettingAddReplace
from .sm_script_config import SMScriptConfig

from .util import mapTruthValueToIcon

class SMScriptTab(QWidget):
    def __init__(self, main):
        super().__init__()

        self.ui = Ui_SMScriptTab()
        self.ui.setupUi(self)

        self.ui.addPushButton.clicked.connect(self.addScript)
        self.ui.deletePushButton.clicked.connect(self.deleteScript)
        self.ui.downPushButton.clicked.connect(self.moveDown)
        self.ui.upPushButton.clicked.connect(self.moveUp)
        self.ui.importButton.clicked.connect(self.importDialog)

        self.ui.scriptsTable.currentCellChanged.connect(self.updateButtonsForCurrentCell)
        self.ui.scriptsTable.cellDoubleClicked.connect(self.editScript)
        self.ui.scriptsTable.setColumnWidth(1, 75)
        self.ui.scriptsTable.setColumnWidth(2, 55)
        self.ui.scriptsTable.setColumnWidth(3, 55)

    def setupUi(self, setting):
        self.modelName = setting.model_name
        self.ui.enableCheckBox.setChecked(setting.enabled),
        self.ui.insertStubCheckBox.setChecked(setting.insert_stub),
        self.scr = setting.scripts

        self.drawScripts()

        self.updateButtons(False)

    def drawScripts(self):
        self.ui.scriptsTable.clearContents()
        self.ui.scriptsTable.setRowCount(len(self.scr))

        headerLabels = []

        for idx, scr in enumerate(self.scr):
            headerLabels.append(f'Script {idx}')

            if isinstance(scr, SMConcrScript):
                self.setRowMod(
                    idx,
                    scr.name,
                    scr.version,
                    mapTruthValueToIcon(scr.enabled),
                    mapTruthValueToIcon(False),
                    json.dumps(scr.conditions),
                )

            else:
                iface = get_interface(scr.tag)
                script = iface.getter(scr.id, scr.storage)

                self.setRowMod(
                    idx,
                    script.name,
                    script.version,
                    mapTruthValueToIcon(script.enabled),
                    mapTruthValueToIcon(True),
                    json.dumps(script.conditions),
                )

        self.ui.scriptsTable.setVerticalHeaderLabels(headerLabels)

    def setRowMod(self, row, *args):
        for i, text in enumerate(args):
            label = QLabel()
            label.setText(text)
            label.setAlignment(Qt.AlignCenter)

            self.ui.scriptsTable.setCellWidget(row, i, label)

    def editScript(self, row, column):
        def saveScript(newScript):
            self.scr[row] = newScript
            self.drawScripts()

        a = SMScriptConfig(mw, self.modelName, saveScript)
        a.setupUi(self.scr[row])
        a.exec_()

    ###########

    def updateButtonsForCurrentCell(self, currentRow, currentColumn, previousRow, previousColumn):
        self.updateButtons(currentRow != -1)

    def updateButtons(self, state=True):
        self.ui.deletePushButton.setEnabled(state)
        self.ui.downPushButton.setEnabled(state)
        self.ui.upPushButton.setEnabled(state)

    def addScript(self):
        newScript = deserialize_script(self.modelName, {
            'name': 'New Script',
            'description': '',
            'enabled': True,
            'conditions': [],
            'statements': [],
        })

        self.scr.append(newScript)
        self.drawScripts()

    def deleteScript(self):
        current_scr: Union[SMConcrScript, SMMetaScript] = self.scr[self.ui.scriptsTable.currentRow()]

        def show_nondeletable():
            from aqt.utils import showInfo # not to be deleted!
            showInfo(
                'This script does not allow for deletion.\n'
                'You might have to uninstall the add-on which inserted this script.'
            )

        if isinstance(current_scr, SMConcrScript):
            del self.scr[self.ui.scriptsTable.currentRow()] # gotta delete within dict
        else:
            iface = get_interface(current_scr.tag)

            if iface.deletable:
                is_deletable = iface.deletable(current_scr.id, current_scr.storage)

                if is_deletable:
                    del self.scr[self.ui.scriptsTable.currentRow()] # gotta delete within dict

                else:
                    show_nondeletable()

            else:
                show_nondeletable()

        self.drawScripts()
        self.updateButtons(False)

    def moveDown(self):
        i = self.ui.scriptsTable.currentRow()

        if len(self.scr) != 1 and i < len(self.scr) - 1:
            self.scr[i], self.scr[i + 1] = self.scr[i + 1], self.scr[i]
            self.drawScripts()
            self.ui.scriptsTable.setCurrentCell(i + 1, 0)

    def moveUp(self):
        i = self.ui.scriptsTable.currentRow()

        if len(self.scr) != 1 and i > 0:
            self.scr[i], self.scr[i - 1] = self.scr[i - 1], self.scr[i]
            self.drawScripts()
            self.ui.scriptsTable.setCurrentCell(i - 1, 0)

    ###########

    def exportData(self):
        result = deserialize_setting(self.modelName, {
            "enabled": self.ui.enableCheckBox.isChecked(),
            "insertStub": self.ui.insertStubCheckBox.isChecked(),
            "scripts": self.scr,
        })
        return result

    def importDialog(self):
        def addAfterImport(scripts_new):
            self.setupUi(self.scr + [deserialize_script(self.modelName, scr) for scr in scripts_new])

        def replaceAfterImport(scripts_new):
            self.setupUi([deserialize_script(self.modelName, scr) for scr in scripts_new])

        dirpath = Path(f'{os.path.dirname(os.path.realpath(__file__))}', '../../json_schemas/scripts.json')
        schema_path = dirpath.absolute().as_uri()

        with dirpath.open('r') as jsonfile:
            schema = json.load(jsonfile)
            resolver = RefResolver(
                schema_path,
                schema,
            )

            validator = Draft7Validator(schema, resolver=resolver, format_checker=None)

            dial = SMSettingAddReplace(mw)
            dial.setupUi(
                json.dumps([serialize_script(scr) for scr in self.scr], sort_keys=True, indent=4),
                validator,
                addAfterImport,
                replaceAfterImport,
            )
            dial.exec_()
