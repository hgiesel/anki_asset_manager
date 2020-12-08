import json
import os

from typing import Union

from pathlib import Path
from jsonschema import RefResolver, Draft7Validator

from aqt import mw
from aqt.qt import QWidget, QLabel, Qt

from ..src.config import (
    serialize_html,
    deserialize_html,
    serialize_html_setting,
    deserialize_html_setting,
)

from ..src.config_types import ConcreteHTML, DEFAULT_CONCRETE_HTML

from .forms.html_tab_ui import Ui_HTMLTab
from .html_config import HTMLConfig

from .utils import map_truth_value_to_icon


class HTMLTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_HTMLTab()
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
        self.ui.scriptsTable.setColumnWidth(2, 110)

    def setupUi(self, modelId, setting):
        self.modelId = modelId
        self.ui.enableCheckBox.setChecked(setting.enabled),
        self.ui.minifyHtml.setChecked(setting.minify),
        self.frags = setting.fragments

        self.drawScripts()
        self.updateButtons(False)

    def drawScripts(self):
        self.ui.scriptsTable.clearContents()
        self.ui.scriptsTable.setRowCount(len(self.frags))

        headerLabels = []

        for idx, script in enumerate(self.frags):
            headerLabels.append(f"Script {idx}")
            self.setRowModFromScript(idx, script, False)

        self.ui.scriptsTable.setVerticalHeaderLabels(headerLabels)

    def setRowModFromScript(self, idx, script, isMeta: bool):
        self.setRowMod(
            idx,
            script.name,
            map_truth_value_to_icon(script.enabled),
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
            self.frags[row] = newScript
            self.drawScripts()

        a = HTMLConfig(self, self.modelId, saveScript)
        a.setupUi(self.frags[row])
        a.open()

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
        self.frags.append(DEFAULT_CONCRETE_HTML)
        self.drawScripts()

    def deleteScript(self):
        current_scr = self.frags[self.ui.scriptsTable.currentRow()]

        del self.frags[self.ui.scriptsTable.currentRow()]  # gotta delete within dict

        self.drawScripts()
        self.updateButtons(False)

    def moveDown(self):
        i = self.ui.scriptsTable.currentRow()

        if len(self.frags) != 1 and i < len(self.frags) - 1:
            self.frags[i], self.frags[i + 1] = self.frags[i + 1], self.frags[i]
            self.drawScripts()
            self.ui.scriptsTable.setCurrentCell(i + 1, 0)

    def moveUp(self):
        i = self.ui.scriptsTable.currentRow()

        if len(self.frags) != 1 and i > 0:
            self.frags[i], self.frags[i - 1] = self.frags[i - 1], self.frags[i]
            self.drawScripts()
            self.ui.scriptsTable.setCurrentCell(i - 1, 0)

    ###########

    def exportData(self):
        return deserialize_html_setting(
            self.modelId,
            {
                "enabled": self.ui.enableCheckBox.isChecked(),
                "minify": self.ui.minifyHtml.isChecked(),
                "fragments": self.frags,
            },
        )
