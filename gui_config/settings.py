from aqt import QDialog, QLayout, QKeySequence

from .forms.settings_ui import Ui_Settings


class Settings(QDialog):
    def __init__(self, mw, callback):
        super().__init__(parent=mw)

        self.mw = mw

        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.cb = callback

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

    def setupUi(self, version: str, add_assets: bool, remove_cards: bool):
        self.ui.version_info.setText(f"Asset Manager v{version}")
        self.ui.add_assets.setChecked(add_assets)
        self.ui.remove_cards.setChecked(remove_cards)

    def accept(self):
        self.cb(
            self.ui.add_assets.isChecked(),
            self.ui.remove_cards.isChecked(),
        )

        super().accept()
