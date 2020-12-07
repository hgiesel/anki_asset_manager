import json
import os

from typing import Union, Tuple

from pathlib import Path
from jsonschema import RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QWidget, QLabel, Qt

from ..src.config import (
    serialize_script,
    deserialize_concrete_script,
    serialize_setting,
    deserialize_setting,
)

from ..src.config_types import ConcreteScript, MetaScript
from ..src.lib.registrar import get_interface, has_interface

from .forms.script_tab_ui import Ui_ScriptTab
from .script_config import ScriptConfig

from .utils import (
    map_truth_value_to_icon,
    script_position_to_gui_text,
)


def get_from_meta(meta_script: MetaScript) -> Tuple[ConcreteScript, Union[str, bool]]:
    iface = get_interface(meta_script.tag)
    is_loose = not has_interface(meta_script.tag)

    script = iface.getter(meta_script.id, meta_script.storage)

    label = "loose" if is_loose else True

    return (script, label)


class ScriptTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_ScriptTab()
        self.ui.setupUi(self)

        self.ui.addPushButton.clicked.connect(self.addScript)
        self.ui.deletePushButton.clicked.connect(self.deleteScript)
        self.ui.downPushButton.clicked.connect(self.moveDown)
        self.ui.upPushButton.clicked.connect(self.moveUp)

        self.ui.scriptsTable.currentCellChanged.connect(
            self.updateButtonsForCurrentCell
        )
        self.ui.scriptsTable.cellDoubleClicked.connect(self.editScript)
        self.ui.scriptsTable.setColumnWidth(1, 55)
        self.ui.scriptsTable.setColumnWidth(2, 55)

    def setupUi(self, modelId, setting):
        self.modelId = modelId
        self.ui.enableCheckBox.setChecked(setting.enabled),
        self.ui.insertStubCheckBox.setChecked(setting.insert_stub),
        self.scr = setting.scripts

        self.drawScripts()
        self.updateButtons(False)

    def drawScripts(self):
        self.ui.scriptsTable.clearContents()
        self.ui.scriptsTable.setRowCount(len(self.scr))

        headerLabels = []

        for idx, script in enumerate(self.scr):
            headerLabels.append(f"Script {idx}")
            self.setRowModFromScript(
                idx,
                *(
                    (script, False)
                    if isinstance(script, ConcreteScript)
                    else get_from_meta(script)
                ),
            )

        self.ui.scriptsTable.setVerticalHeaderLabels(headerLabels)

    def setRowModFromScript(self, idx, script, isMeta: Union[bool, str]):
        self.setRowMod(
            idx,
            script.name,
            map_truth_value_to_icon(script.enabled),
            map_truth_value_to_icon(isMeta),
            script_position_to_gui_text(script.position),
            script.label,
            json.dumps(script.conditions),
        )

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

        a = ScriptConfig(mw, self.modelId, saveScript)
        a.setupUi(self.scr[row])
        a.exec_()

    ###########

    def updateButtonsForCurrentCell(
        self, currentRow, currentColumn, previousRow, previousColumn
    ):
        self.updateButtons(currentRow != -1)

    def updateButtons(self, state=True):
        self.ui.deletePushButton.setEnabled(state)
        self.ui.downPushButton.setEnabled(state)
        self.ui.upPushButton.setEnabled(state)

    def addScript(self):
        newScript = deserialize_concrete_script(
            {
                "name": "New Script",
                "type": "js",
                "description": "",
                "enabled": True,
                "conditions": [],
                "statements": [],
            }
        )

        self.scr.append(newScript)
        self.drawScripts()

    def deleteScript(self):
        current_scr: Union[ConcreteScript, MetaScript] = self.scr[
            self.ui.scriptsTable.currentRow()
        ]

        def show_nondeletable():
            from aqt.utils import showInfo  # not to be deleted!

            showInfo(
                "This script does not allow for deletion.\n"
                "You might have to uninstall the add-on which inserted this script."
            )

        if isinstance(current_scr, ConcreteScript):
            del self.scr[self.ui.scriptsTable.currentRow()]  # gotta delete within dict
        else:
            iface = get_interface(current_scr.tag)

            if iface.deletable:
                is_deletable = iface.deletable(current_scr.id, current_scr.storage)

                if is_deletable:
                    del self.scr[
                        self.ui.scriptsTable.currentRow()
                    ]  # gotta delete within dict

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
        result = deserialize_setting(
            self.modelId,
            {
                "enabled": self.ui.enableCheckBox.isChecked(),
                "insertStub": self.ui.insertStubCheckBox.isChecked(),
                "scripts": self.scr,
            },
        )
        return result
