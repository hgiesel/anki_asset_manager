import json
import os

from pathlib import Path
from jsonschema import RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QWidget, QLabel, Qt

from ...lib.config import deserialize_script, serialize_script, deserialize_setting, serialize_setting
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

    def setupUi(self, setting):
        self.modelName = setting.model_name
        self.scr = setting.scripts

        self.drawScripts()

        self.updateButtons(False)

    def drawScripts(self):
        self.ui.scriptsTable.clearContents()
        self.ui.scriptsTable.setRowCount(len(self.scr))

        headerLabels = []

        for idx, scr in enumerate(self.scr):
            headerLabels.append(f'Script {idx}')

            self.setRowMod(
                idx,
                scr.name,
                scr.version,
                mapTruthValueToIcon(scr.enabled),
                json.dumps(scr.conditions),
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

        a = SMScriptConfig(mw, saveScript)
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
        newScript = deserialize_script({
            'name': 'New Script',
            'description': '',
            'enabled': True,
            'conditions': [],
            'statements': [],
        })

        self.scr.append(newScript)
        self.drawScripts()

    def deleteScript(self):
        del self.scr[self.ui.scriptsTable.currentRow()]

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
            "scripts": self.scr,
        })
        return result

    def importDialog(self):
        def addAfterImport(scripts_new):
            self.setupUi(self.scr + [deserialize_script(scr) for scr in scripts_new])

        def replaceAfterImport(scripts_new):
            self.setupUi([deserialize_script(scr) for scr in scripts_new])

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
